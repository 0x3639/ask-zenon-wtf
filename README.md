# ask.zenon.wtf

An AI-powered Q&A interface for exploring Zenon Network of Momentum design research. Ask questions about protocol architecture, bounded verification, zApps, and more.

## Source Attribution

- **Research documentation:** Sourced from [TminusZ/zenon-developer-commons](https://github.com/TminusZ/zenon-developer-commons)
- **Application code:** Based on [kaine-ai](https://github.com/0x3639/kaine-ai)

## Tech Stack

- **Backend:** Python 3.11, FastAPI, OpenAI API (embeddings + GPT-4o)
- **Frontend:** Static HTML/CSS/JS (ChatGPT-style dark mode interface)
- **Infrastructure:** Docker, Redis (rate limiting), Caddy (reverse proxy)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/0x3639/ask-zenon-wtf.git
   cd ask-zenon-wtf
   ```

2. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

3. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

4. Run with Docker:
   ```bash
   docker-compose up --build
   ```

5. Open http://localhost:8000 in your browser

On first startup, the app will generate embeddings for all 98 documents (~20 seconds).

## Project Structure

```
context/              # 98 Zenon research documentation files
data/                 # AI personality configuration
static/               # Frontend (HTML, CSS, JS)
zenon_ai.py           # Core Q&A engine
web_app.py            # FastAPI web server
docker-compose.yml    # Docker configuration
Caddyfile             # Production reverse proxy config
```

## Documentation Topics

The knowledge base covers:

- Verification-first architecture and bounded verification
- Dual-ledger system design (account-chains + momentum chain)
- Bitcoin SPV integration research
- Light client protocols
- Proof-native applications (zApps)
- Node architecture (Pillars, Sentinels, Sentries, Supervisors)
- Composable External Verification (CEV)

## Configuration

Key environment variables (see `.env.example` for full list):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `CHAT_MODEL` | GPT model for answers | `gpt-4o` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-large` |
| `DEFAULT_CONTEXT_POSTS` | Documents per query | `15` |

## Production Deployment

See `DEPLOYMENT.md` for full production setup with Caddy reverse proxy.

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## License

Research documentation is from TminusZ/zenon-developer-commons. Application code is based on kaine-ai.
