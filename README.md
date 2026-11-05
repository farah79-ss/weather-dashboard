# Weather Dashboard

A web dashboard showing current weather and a 5-day forecast for any city.
Built with **Python**, **Streamlit**, **Requests**, and the **OpenWeather API**.

## Features
- Search any city, switch between Celsius / Fahrenheit
- Current temperature, feels-like, humidity, wind, description and icon
- Map pin and 5-day forecast (chart + table)
- Error handling: city not found, invalid API key, no internet, timeout, bad JSON
- Unit tests with mocked API responses (no key needed to test)

## Setup
1. Get a free API key at https://openweathermap.org/api
2. Install:
   ```bash
   pip install -r requirements.txt
   ```
3. Provide the key (any one of these):
   ```bash
   export OPENWEATHER_API_KEY=your_key_here
   ```
   or paste it in the app sidebar, or put it in `.streamlit/secrets.toml`:
   ```toml
   OPENWEATHER_API_KEY = "your_key_here"
   ```

## Run
```bash
streamlit run app.py
```

## Test
```bash
python -m unittest -v
```

## Structure
| File | Purpose |
|------|---------|
| `weather.py` | API calls, JSON parsing, custom errors |
| `app.py` | Streamlit interface |
| `test_weather.py` | Unit tests (mocked HTTP) |

> Never commit your API key. `.gitignore` already excludes `secrets.toml`.

## Skills shown
REST APIs, JSON processing, error handling, Streamlit, data display (pandas), unit testing with mocks.
