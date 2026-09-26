# DockerrWorkshop

A LangChain agent tool packaged as a Docker container with FastAPI.

## What it does

Exposes a weather tool as a REST API on port 8000:

- `GET /` — health check, returns `{"status": "ok"}`
- `POST /weather` — accepts `{"city": "London"}`, returns weather info

The tool uses a Pydantic input schema for validation and reads its API key from a `.env` file (never committed).

## Project structure

```
.
├── .dockerignore      # keeps .env and cache out of the Docker image
├── .gitignore         # keeps .env, venv, cache out of Git
├── Dockerfile         # Python 3.11-slim image, installs deps, runs main.py
├── main.py            # FastAPI app (the deployed service)
├── requirements.txt   # Python dependencies
└── README.md
```

Workshop exercise files (`LangGraph Agent.py`, `TestAPII.py`, `UnitTest.py`, `langConditionalRouting.py`) are kept locally but not included in the deployed image.

## Local run (without Docker)

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your WEATHER_API_KEY
python3 main.py
```

Then:
```
curl http://localhost:8000/
curl -X POST http://localhost:8000/weather -H 'Content-Type: application/json' -d '{"city":"London"}'
```

## Docker

```
docker build -t my-agent:latest .
docker run -p 8000:8000 --env-file .env my-agent:latest
curl http://localhost:8000/
```

## Cloud deploy (Render / Railway)

1. Push this repo to GitHub.
2. Connect the repo in Render or Railway.
3. Set `WEATHER_API_KEY` as an environment variable in the platform dashboard (not in code).
4. Deploy — the service listens on port 8000.

## Environment variables

| Variable          | Required | Description                        |
|-------------------|----------|------------------------------------|
| `WEATHER_API_KEY` | Yes      | API key for the weather service    |

## Workshop checklist (Session 4)

- [x] `@tool` function with docstring (`get_weather`)
- [x] Pydantic input schema (`WeatherInput`)
- [x] `.env` with API key, loaded via `python-dotenv`
- [x] Input validation raising clear errors (empty city, missing key)
- [x] `.env` in `.gitignore`

## Workshop checklist (Session 5)

- [x] Dockerfile in project root
- [x] `docker build` ready (tested-equivalent via uv; verify with Docker on your machine)
- [x] `docker run` ready (main.py serves on 0.0.0.0:8000)
- [ ] Cloud deploy — connect repo to Render/Railway
- [ ] Set `WEATHER_API_KEY` in cloud platform dashboard
