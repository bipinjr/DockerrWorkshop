# DockerrWorkshop

A LangChain agent backed by Groq's `qwen/qwen3.8-27b` model, exposed as a REST API via FastAPI. Dockerized and deployable to Vercel, Render, or Railway.

## What it does

Exposes an AI agent on port 8000:

- `GET /` — health check (returns service status, model name, backend)
- `GET /health` — detailed health (includes whether the API key is set, whether the model pinged successfully)
- `POST /agent` — accepts `{"message": "Hello"}`, calls Groq, returns `{"message": "...", "model": "..."}`

Uses LangChain's `ChatOpenAI` pointing at Groq's OpenAI-compatible endpoint. Input validated with Pydantic. Secrets via `.env` (never committed).

## Project structure

```
.
├── .dockerignore      # keeps .env, .venv, cache out of the Docker image
├── .gitignore         # keeps .env, venv, cache, .opencode out of Git
├── .env.example       # template for required env vars (copy to .env)
├── Dockerfile         # Python 3.11-slim image, installs deps, runs main.py
├── vercel.json        # Vercel config: serverless functions in api/, static site
├── main.py            # FastAPI app (the deployed service)
├── requirements.txt   # Python dependencies (minimal for Vercel; full in Dockerfile)
├── index.html         # Dark-mode landing page with live chat demo
├── README.md
├── api/
│   ├── health.py      # Vercel serverless function — GET /api/health
│   └── agent.py       # Vercel serverless function — POST /api/agent
└── .venv/             # local virtualenv (gitignored)
```

Workshop exercise files (`LangGraph Agent.py`, `TestAPII.py`, `UnitTest.py`, `langConditionalRouting.py`, `check_models.py`) are kept locally but not included in the deployed image.

## Local run (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add your GROQ_API_KEY
python3 main.py
```

Then:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl -X POST http://localhost:8000/agent \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello! Who are you?"}'
```

## Docker

```bash
docker build -t agent:latest .
docker run -p 8000:8000 --env-file .env agent:latest
curl http://localhost:8000/
```

## Vercel deploy

The repo is pre-configured for Vercel. Two serverless functions live in `api/`:

- `api/health.py` — `GET /api/health`
- `api/agent.py` — `POST /api/agent` (calls Groq directly via `requests`)

`index.html` is the static landing page with a live chat demo.

1. Push this repo to GitHub.
2. In Vercel: **Add New → Import Git Repository** → select `bipinjr/DockerrWorkshop`.
3. In **Project Settings → Environment Variables**, add:
   - `GROQ_API_KEY` = your Groq API key (starts with `gsk_`)
4. Deploy. You get a `*.vercel.app` URL.

The landing page's chat demo will work against your deployed endpoint — paste the URL into the API URL field on the page.

## Render / Railway deploy

Both platforms use the `Dockerfile`:

1. Push to GitHub.
2. Connect the repo in Render or Railway.
3. Set `GROQ_API_KEY` in the platform's environment variables.
4. Deploy — the service listens on port 8000.

- Render: Web Service → connect repo → detects Dockerfile → add env var → deploy → `*.onrender.com`
- Railway: New Project → Deploy from GitHub → uses Dockerfile → add variable → deploy → `*.railway.app`

## Environment variables

| Variable          | Required | Description                                   |
|-------------------|----------|-----------------------------------------------|
| `GROQ_API_KEY`    | Yes      | Groq API key (starts with `gsk_`)            |
| `OPENAI_API_BASE` | No       | Defaults to Groq's endpoint                   |
| `GROQ_MODEL`      | No       | Model name; defaults to `qwen/qwen3.8-27b`   |
| `GROQ_TIMEOUT`    | No       | Seconds; defaults to `30`                     |

## Checklist

- [x] FastAPI service with health + agent endpoints
- [x] LangChain `ChatOpenAI` → Groq `qwen/qwen3.8-27b`
- [x] Pydantic input validation (empty message → 400)
- [x] `.env` with `GROQ_API_KEY`, loaded via `python-dotenv`
- [x] `.env` in `.gitignore` (never committed)
- [x] Dockerfile on `python:3.11-slim`, port 8000
- [x] Vercel config: serverless functions + static site
- [x] `api/health.py` and `api/agent.py` as Vercel functions
- [x] `index.html` landing page with dark mode + live chat demo
- [x] Cloud-deployable to Vercel, Render, and Railway
