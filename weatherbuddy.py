# weatherbuddy.py
import os
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

import requests
from dotenv import load_dotenv

# ---------- Config & Env ----------
# Load .env from the same folder as this script (reliable even if you run from elsewhere)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.getenv("OWM_API_KEY")  # <- must match your .env key name
BASE_URL = "https://api.openweathermap.org/data/2.5"
FAVORITES_FILE = Path("favorites.txt")

if not API_KEY:
    print(
        f"ERROR: Missing OWM_API_KEY in {ENV_PATH}.\n"
        "Create .env next to weatherbuddy.py with a line like:\n"
        "OWM_API_KEY=your_openweathermap_key_here"
    )
    sys.exit(1)

# ---------- Favorites ----------
def load_favorites() -> List[str]:
    if not FAVORITES_FILE.exists():
        return []
    return [
        line.strip() for line in FAVORITES_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

def save_favorite(city: str) -> None:
    favs = set(load_favorites())
    favs.add(city.strip())
    FAVORITES_FILE.write_text("\n".join(sorted(favs)) + "\n", encoding="utf-8")
    print(f"{city} added to favorites.")

# ---------- API Calls ----------
def _request(endpoint: str, params: Dict[str, str]) -> Optional[Dict]:
    """Internal helper to perform a GET request with basic error handling."""
    url = f"{BASE_URL}/{endpoint}"
    try:
        r = requests.get(url, params=params, timeout=12)
        if r.status_code == 404:
            print("City not found (404). Please check the spelling.")
            return None
        if r.status_code == 401:
            print("Unauthorized (401). Check your API key (OWM_API_KEY) or account activation.")
            return None
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

def get_current_weather(city: str) -> Optional[Dict]:
    return _request("weather", {"q": city, "appid": API_KEY, "units": "metric"})

def get_forecast(city: str) -> Optional[Dict]:
    return _request("forecast", {"q": city, "appid": API_KEY, "units": "metric"})

# ---------- Display Helpers ----------
def display_current_weather(data: Optional[Dict]) -> None:
    if not data or "main" not in data:
        print("No current weather data available.")
        return

    name = data.get("name", "?")
    country = data.get("sys", {}).get("country", "")
    main = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    wind = data.get("wind", {})

    print("\nCurrent Weather")
    print("-" * 40)
    print(f"City: {name}, {country}")
    print(f"Temperature: {main.get('temp', '?')}°C (feels {main.get('feels_like', '?')}°C)")
    print(f"Humidity: {main.get('humidity', '?')}% | Pressure: {main.get('pressure', '?')} hPa")
    print(f"Condition: {weather.get('description', 'N/A').title()}")
    if "speed" in wind:
        print(f"Wind: {wind.get('speed')} m/s @ {wind.get('deg', '?')}°")

def summarize_forecast_daily(forecast_json: Dict) -> List[Tuple[str, float]]:
    """Return list of (YYYY-MM-DD, avg_temp) for up to 5 days."""
    buckets: Dict[str, List[float]] = defaultdict(list)
    for slot in forecast_json.get("list", []):
        dt_txt = slot.get("dt_txt")
        temp = slot.get("main", {}).get("temp")
        if not dt_txt or temp is None:
            continue
        day = dt_txt[:10]  # YYYY-MM-DD
        buckets[day].append(temp)

    daily: List[Tuple[str, float]] = []
    for day, temps in sorted(buckets.items()):
        daily.append((day, sum(temps) / len(temps)))
    return daily[:5]

def ascii_chart(dailies: List[Tuple[str, float]]) -> str:
    if not dailies:
        return "(no data)"
    temps = [t for _, t in dailies]
    tmin, tmax = min(temps), max(temps)
    span = max(1.0, tmax - tmin)
    lines = []
    for day, t in dailies:
        width = int(((t - tmin) / span) * 40)  # max 40 chars
        bar = "#" * max(1, width)
        lines.append(f"{day} | {bar} {t:.1f}°C")
    return "\n".join(lines)

def display_forecast(data: Optional[Dict]) -> None:
    if not data or "list" not in data:
        print("No forecast data available.")
        return

    city = data.get("city", {}).get("name", "?")
    print(f"\n5-Day Forecast — {city}")
    print("-" * 40)
    dailies = summarize_forecast_daily(data)
    for day, avg in dailies:
        print(f"{day}: {avg:.1f}°C (avg)")

    print("\nTemperature Trend (ASCII)")
    print(ascii_chart(dailies))

# ---------- CLI ----------
def choose_city() -> str:
    """Prompt user for a city, showing favorites if available."""
    favs = load_favorites()
    print("\nWeatherBuddy")
    if favs:
        print("Favorites:")
        for i, c in enumerate(favs, start=1):
            print(f"  {i}) {c}")
        print("  0) Enter a new city")
        choice = input("Select a favorite (number) or 0 to type a city: ").strip()
        if choice.isdigit():
            n = int(choice)
            if n == 0:
                return input("Enter city name: ").strip()
            if 1 <= n <= len(favs):
                return favs[n - 1]
    return input("Enter city name (or 'q' to quit): ").strip()

def main() -> None:
    while True:
        city = choose_city()
        if not city:
            print("Please enter a city name.")
            continue
        if city.lower() in {"q", "quit", "exit"}:
            break

        current = get_current_weather(city)
        display_current_weather(current)

        forecast = get_forecast(city)
        display_forecast(forecast)

        if current and city not in load_favorites():
            save = input("\nSave city to favorites? (y/n): ").strip().lower()
            if save == "y":
                save_favorite(city)

        again = input("\nLook up another city? (y/n): ").strip().lower()
        if again != "y":
            break

if __name__ == "__main__":
    main()
