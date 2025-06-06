from fastapi import FastAPI, Request
import requests

app = FastAPI()

# Metadata endpoint (Claude reads this first)
@app.get("/")
async def get_metadata():
    return {
        "name": "weather-tool",
        "description": "Fetches real-time weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "temperature": {"type": "string"},
                "description": {"type": "string"}
            }
        }
    }

# Claude POSTs tool input here
@app.post("/call")
async def call_tool(request: Request):
    data = await request.json()
    city = data.get("city")

    # Use OpenWeatherMap to get weather
    api_key = "f1e392781d2b2360226bab8a382791de"  # insert your API key here
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

    res = requests.get(url)
    weather_data = res.json()

    temperature = weather_data["main"]["temp"]
    description = weather_data["weather"][0]["description"]

    return {
        "temperature": f"{temperature}°C",
        "description": description
    }
