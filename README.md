# CSCI2910-Lab4-WeatherBuddy

Simple Python CLI that fetches **current weather** and a **5-day forecast**
from the OpenWeatherMap API, shows a concise summary, and renders an
**ASCII temperature trend chart**. Supports saving **favorite cities**.

## Features
- Current weather: temperature, feels-like, humidity, pressure, wind
- 5-day forecast (3-hour intervals summarized to daily averages)
- ASCII chart of temperature trends
- Save and re-use favorite cities
- Graceful errors for invalid city (404) and bad API key (401)

## Tech Stack
- Python 3.9+
- `requests` for HTTP
- `python-dotenv` for environment variables (.env)

## Prerequisites
- Python 3.9 or newer
- An OpenWeatherMap API key (free tier is fine)

## Setup

```bash
# clone or open the folder in VS Code
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
