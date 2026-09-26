import json
import os


def handler(request):
    """Vercel serverless function — GET /api/health"""
    groq_key = os.environ.get("GROQ_API_KEY", "")
    groq_model = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-store",
        },
        "body": json.dumps({
            "status": "ok",
            "service": "agent-service",
            "model": groq_model,
            "backend": "groq",
            "api_key_set": bool(groq_key),
            "framework": "vercel-python",
        }),
    }
