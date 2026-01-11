# ask.zenon.wtf Implementation Roadmap

## Project Overview

Adapt the kaine-ai bot to create ask.zenon.wtf - an AI-powered Q&A interface for Zenon Network design research. The knowledge base will be the 98 Markdown documents in `/context/`.

## Status

- [x] Phase 1: Repository Setup
- [x] Phase 2: Data Layer Adaptation
- [x] Phase 3: AI Personality & Prompts
- [x] Phase 4: Web Interface Updates
- [x] Phase 5: Configuration
- [ ] Phase 6: Deployment

## Source

- **Based on:** [kaine-ai](https://github.com/0x3639/kaine-ai)
- **Domain:** ask.zenon.wtf
- **Tech stack:** Python 3.11, FastAPI, OpenAI (embeddings + GPT-4o), Redis, Docker

---

## Phase 1: Repository Setup ✓

### 1.1 Files copied from kaine-ai:
```
kaine_ai.py → zenon_ai.py
web_app.py
static/
data/zenon_personality.md
requirements.txt, requirements-web.txt, requirements-prod.txt
Dockerfile, docker-compose.yml, docker-compose.prod.yml
Caddyfile, deploy.sh, .env.example
```

---

## Phase 2: Data Layer Adaptation

### 2.1 Create Markdown loader
**File:** `zenon_ai.py`

Replace JSON loader with Markdown loader that:
- Reads all `.md` files from `/context/`
- Extracts content and metadata (title from first heading, filename)
- Transforms to compatible format for chunking

### 2.2 Update chunking logic
- Current: 512-token chunks with 50-token overlap
- Adapt for Markdown: preserve section boundaries where possible
- Include document title/filename as metadata for citations

### 2.3 Modify citation format
- Change from Telegram URLs to document references
- Format: `[document_name.md]` or section headers

---

## Phase 3: AI Personality & Prompts

### 3.1 Create Zenon personality file
**File:** `data/zenon_personality.md`

Replace Kaine personality with Zenon expert personality:
- Technical accuracy for blockchain/distributed systems
- Reference greenpaper terminology (bounded verification, zApps, CEV, etc.)
- Distinguish between core team papers (normative) vs community papers (non-normative)
- Guide users to relevant documents

### 3.2 Update system prompts in `zenon_ai.py`
- Modify `answer_question()` method prompts
- Update speculation mode behavior for research context
- Adjust relevance thresholds for technical documentation

---

## Phase 4: Web Interface Updates

### 4.1 Branding changes
**Files:** `static/index.html`, `static/style.css`

- Update title: "Ask Zenon"
- Update placeholder text: "Ask about Zenon Network design..."
- Update footer/attribution

### 4.2 UI copy updates
- Welcome message explaining the knowledge base
- Example questions relevant to Zenon
- Attribution to TminusZ/zenon-developer-commons

---

## Phase 5: Configuration

### 5.1 Environment variables
**File:** `.env.example`

```
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-large
CHAT_MODEL=gpt-4o
DEFAULT_CONTEXT_POSTS=15
CHUNK_SIZE=512
CHUNK_OVERLAP=50
PERSONALITY_FILE=data/zenon_personality.md
ENVIRONMENT=production
REDIS_URL=redis://redis:6379/0
```

### 5.2 Update file paths
- Cache file: `zenon_ai_cache.pkl`
- Data directory: `/context/` instead of `/data/`

---

## Phase 6: Deployment

### 6.1 Docker configuration
- Update `Dockerfile` with zenon_ai.py
- Modify `docker-compose.yml` service names
- Update `Caddyfile` for ask.zenon.wtf domain

### 6.2 DNS & SSL
- Point ask.zenon.wtf to Caddy server
- Let's Encrypt SSL via Caddy automatic HTTPS

---

## Critical Files to Modify

| File | Changes Required |
|------|-----------------|
| `zenon_ai.py` | Markdown loader, citation format, prompts |
| `web_app.py` | Branding, data paths, import zenon_ai |
| `data/zenon_personality.md` | New personality |
| `static/index.html` | UI branding |
| `.env.example` | Configuration values |
| `docker-compose.yml` | Service names, volumes |
| `Caddyfile` | Domain configuration |

---

## Verification Plan

1. **Local testing:**
   - Run `python zenon_ai.py` to verify Markdown loading and embedding generation
   - Test with sample questions about bounded verification, zApps, etc.

2. **Web app testing:**
   - Run `docker-compose up`
   - Verify `/api/health` endpoint
   - Test Q&A through web interface

3. **Citation verification:**
   - Ensure responses cite correct document names
   - Verify links/references work

4. **Production deployment:**
   - Deploy to server
   - Verify SSL and domain
   - Test rate limiting
