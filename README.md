# 🌤️ Weather MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that gives AI assistants (like Claude) the ability to fetch real-time weather data for any city using the [OpenWeatherMap API](https://openweathermap.org/api).

---

## 📌 What It Does

This MCP server exposes a single tool — `get_weather` — that an AI assistant can call to retrieve the current weather conditions for any city in the world.

**Example response:**
```
The weather in London is light rain with 13°C.
```

---

## 🛠️ Tech Stack

- **Python** — core language
- **[FastMCP](https://github.com/jlowin/fastmcp)** — framework for building MCP servers quickly
- **[OpenWeatherMap API](https://openweathermap.org/api)** — weather data source
- **[Requests](https://pypi.org/project/requests/)** — HTTP client

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Tarun-004/weather-mcp.git
cd weather-mcp
```

### 2. Install Dependencies

```bash
pip install fastmcp requests
```

### 3. Add Your API Key

Get a free API key from [OpenWeatherMap](https://openweathermap.org/api), then open `server.py` and replace the placeholder:

```python
API_KEY = "your_openweathermap_api_key_here"
```

> ⚠️ **Never commit your API key to GitHub.** Consider using a `.env` file and the `python-dotenv` package to keep it safe.

### 4. Run the Server

```bash
python server.py
```

---

## 🔧 MCP Configuration

To connect this server to an MCP-compatible client (e.g., Claude Desktop), add the following to your MCP config file:

```jsonc
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

---

## 🧰 Available Tool

### `get_weather`

Fetches the current weather for a given city.

| Parameter | Type   | Description                        |
|-----------|--------|------------------------------------|
| `city`    | string | Name of the city (e.g., `"Tokyo"`) |

**Returns:** A plain-text string with the weather description and temperature in Celsius.

---

## 💡 Ideas for Future Improvements

- [ ] Add support for forecasts (5-day, hourly)
- [ ] Return humidity, wind speed, and UV index
- [ ] Support coordinates (lat/lon) in addition to city name
- [ ] Use environment variables for the API key
- [ ] Add error handling for invalid city names

