import json
import os
from http import HTTPStatus

import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_BASE_URL = os.environ.get("OPENAI_API_BASE", "https://api.groq.com/openai/v1")
MODEL_NAME = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
TIMEOUT = int(os.environ.get("GROQ_TIMEOUT", "30"))


def handler(request):
    """Vercel serverless function — POST /api/agent"""
    if request.method != "POST":
        return _json(HTTPStatus.METHOD_NOT_ALLOWED, {"detail": "method not allowed"})

    try:
        body = request.get_json(silent=True) or {}
    except Exception:
        return _json(HTTPStatus.BAD_REQUEST, {"detail": "invalid json"})

    message = (body.get("message") or "").strip()
    if not message:
        return _json(HTTPStatus.BAD_REQUEST, {"detail": "message must be non-empty"})

    if not GROQ_API_KEY:
        return _json(HTTPStatus.INTERNAL_SERVER_ERROR, {
            "detail": "GROQ_API_KEY not configured"
        })

    try:
        resp = requests.post(
            f"{GROQ_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful, concise assistant. You are running as a "
                            "deployed agent service behind a REST API. Give clear, direct "
                            "answers. If asked about the service itself, explain that it is "
                            "a LangChain + FastAPI agent backed by Groq, containerized with "
                            "Docker, and deployable to Render, Railway, or Vercel."
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return _json(HTTPStatus.OK, {
            "message": content,
            "model": MODEL_NAME,
        })
    except requests.Timeout:
        return _json(HTTPStatus.GATEWAY_TIMEOUT, {"detail": "LLM call timed out"})
    except requests.HTTPError as exc:
        try:
            err_body = exc.response.json()
            detail = err_body.get("error", {}).get("message", str(exc))
        except Exception:
            detail = str(exc)
        status = exc.response.status_code
        return _json(status, {"detail": f"LLM call failed: {detail}"})
    except Exception as exc:
        return _json(HTTPStatus.BAD_GATEWAY, {"detail": f"LLM call failed: {exc}"})


def _json(status, payload):
    return {
        "statusCode": status,
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-store",
        },
        "body": json.dumps(payload),
    }
