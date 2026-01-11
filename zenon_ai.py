#!/usr/bin/env python3
"""
Zenon AI - Research Documentation Q&A Tool using OpenAI API
This tool answers questions about Zenon Network of Momentum design research.

Features:
- Document chunking for granular embeddings
- Hybrid search (semantic + keyword via TF-IDF)
- Optional context compression (disabled by default for cost efficiency)
- Configurable compression threshold via environment variables
- Cost tracking and estimation
- Diversity reranking for better document selection

Based on kaine-ai (https://github.com/0x3639/kaine-ai)
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
from openai import OpenAI
import tiktoken
import pickle
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict
from math import log

# Load environment variables from .env file
load_dotenv()

class ZenonQA:
    def __init__(self, context_dir: str = "context", api_key: str = None):
        """
        Initialize the Zenon Q&A tool

        Args:
            context_dir: Path to directory containing Markdown documentation files
            api_key: OpenAI API key (if not provided, will use OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable or .env file")

        self.client = OpenAI(api_key=self.api_key)
        self.context_dir = context_dir
        self.documents = []  # Original documents
        self.chunks = []  # List of chunks with metadata
        self.embeddings = []

        # Ensure cache directory exists
        cache_dir = Path('cache')
        cache_dir.mkdir(exist_ok=True)

        # Cache files stored in cache/ directory
        self.embeddings_file = cache_dir / 'zenon_embeddings.pkl'
        self.tfidf_file = cache_dir / 'zenon_tfidf.pkl'
        self.chunks_file = cache_dir / 'zenon_chunks.pkl'

        # Cost tracking
        self.total_cost = 0.0
        self.enable_cost_tracking = os.getenv('ENABLE_COST_TRACKING', 'false').lower() == 'true'

        # Load model configurations from environment
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-large')
        self.chat_model = os.getenv('CHAT_MODEL', 'gpt-4o')
        self.default_context_docs = int(os.getenv('DEFAULT_CONTEXT_POSTS', '15'))
        self.chunk_size = int(os.getenv('CHUNK_SIZE', '512'))  # Tokens per chunk
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '50'))

        # Compression settings (disabled by default for cost efficiency)
        self.enable_compression = os.getenv('ENABLE_COMPRESSION', 'false').lower() == 'true'
        self.compression_threshold = int(os.getenv('COMPRESSION_THRESHOLD', '100000'))

        # Diversity reranking
        self.enable_diversity = os.getenv('ENABLE_DIVERSITY', 'true').lower() == 'true'

        # Personality configuration
        self.personality_file = os.getenv('ZENON_PERSONALITY_FILE', 'data/zenon_personality.md')
        self.speculation_threshold = float(os.getenv('SPECULATION_THRESHOLD', '0.5'))
        self.personality_context = self._load_personality()

        # Tokenizer for chunking
        self.tokenizer = tiktoken.encoding_for_model(self.embedding_model)

        # Load the documents
        self.load_documents()

        # Load or create chunks, embeddings, and TF-IDF
        self.load_or_create_chunks()
        self.load_or_create_embeddings()
        self.load_or_create_tfidf()
    
    def load_documents(self):
        """Load Markdown documents from context directory"""
        print(f"Loading documents from {self.context_dir}/...")
        self.documents = []

        context_path = Path(self.context_dir)
        if not context_path.exists():
            raise ValueError(f"Context directory not found: {self.context_dir}")

        for md_file in sorted(context_path.glob("*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract title from first heading or use filename
                title = md_file.stem
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break

                # Determine document type based on filename patterns
                filename = md_file.name.lower()
                if 'core_team' in filename or 'lightpaper' in filename or 'whitepaper' in filename:
                    doc_type = 'core'  # Normative
                elif 'greenpaper' in filename:
                    doc_type = 'greenpaper'  # Community research
                elif 'spv' in filename or 'bitcoin' in filename:
                    doc_type = 'bitcoin-spv'
                elif 'architecture' in filename or 'node' in filename:
                    doc_type = 'architecture'
                else:
                    doc_type = 'research'

                self.documents.append({
                    'filename': md_file.name,
                    'title': title,
                    'content': content,
                    'doc_type': doc_type,
                    'path': str(md_file)
                })
            except Exception as e:
                print(f"Warning: Could not load {md_file}: {e}")

        print(f"Loaded {len(self.documents)} documents")

    def _load_personality(self) -> str:
        """Load Zenon expert personality context from file"""
        if os.path.exists(self.personality_file):
            try:
                with open(self.personality_file, 'r', encoding='utf-8') as f:
                    personality = f.read()
                print(f"Loaded personality context from {self.personality_file}")
                return personality
            except Exception as e:
                print(f"Warning: Could not load personality file: {e}")
                return ""
        else:
            print(f"Note: Personality file not found at {self.personality_file}, using generic mode")
            return ""

    def _create_searchable_text(self, doc: Dict) -> str:
        """Create a searchable text representation of a document (normalized)"""
        parts = []

        # Add document metadata
        parts.append(f"Document: {doc.get('filename', 'Unknown')}")
        parts.append(f"Title: {doc.get('title', 'Unknown')}")
        parts.append(f"Type: {doc.get('doc_type', 'research')}")

        # Add content (normalized for search)
        if doc.get('content'):
            parts.append(f"Content: {doc['content'].lower()}")

        return "\n".join(parts).strip()
    
    def load_or_create_chunks(self):
        """Create or load chunks from documents for granular embeddings"""
        if os.path.exists(self.chunks_file):
            print(f"Loading existing chunks from {self.chunks_file}...")
            with open(self.chunks_file, 'rb') as f:
                self.chunks = pickle.load(f)
            print(f"Loaded {len(self.chunks)} chunks")
        else:
            print("Creating chunks from documents...")
            self.create_chunks()
            with open(self.chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            print("Chunks saved")

    def create_chunks(self):
        """Split documents into chunks for better granularity"""
        self.chunks = []
        for doc_idx, doc in enumerate(self.documents):
            text = self._create_searchable_text(doc)
            tokens = self.tokenizer.encode(text)

            if len(tokens) <= self.chunk_size:
                self.chunks.append({
                    'doc_idx': doc_idx,
                    'chunk_idx': 0,
                    'text': text,
                    'metadata': {
                        'filename': doc.get('filename'),
                        'title': doc.get('title'),
                        'doc_type': doc.get('doc_type')
                    }
                })
            else:
                # Split with overlap
                chunk_num = 0
                for start in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
                    end = start + self.chunk_size
                    chunk_tokens = tokens[start:end]
                    chunk_text = self.tokenizer.decode(chunk_tokens)
                    self.chunks.append({
                        'doc_idx': doc_idx,
                        'chunk_idx': chunk_num,
                        'text': chunk_text,
                        'metadata': {
                            'filename': doc.get('filename'),
                            'title': doc.get('title'),
                            'doc_type': doc.get('doc_type')
                        }
                    })
                    chunk_num += 1
                    if end >= len(tokens):
                        break
        print(f"Created {len(self.chunks)} chunks from {len(self.documents)} documents")
    
    def load_or_create_embeddings(self):
        """Load existing embeddings or create new ones for chunks"""
        if os.path.exists(self.embeddings_file):
            print(f"Loading existing embeddings from {self.embeddings_file}...")
            with open(self.embeddings_file, 'rb') as f:
                self.embeddings = pickle.load(f)
            print(f"Loaded {len(self.embeddings)} embeddings")
        else:
            print("Creating embeddings for chunks (this may take a while)...")
            self.create_embeddings()
            self.save_embeddings()
    
    def create_embeddings(self):
        """Create embeddings for all chunks using OpenAI API"""
        self.embeddings = []
        batch_size = 100
        
        for i in range(0, len(self.chunks), batch_size):
            batch = self.chunks[i:i+batch_size]
            texts = [chunk['text'] for chunk in batch]
            
            print(f"Processing batch {i//batch_size + 1}/{(len(self.chunks)-1)//batch_size + 1}...")
            
            try:
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=texts
                )
                for embedding in response.data:
                    vec = np.array(embedding.embedding)
                    vec /= np.linalg.norm(vec) if np.linalg.norm(vec) > 0 else 1  # Normalize
                    self.embeddings.append(vec)
            except Exception as e:
                print(f"Error creating embeddings: {e}")
                for _ in batch:
                    self.embeddings.append(np.zeros(3072))  # Size for text-embedding-3-large
        
        print(f"Created {len(self.embeddings)} embeddings")
    
    def save_embeddings(self):
        """Save embeddings to file"""
        print(f"Saving embeddings to {self.embeddings_file}...")
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print("Embeddings saved")

    def track_cost(self, input_tokens: int, output_tokens: int, model: str):
        """Track API costs"""
        if not self.enable_cost_tracking:
            return

        # Pricing as of Jan 2025 (per 1M tokens)
        pricing = {
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4-turbo-preview': {'input': 10.00, 'output': 30.00},
            'text-embedding-3-large': {'input': 0.13, 'output': 0.0},
            'text-embedding-3-small': {'input': 0.02, 'output': 0.0},
        }

        if model in pricing:
            cost = (input_tokens / 1_000_000 * pricing[model]['input'] +
                   output_tokens / 1_000_000 * pricing[model]['output'])
            self.total_cost += cost
            if self.enable_cost_tracking:
                print(f"[Cost] {model}: ${cost:.4f} (Total: ${self.total_cost:.4f})")
    
    def load_or_create_tfidf(self):
        """Load or create TF-IDF vectors for keyword search"""
        if os.path.exists(self.tfidf_file):
            print(f"Loading TF-IDF from {self.tfidf_file}...")
            with open(self.tfidf_file, 'rb') as f:
                self.term_to_id, self.idf, self.chunk_tfs = pickle.load(f)
            print("Loaded TF-IDF")
        else:
            print("Creating TF-IDF for hybrid search...")
            self.create_tfidf()
            with open(self.tfidf_file, 'wb') as f:
                pickle.dump((self.term_to_id, self.idf, self.chunk_tfs), f)
            print("TF-IDF saved")
    
    def create_tfidf(self):
        """Simple TF-IDF implementation using numpy"""
        # Build vocabulary
        all_terms = set()
        for chunk in self.chunks:
            terms = chunk['text'].lower().split()  # Simple tokenization
            all_terms.update(terms)
        self.term_to_id = {term: idx for idx, term in enumerate(sorted(all_terms))}
        vocab_size = len(self.term_to_id)
        
        # Document frequency
        df = np.zeros(vocab_size)
        for chunk in self.chunks:
            terms = set(chunk['text'].lower().split())
            for term in terms:
                df[self.term_to_id[term]] += 1
        
        # IDF
        self.idf = np.log(len(self.chunks) / (df + 1))  # Smoothing
        
        # TF per chunk
        self.chunk_tfs = []
        for chunk in self.chunks:
            tf = np.zeros(vocab_size)
            terms = chunk['text'].lower().split()
            for term in terms:
                tid = self.term_to_id.get(term)
                if tid is not None:
                    tf[tid] += 1
            tf = tf / (len(terms) + 1)  # Normalized TF
            self.chunk_tfs.append(tf)
    
    def compute_tfidf_scores(self, query_terms: List[str]) -> List[float]:
        """Compute TF-IDF scores for a query"""
        query_tf = np.zeros(len(self.term_to_id))
        for term in query_terms:
            tid = self.term_to_id.get(term)
            if tid is not None:
                query_tf[tid] += 1
        query_tf /= len(query_terms) + 1
        
        scores = []
        for chunk_tf in self.chunk_tfs:
            score = np.dot(query_tf * self.idf, chunk_tf * self.idf)
            scores.append(score)
        return scores
    
    def find_relevant_chunks(self, query: str, top_k: int = 30, semantic_weight: float = 0.7) -> List[Dict]:
        """
        Hybrid search: semantic + keyword
        Returns top chunks after fusion and optional diversity re-ranking
        """
        # Query embedding
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=[query.lower()]  # Normalize
            )
            query_embedding = np.array(response.data[0].embedding)
            query_embedding /= np.linalg.norm(query_embedding)

            # Track cost
            query_tokens = len(self.tokenizer.encode(query))
            self.track_cost(query_tokens, 0, self.embedding_model)
        except Exception as e:
            print(f"Error creating query embedding: {e}")
            return []

        # Semantic similarities
        semantic_sim = []
        for emb in self.embeddings:
            sim = np.dot(query_embedding, emb)
            semantic_sim.append(sim)

        # Keyword scores (TF-IDF)
        query_terms = query.lower().split()
        tfidf_scores = self.compute_tfidf_scores(query_terms)

        # Fuse scores
        fused_scores = []
        for i in range(len(self.chunks)):
            score = semantic_weight * semantic_sim[i] + (1 - semantic_weight) * tfidf_scores[i]
            fused_scores.append((i, score))

        # Sort and get top_k
        fused_scores.sort(key=lambda x: x[1], reverse=True)

        # Diversity re-ranking if enabled
        if self.enable_diversity:
            relevant_chunks = self._diversity_rerank(fused_scores, top_k)
        else:
            top_indices = [idx for idx, _ in fused_scores[:top_k]]
            relevant_chunks = []
            for idx in top_indices:
                chunk = self.chunks[idx].copy()
                chunk['relevance_score'] = dict(fused_scores)[idx]
                relevant_chunks.append(chunk)

        return relevant_chunks

    def _diversity_rerank(self, scored_chunks: List[tuple], top_k: int) -> List[Dict]:
        """
        Re-rank chunks to promote diversity (avoid too many chunks from same document)
        """
        selected = []
        doc_counts = defaultdict(int)
        max_per_doc = 3  # Maximum chunks from same document

        for idx, score in scored_chunks:
            doc_idx = self.chunks[idx]['doc_idx']

            # Skip if we already have too many from this document
            if doc_counts[doc_idx] >= max_per_doc:
                continue

            chunk = self.chunks[idx].copy()
            chunk['relevance_score'] = score
            selected.append(chunk)
            doc_counts[doc_idx] += 1

            if len(selected) >= top_k:
                break

        return selected
    
    def compress_context(self, chunks: List[Dict], query: str) -> str:
        """Compress chunks using OpenAI to summarize for more context (expensive!)"""
        compressed_parts = []
        print(f"[Compression] Compressing {len(chunks)} chunks (this will cost ~${len(chunks) * 0.007:.3f})...")

        for i, chunk in enumerate(chunks):
            prompt = f"Summarize this text concisely, focusing on aspects relevant to: '{query}'\n\nText: {chunk['text'][:2000]}"
            try:
                response = self.client.chat.completions.create(
                    model=self.chat_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=150
                )
                summary = response.choices[0].message.content

                # Track cost
                input_tokens = len(self.tokenizer.encode(prompt))
                output_tokens = len(self.tokenizer.encode(summary))
                self.track_cost(input_tokens, output_tokens, self.chat_model)

                compressed_parts.append(summary)
                if (i + 1) % 10 == 0:
                    print(f"[Compression] Processed {i + 1}/{len(chunks)} chunks...")
            except Exception as e:
                print(f"[Warning] Compression failed for chunk {i}: {e}")
                summary = chunk['text'][:500]  # Fallback
                compressed_parts.append(summary)

        return "\n\n".join(compressed_parts)
    
    def build_context(self, chunks: List[Dict], query: str) -> str:
        """Build context from chunks with optional compression"""
        # Group chunks by doc_idx to reconstruct
        doc_groups = defaultdict(list)
        for chunk in chunks:
            doc_groups[chunk['doc_idx']].append(chunk)

        context_parts = []
        for doc_idx, group in doc_groups.items():
            metadata = group[0]['metadata']
            combined_text = " ".join(c['text'] for c in group)  # Recombine for coherence
            context_parts.append(f"Document: {metadata.get('filename', 'Unknown')}")
            context_parts.append(f"Title: {metadata.get('title', 'Unknown')}")
            context_parts.append(f"Type: {metadata.get('doc_type', 'research')}")
            context_parts.append(f"Content: {combined_text[:2000]}...")  # Initial truncate
            context_parts.append("")

        full_context = "\n".join(context_parts)
        context_tokens = len(self.tokenizer.encode(full_context))

        # Compress only if enabled AND exceeds threshold
        if self.enable_compression and context_tokens > self.compression_threshold:
            print(f"[Context] {context_tokens} tokens exceeds threshold ({self.compression_threshold}), compressing...")
            full_context = self.compress_context(chunks, query)
        else:
            if context_tokens > self.compression_threshold:
                print(f"[Context] {context_tokens} tokens exceeds threshold, but compression is disabled")
            else:
                print(f"[Context] Using {context_tokens} tokens (under threshold: {self.compression_threshold})")

        return full_context
    
    def answer_question(self, question: str, context_docs: int = None, return_sources: bool = False):
        """
        Answer a question about Zenon Network design research

        Args:
            question: The question to answer
            context_docs: Number of context documents to use
            return_sources: If True, return dict with answer and sources. If False, return just answer string.

        Returns:
            If return_sources=False: str (answer text)
            If return_sources=True: dict with keys 'answer' (str) and 'sources' (list of dicts)
        """
        if context_docs is None:
            context_docs = self.default_context_docs

        # Find relevant chunks (larger top_k for hybrid)
        relevant_chunks = self.find_relevant_chunks(question, top_k=context_docs * 2)  # Oversample

        if not relevant_chunks:
            answer = "I couldn't find any relevant documentation to answer your question."
            if return_sources:
                return {"answer": answer, "sources": []}
            return answer

        # Build compressed context
        context = self.build_context(relevant_chunks, question)

        # Calculate average relevance score to determine if we're speculating
        avg_relevance = sum(chunk.get('relevance_score', 0) for chunk in relevant_chunks) / len(relevant_chunks)
        is_speculation = avg_relevance < self.speculation_threshold

        # Create the prompt with Zenon expert personality
        if self.personality_context:
            system_prompt = f"""You are an expert on Zenon Network of Momentum (NoM) design and architecture, answering questions based on research documentation.

PERSONALITY & COMMUNICATION STYLE:
{self.personality_context}

RESPONSE INSTRUCTIONS:
1. When documentation directly answers the question (high relevance):
   - Answer based on the documents provided in the context
   - ALWAYS cite sources using the EXACT format specified below
   - Be technically accurate and precise

2. When speculating (low relevance or no direct answer in documents):
   - Clearly indicate when you're inferring from related concepts
   - Lead with phrases like "Based on the architectural principles described..."
   - End with: "*Note: This response is inferred from related documentation rather than a direct statement in the research.*"

3. CITATION FORMAT (MUST FOLLOW EXACTLY):
   - Format EVERY citation as: [document_filename.md]
   - Example: [ZENON_GREENPAPER.md], [architecture-overview.md]
   - Place citations inline after mentioning information from that document
   - If citing multiple documents, list each separately

4. DOCUMENT TYPES:
   - Core team papers (normative): Lightpaper, Whitepaper
   - Greenpaper series (community-authored, non-normative): Research proposals
   - Architecture docs: System design specifications
   - Research docs: Exploratory analysis"""
        else:
            # Fallback to generic mode if no personality file
            system_prompt = """You are an expert assistant analyzing Zenon Network research documentation.
            Based on the provided context, answer the user's question accurately and concisely.
            If the answer cannot be found in the context, say so.

            CITATION FORMAT (MUST FOLLOW EXACTLY):
            - Format EVERY citation as: [document_filename.md]
            - Example: [ZENON_GREENPAPER.md], [architecture-overview.md]
            - Place citations inline after mentioning information from that document
            - Be clear about which document each piece of information comes from"""

        user_prompt = f"""Context (relevant Zenon research documentation):
{context}

Question: {question}

{"[LOW RELEVANCE - Consider inference based on architectural principles]" if is_speculation else "[HIGH RELEVANCE - Answer based on documentation with citations]"}

Please provide a clear, technically accurate answer."""

        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000  # Increased for more detailed answers
            )

            # Track cost
            input_tokens = len(self.tokenizer.encode(system_prompt + user_prompt))
            output_tokens = len(self.tokenizer.encode(response.choices[0].message.content))
            self.track_cost(input_tokens, output_tokens, self.chat_model)

            answer = response.choices[0].message.content

            # If sources are requested, extract and format them
            if return_sources:
                sources = self._extract_sources_from_chunks(relevant_chunks)
                return {"answer": answer, "sources": sources}

            return answer
        except Exception as e:
            error_msg = f"Error generating answer: {e}"
            if return_sources:
                return {"answer": error_msg, "sources": []}
            return error_msg

    def _extract_sources_from_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Extract source information from chunks, grouped by document to avoid duplicates
        """
        # Group by doc_idx to avoid duplicate sources from same document
        seen_docs = set()
        sources = []

        for chunk in chunks:
            doc_idx = chunk['doc_idx']
            if doc_idx in seen_docs:
                continue
            seen_docs.add(doc_idx)

            metadata = chunk['metadata']

            source = {
                'filename': metadata.get('filename', 'Unknown'),
                'title': metadata.get('title', 'Unknown'),
                'doc_type': metadata.get('doc_type', 'research'),
                'relevance_score': round(chunk.get('relevance_score', 0), 3)
            }
            sources.append(source)

        # Sort by relevance score
        sources.sort(key=lambda x: x['relevance_score'], reverse=True)

        return sources
    
    def interactive_chat(self):
        """Run an interactive chat session"""
        print("\n" + "="*60)
        print("Zenon AI - Research Documentation Q&A Tool")
        print("="*60)
        print(f"Loaded {len(self.documents)} documents, {len(self.chunks)} chunks from {self.context_dir}/")
        print("\nConfiguration:")
        print(f"  - Embedding Model: {self.embedding_model}")
        print(f"  - Chat Model: {self.chat_model}")
        print(f"  - Default Context Docs: {self.default_context_docs}")
        print(f"  - Compression: {'Enabled' if self.enable_compression else 'Disabled'} (threshold: {self.compression_threshold:,} tokens)")
        print(f"  - Diversity Re-ranking: {'Enabled' if self.enable_diversity else 'Disabled'}")
        print(f"  - Cost Tracking: {'Enabled' if self.enable_cost_tracking else 'Disabled'}")
        print("\nYou can ask questions about Zenon Network design. Type 'quit' to exit.")
        print("Type 'stats' to see statistics about the documentation.")
        print("="*60 + "\n")

        while True:
            question = input("\n🤔 Your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if question.lower() == 'stats':
                self.show_statistics()
                continue

            if not question:
                print("Please enter a question.")
                continue

            print("\n🔍 Searching for relevant documentation (hybrid mode)...")
            answer = self.answer_question(question)

            print("\n💡 Answer:")
            print("-" * 40)
            print(answer)
            print("-" * 40)

    def show_statistics(self):
        """Show statistics about the loaded documents"""
        print("\n📊 Statistics:")
        print("-" * 40)
        print(f"Total documents: {len(self.documents)}")
        print(f"Total chunks: {len(self.chunks)}")

        # Count by document type
        types = {}
        for doc in self.documents:
            doc_type = doc.get('doc_type', 'unknown')
            types[doc_type] = types.get(doc_type, 0) + 1

        print("\nDocument types:")
        for doc_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {doc_type}: {count}")

        # List core documents
        core_docs = [d['filename'] for d in self.documents if d.get('doc_type') == 'core']
        if core_docs:
            print("\nCore team papers (normative):")
            for doc in core_docs:
                print(f"  - {doc}")

        # List greenpaper series
        greenpaper_docs = [d['filename'] for d in self.documents if d.get('doc_type') == 'greenpaper']
        if greenpaper_docs:
            print(f"\nGreenpaper series: {len(greenpaper_docs)} documents")

        print("-" * 40)


def main():
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key not found!")
        print("Please set your API key in the .env file or using:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nTo use .env file, create a file named '.env' with:")
        print("  OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)

    # Check for context directory argument or use default
    if len(sys.argv) > 1:
        context_dir = sys.argv[1]
    else:
        context_dir = 'context'

    # Check if directory exists
    if not os.path.exists(context_dir):
        print(f"Error: Context directory '{context_dir}' not found!")
        print("\nUsage: python zenon_ai.py [context_directory]")
        print("Example: python zenon_ai.py context")
        print("\nMake sure your Markdown documentation files are in the 'context/' directory.")
        sys.exit(1)

    try:
        # Create Q&A tool
        qa_tool = ZenonQA(context_dir, api_key)

        # Start interactive chat
        qa_tool.interactive_chat()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()