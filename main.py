"""
Agent service — Groq LLM backed via LangChain, exposed as a FastAPI REST API.
Reads GROQ_API_KEY from .env (never committed). Serves on port 8000.
"""
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.groq.com/openai/v1")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not set. Copy .env.example to .env and add your key."
    )

# ---------- LLM setup (Groq via OpenAI-compatible endpoint) ----------
llm = ChatOpenAI(
    api_key=GROQ_API_KEY,
    base_url=OPENAI_API_BASE,
    model="qwen/qwen3.8-27b",
    temperature=0.7,
    timeout=30,
)

MODEL_NAME = llm.model_name

# ---------- Input / output schemas ----------
class AgentRequest(BaseModel):
    message: str = Field(..., description="User message to send to the agent")

class AgentResponse(BaseModel):
    message: str
    model: str
    usage: dict = {}


# ---------- System prompt ----------
SYSTEM_PROMPT = (
    "You are a helpful, concise assistant. You are running as a deployed agent "
    "service behind a REST API. Give clear, direct answers. If the user asks "
    "about the service itself, explain that it is a LangChain + FastAPI agent "
    "backed by Groq, containerized with Docker, and deployable to Render or Railway."
)


# ---------- App lifecycle ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Health check on startup
    try:
        llm.invoke([HumanMessage(content="ping")])
        app.state.healthy = True
    except Exception as exc:
        app.state.healthy = False
        print(f"LLM ping failed on startup: {exc}")
    yield


app = FastAPI(
    title="Agent Service",
    description="LangChain agent backed by Groq, served over HTTP",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def health():
    healthy = getattr(app.state, "healthy", None)
    return {
        "status": "ok" if healthy else "degraded",
        "service": "agent-service",
        "model": MODEL_NAME,
        "backend": "groq",
    }


@app.post("/agent", response_model=AgentResponse)
def agent_endpoint(req: AgentRequest):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="message must be non-empty")

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=req.message),
        ]
        response = llm.invoke(messages)
        return AgentResponse(
            message=response.content,
            model=MODEL_NAME,
            usage={},
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}")


@app.get("/health")
def detailed_health():
    return {
        "service": "agent-service",
        "model": MODEL_NAME,
        "backend": "groq",
        "api_key_set": bool(GROQ_API_KEY),
        "healthy": getattr(app.state, "healthy", None),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
