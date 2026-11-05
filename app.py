"""Weather Dashboard - Streamlit UI."""
import os

import pandas as pd
import streamlit as st

from weather import (
    CityNotFoundError,
    ConnectionProblemError,
    InvalidAPIKeyError,
    WeatherError,
    get_current_weather,
    get_forecast,
)

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="centered")
st.title("🌤️ Weather Dashboard")

def load_api_key() -> str:
    key = os.getenv("OPENWEATHER_API_KEY", "")
    if key:
        return key
    try:
        return st.secrets.get("OPENWEATHER_API_KEY", "")
    except Exception:  # no secrets.toml file
        return ""


api_key = load_api_key()
if not api_key:
    api_key = st.sidebar.text_input("OpenWeather API key", type="password")

unit_label = st.sidebar.radio("Units", ["Celsius", "Fahrenheit"])
units = "metric" if unit_label == "Celsius" else "imperial"
symbol = "°C" if units == "metric" else "°F"
speed = "m/s" if units == "metric" else "mph"

city = st.text_input("City", value="Riyadh", placeholder="e.g. Jeddah, London, Tokyo")

if st.button("Get weather", type="primary"):
    try:
        with st.spinner("Loading..."):
            current = get_current_weather(city, api_key, units)
            forecast = get_forecast(city, api_key, units)
    except CityNotFoundError as e:
        st.warning(str(e))
    except InvalidAPIKeyError as e:
        st.error(str(e))
    except ConnectionProblemError as e:
        st.error(str(e))
    except WeatherError as e:
        st.error(str(e))
    else:
        st.subheader(f'{current["city"]}, {current["country"]}')
        st.image(f'https://openweathermap.org/img/wn/{current["icon"]}@2x.png', width=100)
        st.write(current["description"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temperature", f'{current["temp"]:.1f}{symbol}')
        c2.metric("Feels like", f'{current["feels_like"]:.1f}{symbol}')
        c3.metric("Humidity", f'{current["humidity"]}%')
        c4.metric("Wind", f'{current["wind_speed"]} {speed}')

        st.map(pd.DataFrame({"lat": [current["lat"]], "lon": [current["lon"]]}))

        st.subheader("5-day forecast")
        df = pd.DataFrame(forecast)
        st.line_chart(df.set_index("date")["temp"])
        st.dataframe(
            df.rename(columns={"date": "Date", "temp": f"Temp ({symbol})", "description": "Weather", "humidity": "Humidity %"}),
            hide_index=True,
            use_container_width=True,
        )
