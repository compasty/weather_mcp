from typing import Any
import httpx
import os
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

# Initialize FastMCP server
mcp = FastMCP("weather")

url = os.getenv("qweather_host") + "/v7/weather/now"
headers = {
    "X-QW-Api-Key": os.getenv("qweather_api_key"),
}
geo_url = "https://geoapi.qweather.com/v2/city/lookup"

async def make_geo_req(location: str) -> str:
    params = {
        "location": location,
        "region": "cn"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(geo_url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            content = response.json()
            if content["code"] == "200":
                locations = content["location"]
                if len(locations) > 0:
                    return locations[0]["id"]
                else:
                    return None
            else:
                return None
        except Exception:
            return None


async def make_weather_req(location_id: str) -> Any:
    params = {
        "location": location_id
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def format_weather(location: str, weather: dict) -> str:
    """Format weather info into a readable string."""
    return f"""
地区: {location}
温度: {weather.get('temp', 'Unknown')}
天气: {weather.get('text', 'Unnown')}
体感温度: {weather.get('feelsLike', 'Unknown')}
风向: {weather.get('windDir', '') + ' ' + weather.get('windScale', 'Unknown') + '级'}
"""

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get current weather for a location.

    Args:
        location: city name of china
    """
    # Get the forecast URL from the points response
    location_id = await make_geo_req(location)

    if location_id is None:
        return "Unable to fetch detailed city."
    weather = await make_weather_req(location_id)

    # 格式化输出
    if weather is None:
        return "Unable to fetch city weather"
    else:
        return format_weather(location, weather["now"])

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')