FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Extra deps for the LangChain + FastAPI service (not needed by Vercel serverless functions)
RUN pip install --no-cache-dir \
    langgraph \
    langchain-core \
    langchain-openai \
    langsmith \
    fastapi>=0.115.0 \
    "uvicorn[standard]>=0.30.0"

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
