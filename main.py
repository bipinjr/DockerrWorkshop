"""
Agent web service — exposes the weather tool via a FastAPI HTTP endpoint.
Designed to run inside the Docker container on port 8000.
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.tools import tool

load_dotenv()

# ---------- Tool definition (same as TestAPII.py) ----------
class WeatherInput(BaseModel):
    city: str = Field(description="Name of the city to get weather for")

@tool("get_weather", args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """
    Returns the current weather for a given city.
    Use this tool when the user asks about weather conditions.
    """
    if not city or not city.strip():
        raise ValueError("City name must be a non-empty string")
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("WEATHER_API_KEY not set in environment")
    # ... real API call would go here ...
    return f"Weather in {city}: 28°C, Sunny"

# ---------- FastAPI app ----------
app = FastAPI(title="Agent Tool Service", version="1.0.0")

class WeatherRequest(BaseModel):
    city: str = Field(description="Name of the city to get weather for")

@app.get("/")
def health_check():
    """Health check endpoint — returns 200 OK when the container is running."""
    return {"status": "ok", "service": "agent-tool-service"}

@app.post("/weather")
def weather_endpoint(req: WeatherRequest):
    """Call the weather tool and return its output."""
    try:
        result = get_weather.invoke({"city": req.city})
        return {"city": req.city, "weather": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
