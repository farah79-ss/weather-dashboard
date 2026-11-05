"""Tests use mocked HTTP responses, so no real API key or internet is needed."""
import unittest
from unittest.mock import MagicMock, patch

import requests

import weather

CURRENT_SAMPLE = {
    "name": "Riyadh",
    "sys": {"country": "SA"},
    "coord": {"lat": 24.69, "lon": 46.72},
    "main": {"temp": 31.2, "feels_like": 30.5, "humidity": 20, "pressure": 1010},
    "wind": {"speed": 3.4},
    "weather": [{"description": "clear sky", "icon": "01d"}],
}

FORECAST_SAMPLE = {
    "list": [
        {"dt_txt": "2026-11-05 09:00:00", "main": {"temp": 28, "humidity": 25}, "weather": [{"description": "clear sky"}]},
        {"dt_txt": "2026-11-05 12:00:00", "main": {"temp": 33, "humidity": 18}, "weather": [{"description": "sunny"}]},
        {"dt_txt": "2026-11-06 12:00:00", "main": {"temp": 30, "humidity": 22}, "weather": [{"description": "few clouds"}]},
    ]
}


def fake_response(status=200, json_data=None):
    r = MagicMock()
    r.status_code = status
    r.ok = 200 <= status < 300
    r.json.return_value = json_data if json_data is not None else {}
    return r


class TestWeather(unittest.TestCase):
    @patch("weather.requests.get")
    def test_current_ok(self, mock_get):
        mock_get.return_value = fake_response(200, CURRENT_SAMPLE)
        data = weather.get_current_weather("Riyadh", "key")
        self.assertEqual(data["city"], "Riyadh")
        self.assertEqual(data["description"], "Clear Sky")
        self.assertAlmostEqual(data["temp"], 31.2)

    @patch("weather.requests.get")
    def test_city_not_found(self, mock_get):
        mock_get.return_value = fake_response(404)
        with self.assertRaises(weather.CityNotFoundError):
            weather.get_current_weather("Nowhereville", "key")

    @patch("weather.requests.get")
    def test_invalid_key(self, mock_get):
        mock_get.return_value = fake_response(401)
        with self.assertRaises(weather.InvalidAPIKeyError):
            weather.get_current_weather("Riyadh", "bad")

    @patch("weather.requests.get", side_effect=requests.exceptions.ConnectionError)
    def test_connection_error(self, _mock_get):
        with self.assertRaises(weather.ConnectionProblemError):
            weather.get_current_weather("Riyadh", "key")

    @patch("weather.requests.get", side_effect=requests.exceptions.Timeout)
    def test_timeout(self, _mock_get):
        with self.assertRaises(weather.ConnectionProblemError):
            weather.get_current_weather("Riyadh", "key")

    @patch("weather.requests.get")
    def test_bad_json_shape(self, mock_get):
        mock_get.return_value = fake_response(200, {"unexpected": True})
        with self.assertRaises(weather.WeatherError):
            weather.get_current_weather("Riyadh", "key")

    def test_empty_city(self):
        with self.assertRaises(weather.WeatherError):
            weather.get_current_weather("   ", "key")

    def test_forecast_one_per_day_prefers_noon(self):
        days = weather.parse_forecast(FORECAST_SAMPLE)
        self.assertEqual(len(days), 2)
        self.assertEqual(days[0]["temp"], 33)


if __name__ == "__main__":
    unittest.main()
