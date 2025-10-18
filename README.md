# WeatherBuddy (CSCI 2910 – Lab 3/4)

CLI tool that calls the OpenWeatherMap API to show current weather and a 5-day forecast,
with an ASCII temperature trend. Includes error handling and a favorites feature.

## How to Run (Local)
1. Create a virtual environment (optional) and install:
2. Copy `.env.example` to `.env` and put your real key:
3. Run:

## Features
- Current weather (temp, humidity, pressure, wind)
- 5-day forecast summarized to daily averages
- ASCII temperature trend chart
- Save & reuse favorite cities
- Graceful 401/404/timeout handling

## Tech
- Python, `requests`, `python-dotenv`

## Notes
- **Do not commit `.env`**. API key must remain private.
- Free OWM keys can be throttled; retry if rate-limited.

## Issues (progress log)
- 2025-09-29: 401 Unauthorized — fixed by regenerating key & reloading env.
- 2025-09-30: Timeout on campus Wi-Fi — authenticated portal; raised timeout to 10s.
