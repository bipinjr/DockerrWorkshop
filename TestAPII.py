import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field

load_dotenv()  # load API keys from .env file

# Define input schema for the tool
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
    api_key = os.getenv("WEATHER_API_KEY")  # loaded from .env
    if not api_key:
        raise ValueError("WEATHER_API_KEY not set in environment")
    # ... real API call would go here ...
    return f"Weather in {city}: 28°C, Sunny"


if __name__ == "__main__":
    # Demonstrate the tool with valid and invalid inputs
    print("=== Valid call ===")
    print(get_weather.invoke({"city": "London"}))

    print("\n=== Invalid call (empty city) ===")
    try:
        get_weather.invoke({"city": ""})
    except ValueError as e:
        print(f"Caught expected error: {e}")
