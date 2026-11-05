"""طبقة التعامل مع OpenWeather API."""
from typing import Any, Dict, List

import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"
TIMEOUT = 10


class WeatherError(Exception):
    """Base error for weather operations."""


class CityNotFoundError(WeatherError):
    pass


class InvalidAPIKeyError(WeatherError):
    pass


class ConnectionProblemError(WeatherError):
    pass


def _request(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        resp = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise ConnectionProblemError("The request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise ConnectionProblemError("Could not connect. Check your internet connection.")
    except requests.exceptions.RequestException as e:
        raise ConnectionProblemError(f"Request failed: {e}")

    if resp.status_code == 404:
        raise CityNotFoundError("City not found. Check the spelling and try again.")
    if resp.status_code == 401:
        raise InvalidAPIKeyError("Invalid API key. Check your OpenWeather key.")
    if resp.status_code == 429:
        raise WeatherError("Too many requests. Please wait a moment.")
    if not resp.ok:
        raise WeatherError(f"Unexpected error from the weather service ({resp.status_code}).")

    try:
        return resp.json()
    except ValueError:
        raise WeatherError("The weather service returned an invalid response.")


def parse_current(data: Dict[str, Any]) -> Dict[str, Any]:
    """Turn the raw JSON into a clean dictionary."""
    try:
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].title(),
            "icon": data["weather"][0]["icon"],
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
        }
    except (KeyError, IndexError, TypeError):
        raise WeatherError("Unexpected data format from the weather service.")


def parse_forecast(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Keep one reading per day (around noon) from the 3-hour forecast list."""
    try:
        items = data["list"]
        days: Dict[str, Dict[str, Any]] = {}
        for item in items:
            date, time = item["dt_txt"].split(" ")
            entry = {
                "date": date,
                "temp": item["main"]["temp"],
                "description": item["weather"][0]["description"].title(),
                "humidity": item["main"]["humidity"],
            }
            if date not in days or time.startswith("12"):
                days[date] = entry
        return list(days.values())
    except (KeyError, IndexError, TypeError, ValueError):
        raise WeatherError("Unexpected forecast format from the weather service.")


def get_current_weather(city: str, api_key: str, units: str = "metric") -> Dict[str, Any]:
    if not city or not city.strip():
        raise WeatherError("Please enter a city name.")
    if not api_key:
        raise InvalidAPIKeyError("API key is missing.")
    data = _request("weather", {"q": city.strip(), "appid": api_key, "units": units})
    return parse_current(data)


def get_forecast(city: str, api_key: str, units: str = "metric") -> List[Dict[str, Any]]:
    data = _request("forecast", {"q": city.strip(), "appid": api_key, "units": units})
    return parse_forecast(data)
