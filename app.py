import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import plotly.express as px

API_KEY = "YOUR_API_KEYS_HERE"  # Replace with your actual key

# Get user IP-based location
def get_user_location():
    try:
        res = requests.get("http://ip-api.com/json/")
        data = res.json()
        return data.get("city", ""), data.get("lat", 0), data.get("lon", 0)
    except:
        return "", 0, 0

# Get coordinates from a city name
def get_coordinates(city_name):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
    res = requests.get(geo_url).json()
    if res:
        return res[0]["lat"], res[0]["lon"]
    else:
        return None, None

def get_current_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    return requests.get(url).json()

def get_forecast(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    filtered = []
    for entry in data["list"]:
        if "12:00:00" in entry["dt_txt"]:
            filtered.append(entry)
    return data["list"], filtered

def get_weather_theme(description):
    desc = description.lower()
    if "cloud" in desc:
        return "☁️", "https://images.unsplash.com/photo-1508264165352-258859e62245"
    elif "clear" in desc:
        return "☀️", "https://images.unsplash.com/photo-1501973801540-537f08ccae7d"
    elif "rain" in desc:
        return "🌧️", "https://images.unsplash.com/photo-1496307042754-b4aa456c4a2d"
    elif "snow" in desc:
        return "❄️", "https://images.unsplash.com/photo-1608889175110-8a7a4f675ea4"
    elif "storm" in desc or "thunder" in desc:
        return "⛈️", "https://images.unsplash.com/photo-1500674425229-f692875b0ab7"
    elif "mist" in desc or "fog" in desc:
        return "🌫️", "https://images.unsplash.com/photo-1527766833261-b09c3163a791"
    else:
        return "🌡️", "https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0"

def set_background(url):
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background: url('{url}') no-repeat center center fixed;
            background-size: cover;
        }}
        .block-container {{
            background-color: rgba(255, 255, 255, 0.88);
            border-radius: 12px;
            padding: 2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Main App
st.set_page_config("Weather App", layout="centered")
st.title("🌦️ Live Weather Forecast")

auto_city, lat, lon = get_user_location()
city = st.text_input("Enter city (or leave blank to auto-detect)", value=auto_city)

if city:
    if city != auto_city:
        lat, lon = get_coordinates(city)

    if lat and lon:
        current = get_current_weather(lat, lon)
        hourly, forecast = get_forecast(lat, lon)

        temp = current["main"]["temp"]
        feels_like = current["main"]["feels_like"]
        desc = current["weather"][0]["description"].capitalize()
        humidity = current["main"]["humidity"]
        wind = current["wind"]["speed"]
        timezone_offset = current["timezone"]
        dt_local = datetime.utcfromtimestamp(current["dt"] + timezone_offset).strftime('%Y-%m-%d %H:%M:%S')

        icon, bg_url = get_weather_theme(desc)
        set_background(bg_url)

        # Current Weather
        st.subheader(f"📍 {city}")
        st.markdown(f"**{icon} {desc}**")
        st.markdown(f"🕒 Local Time: `{dt_local}`")
        st.markdown(f"🌡️ Temperature: `{temp}°C`")
        st.markdown(f"🤒 Feels Like: `{feels_like}°C`")
        st.markdown(f"💧 Humidity: `{humidity}%`")
        st.markdown(f"🌬️ Wind Speed: `{wind} m/s`")

        # Forecast
        st.markdown("---")
        st.subheader("📅 5-Day Forecast")
        for day in forecast[:5]:
            date = datetime.strptime(day["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%A, %b %d")
            d_temp = day["main"]["temp"]
            d_desc = day["weather"][0]["description"].capitalize()
            d_icon, _ = get_weather_theme(d_desc)
            st.markdown(f"**{date}**: {d_icon} `{d_temp}°C`, {d_desc}")

        # Temperature Trend Chart
        forecast_data = {
            "Date": [datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%a") for item in forecast[:5]],
            "Temp": [item["main"]["temp"] for item in forecast[:5]]
        }
        df = pd.DataFrame(forecast_data)

        st.subheader("📊 Temperature Trend (Next 5 Days)")
        fig = px.line(df, x="Date", y="Temp", markers=True, line_shape="spline")
        fig.update_layout(yaxis_title="Temperature (°C)", xaxis_title="Day")
        st.plotly_chart(fig, use_container_width=True)

        # Hourly Forecast
        st.subheader("⏰ Hourly Forecast (Next 12 Hours)")
        for entry in hourly[:4]:
            time = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
            h_temp = entry["main"]["temp"]
            h_desc = entry["weather"][0]["description"].capitalize()
            h_icon, _ = get_weather_theme(h_desc)
            st.markdown(f"**{time}** - {h_icon} `{h_temp}°C`, {h_desc}")

    else:
        st.error("Could not retrieve coordinates for that city.")
