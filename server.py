from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("WeatherServer")

API_KEY = "paste_your_api_key"


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_coords(city: str) -> tuple[float, float] | None:
    """Resolve a city name to (lat, lon) using the OWM Geocoding API."""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    r = requests.get(url)
    if r.status_code != 200 or not r.json():
        return None
    data = r.json()[0]
    return data["lat"], data["lon"]


# ── Tool 1 : Basic weather (original) ─────────────────────────────────────────

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current temperature and a short weather description for a city."""
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return f"Could not fetch weather for '{city}'."

    data = response.json()
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return f"The weather in {city} is {description} with {temp}°C."


# ── Tool 2 : Detailed current conditions ──────────────────────────────────────

@mcp.tool()
def get_weather_conditions(city: str) -> str:
    """
    Get a detailed snapshot of current weather conditions for a city,
    including sky conditions (sunny/cloudy/rainy etc.), feels-like temperature,
    humidity, wind speed, and visibility.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return f"Could not fetch weather conditions for '{city}'."

    d = r.json()
    main   = d["main"]
    wind   = d["wind"]
    clouds = d["clouds"]["all"]          # % cloud cover
    weather_id   = d["weather"][0]["id"]
    description  = d["weather"][0]["description"].capitalize()

    # Human-friendly sky label
    if weather_id < 300:
        sky = "⛈️  Thunderstorm"
    elif weather_id < 400:
        sky = "🌦️  Drizzle"
    elif weather_id < 600:
        sky = "🌧️  Rainy"
    elif weather_id < 700:
        sky = "❄️  Snowy"
    elif weather_id < 800:
        sky = "🌫️  Foggy / Hazy"
    elif weather_id == 800:
        sky = "☀️  Clear / Sunny"
    elif weather_id == 801:
        sky = "🌤️  Mostly Sunny (few clouds)"
    elif weather_id == 802:
        sky = "⛅  Partly Cloudy"
    elif weather_id == 803:
        sky = "🌥️  Mostly Cloudy"
    else:
        sky = "☁️  Overcast"

    visibility_km = d.get("visibility", 0) / 1000
    wind_kph      = round(wind["speed"] * 3.6, 1)

    return (
        f"📍 {city.title()} — Current Conditions\n"
        f"────────────────────────────────\n"
        f"Sky       : {sky}\n"
        f"Details   : {description}\n"
        f"Temp      : {main['temp']}°C  (feels like {main['feels_like']}°C)\n"
        f"Humidity  : {main['humidity']}%\n"
        f"Wind      : {wind_kph} km/h\n"
        f"Cloud cover: {clouds}%\n"
        f"Visibility: {visibility_km:.1f} km"
    )


# ── Tool 3 : AQI ──────────────────────────────────────────────────────────────

@mcp.tool()
def get_aqi(city: str) -> str:
    """
    Get the current Air Quality Index (AQI) and key pollutant levels for a city.
    Returns an overall AQI category (Good / Fair / Moderate / Poor / Very Poor)
    along with PM2.5, PM10, NO₂, and O₃ values in µg/m³.
    """
    coords = _get_coords(city)
    if coords is None:
        return f"Could not find coordinates for '{city}'."

    lat, lon = coords
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={API_KEY}"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return f"Could not fetch AQI data for '{city}'."

    item = r.json()["list"][0]
    aqi_index  = item["main"]["aqi"]          # 1–5
    components = item["components"]

    aqi_labels = {
        1: ("Good",      "✅", "Air quality is great — safe for all activities."),
        2: ("Fair",      "🟡", "Air quality is acceptable. Sensitive groups may feel mild effects."),
        3: ("Moderate",  "🟠", "Sensitive individuals should limit prolonged outdoor exertion."),
        4: ("Poor",      "🔴", "Everyone may start to experience health effects. Reduce outdoor activity."),
        5: ("Very Poor", "🟣", "Health warnings in effect. Avoid outdoor activities."),
    }
    label, icon, advice = aqi_labels.get(aqi_index, ("Unknown", "❓", ""))

    return (
        f"💨 {city.title()} — Air Quality Index\n"
        f"────────────────────────────────\n"
        f"AQI       : {icon} {label} (index {aqi_index}/5)\n"
        f"Advice    : {advice}\n"
        f"\nKey Pollutants (µg/m³):\n"
        f"  PM2.5   : {components.get('pm2_5', 'N/A')}\n"
        f"  PM10    : {components.get('pm10',  'N/A')}\n"
        f"  NO₂     : {components.get('no2',   'N/A')}\n"
        f"  O₃      : {components.get('o3',    'N/A')}\n"
        f"  CO      : {components.get('co',    'N/A')}"
    )


# ── Tool 4 : Weekly forecast ───────────────────────────────────────────────────

@mcp.tool()
def get_weekly_forecast(city: str) -> str:
    """
    Get a plain-English 5-day weather forecast for a city.
    Summarises each day as one readable line, e.g.
    'Thursday — Heavy rain, 22°C / 17°C. Carry an umbrella!'
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric&cnt=40"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return f"Could not fetch forecast for '{city}'."

    # Group 3-hourly slots by date
    from collections import defaultdict
    from datetime import datetime

    daily: dict[str, dict] = defaultdict(lambda: {
        "temps": [], "ids": [], "descriptions": []
    })

    for slot in r.json()["list"]:
        date_str = slot["dt_txt"][:10]                  # "YYYY-MM-DD"
        daily[date_str]["temps"].append(slot["main"]["temp"])
        daily[date_str]["ids"].append(slot["weather"][0]["id"])
        daily[date_str]["descriptions"].append(slot["weather"][0]["description"])

    def _day_summary(date_str: str, info: dict) -> str:
        day_name  = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        max_temp  = round(max(info["temps"]))
        min_temp  = round(min(info["temps"]))

        # Pick the most severe weather id of the day
        worst_id  = min(info["ids"])
        # Most frequent description
        desc      = max(set(info["descriptions"]), key=info["descriptions"].count).capitalize()

        # Tip
        if worst_id < 600:
            tip = "🌂 Carry an umbrella!"
        elif worst_id < 700:
            tip = "🧥 Bundle up — snow expected."
        elif worst_id < 800:
            tip = "😷 Visibility may be low."
        elif worst_id == 800:
            tip = "😎 Great day to be outside."
        else:
            tip = "🌥️ Clouds around — light jacket handy."

        return f"  {day_name:<12} {desc:<30} {max_temp}°C / {min_temp}°C   {tip}"

    lines = [f"📅 5-Day Forecast for {city.title()}", "─" * 60]
    for date_str, info in sorted(daily.items()):
        lines.append(_day_summary(date_str, info))

    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
