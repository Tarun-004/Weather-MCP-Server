from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("WeatherServer")

API_KEY = "59727b3f28fd25570c15bc658c55a4f9"


@mcp.tool()
def get_weather(city: str) -> str:
    """
    Get current weather for a city.
    """

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        return "Could not fetch weather."

    data = response.json()

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]

    return f"The weather in {city} is {description} with {temp}°C."


if __name__ == "__main__":
    mcp.run()