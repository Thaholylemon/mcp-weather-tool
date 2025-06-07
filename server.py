import os
from fastapi import FastAPI, Request, HTTPException
import requests
from typing import Dict, Any

app = FastAPI(title="Weather MCP Server")

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
    try:
        data = await request.json()
        city = data.get("city")
        
        if not city:
            raise HTTPException(status_code=400, detail="City parameter is required")

        # Use OpenWeatherMap to get weather
        api_key = "f1e392781d2b2360226bab8a382791de"
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

        response = requests.get(url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Weather API error: {response.status_code}")
        
        weather_data = response.json()
        
        # Check if the required fields exist in the response
        if "main" not in weather_data or "weather" not in weather_data:
            raise HTTPException(status_code=500, detail="Invalid weather data received")
        
        if not weather_data["weather"]:
            raise HTTPException(status_code=500, detail="No weather information available")

        temperature = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]

        return {
            "temperature": f"{temperature}°C",
            "description": description
        }
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Missing data field: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "weather-mcp-server"}

# This is important for deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)