# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository powers **ask.zenon.wtf** - an AI-powered Q&A interface for Zenon Network of Momentum design research. It uses OpenAI embeddings and GPT-4o to answer questions about the research documentation.

## Tech Stack

- **Backend:** Python 3.11, FastAPI, OpenAI API
- **Frontend:** Static HTML/CSS/JS (ChatGPT-style interface)
- **Infrastructure:** Docker, Redis (caching/rate limiting), Caddy (reverse proxy)
- **Based on:** [kaine-ai](https://github.com/0x3639/kaine-ai)

## Project Structure

```
context/          # Zenon research documentation (98 Markdown files)
data/             # Personality configuration
static/           # Frontend assets (HTML, CSS, JS)
zenon_ai.py       # Core Q&A engine (embedding, search, answer generation)
web_app.py        # FastAPI web server
```

## Common Commands

```bash
# Install dependencies
pip install -r requirements-web.txt

# Run development server
python web_app.py

# Run with Docker
docker-compose up

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## Key Files

| File | Purpose |
|------|---------|
| `zenon_ai.py` | Core Q&A engine: loads Markdown docs, creates embeddings, handles search and answer generation |
| `web_app.py` | FastAPI server with rate limiting, session management, health checks |
| `data/zenon_personality.md` | AI personality and response guidelines |
| `static/index.html` | Main web interface |
| `.env.example` | Configuration template |

## Environment Variables

Key settings in `.env`:
- `OPENAI_API_KEY` - Required for embeddings and chat
- `CONTEXT_DIR` - Path to documentation (default: `context`)
- `ZENON_PERSONALITY_FILE` - Path to personality file
- `REDIS_URL` - Redis connection for rate limiting

## Documentation Knowledge Base

All research documents are in `context/`. Key document types:

**Core Team Papers (Normative):**
- `1_ZENON_LIGHTPAPER_(CORE_TEAM).md`, `2_ZENON_WHITEPAPER_(CORE_TEAM).md`

**Greenpaper Series (Community-authored):**
- `ZENON_GREENPAPER.md` and `0x00` through `0x10` series

**Architecture/Research:**
- Node architecture, Bitcoin SPV integration, light clients, state management

## Key Concepts

- **Dual-Ledger Architecture:** Account-chains (parallel execution) + Momentum chain (global ordering)
- **Bounded Verification:** Verification under explicit resource constraints
- **zApps:** Proof-native applications
- **CEV:** Composable External Verification (e.g., Bitcoin SPV)
- **ACIs:** Application Contract Interfaces
