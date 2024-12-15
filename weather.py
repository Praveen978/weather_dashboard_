import pandas as pd
import streamlit as st
import requests
from datetime import datetime
import plotly.graph_objects as go

# API Keys
WEATHER_API_KEY = "c636a75a96c74aeced3f5b2e0f056787"
GEOCODE_API_KEY = "2a8c929f9c434f978fda64e8027ea1c2"

# Icons for better UI
WEATHER_ICONS = {
    "clear sky": "☀️",
    "few clouds": "🌤️",
    "scattered clouds": "⛅",
    "broken clouds": "☁️",
    "shower rain": "🌧️",
    "rain": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️"
}

# Helper Functions
def get_coordinates(api_key, location):
    """Get latitude and longitude for a given location."""
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    complete_url = f"{base_url}?q={location},India&key={api_key}"
    
    response = requests.get(complete_url)
    data = response.json()
    if response.status_code == 200 and data['results']:
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return lat, lng
    st.error("Error retrieving coordinates. Please check the location.")
    return None, None

def get_weather(lat, lng):
    """Get current weather data."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(complete_url)
    if response.status_code == 200:
        return response.json()
    st.error("Error retrieving current weather data.")
    return None

def get_forecast(lat, lng):
    """Get 5-day weather forecast."""
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    complete_url = f"{base_url}?lat={lat}&lon={lng}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(complete_url)
    if response.status_code == 200:
        return response.json()
    st.error("Error retrieving forecast data.")
    return None

def summarize_forecast(forecast_data):
    """Summarize the forecast data into daily averages."""
    forecast_list = forecast_data['list']
    df = pd.DataFrame([{
        'date': datetime.fromtimestamp(item['dt']).date(),
        'temp': item['main']['temp'],
        'description': item['weather'][0]['description']
    } for item in forecast_list])
    summary = df.groupby('date').agg(
        avg_temp=('temp', 'mean'),
        condition=('description', lambda x: x.mode()[0])
    ).reset_index()
    return summary

# Display Functions
def display_current_weather(weather_data):
    """Display current weather with icons."""
    st.subheader("🌍 Current Weather")
    weather_main = weather_data['weather'][0]['description']
    icon = WEATHER_ICONS.get(weather_main, "🌦️")
    st.markdown(f"### {icon} {weather_main.capitalize()}")
    st.write(f"**Temperature:** {weather_data['main']['temp']}°C (Feels like {weather_data['main']['feels_like']}°C)")
    st.write(f"**Humidity:** {weather_data['main']['humidity']}%")
    st.write(f"**Pressure:** {weather_data['main']['pressure']} hPa")
    st.write(f"**Wind Speed:** {weather_data['wind']['speed']} m/s")
    st.write(f"**Sunrise:** {datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M')}")
    st.write(f"**Sunset:** {datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')}")

def display_forecast_summary(summary):
    """Display the 5-day weather forecast."""
    st.subheader("📅 5-Day Weather Forecast")
    for _, row in summary.iterrows():
        icon = WEATHER_ICONS.get(row['condition'], "🌦️")
        st.markdown(f"**{row['date'].strftime('%A, %d %b')}**: {icon} {row['condition'].capitalize()}, Avg Temp: {row['avg_temp']:.1f}°C")

def display_lifestyle_tips(weather_data):
    """Provide lifestyle tips based on weather and air conditions."""
    humidity = weather_data['main']['humidity']
    st.subheader("💡 Lifestyle Tips")
    st.write("**General Recommendations:**")
    if humidity > 80:
        st.write("• Use oil-control products to prevent skin irritation.")
    if weather_data['main']['temp'] > 30:
        st.write("• Stay hydrated and avoid outdoor workouts during peak hours.")
    st.write("• Suitable for car washing and indoor activities.")

def display_trend_graphs(forecast_data):
    """Display enhanced temperature, humidity, and wind speed trends."""
    forecast_list = forecast_data['list']
    df = pd.DataFrame([{
        'datetime': datetime.fromtimestamp(item['dt']),
        'temp': item['main']['temp'],
        'humidity': item['main']['humidity'],
        'wind_speed': item['wind']['speed']
    } for item in forecast_list])

    # Enhanced Temperature Trend
    st.subheader("🌡️ Temperature Trend")
    fig_temp = go.Figure()

    # Line chart for temperature
    fig_temp.add_trace(go.Scatter(
        x=df['datetime'], 
        y=df['temp'], 
        mode='lines+markers', 
        line=dict(color='orange', width=2), 
        name="Temperature (°C)",
        text=[f"Temp: {t:.1f}°C" for t in df['temp']],
        hoverinfo="text+x"
    ))

    # Highlight max and min temperature
    max_temp = df['temp'].max()
    min_temp = df['temp'].min()
    fig_temp.add_annotation(
        x=df['datetime'][df['temp'].idxmax()], 
        y=max_temp, 
        text=f"🔥 Max: {max_temp:.1f}°C", 
        showarrow=True, arrowhead=2, bgcolor="red", font=dict(color="white")
    )
    fig_temp.add_annotation(
        x=df['datetime'][df['temp'].idxmin()], 
        y=min_temp, 
        text=f"❄️ Min: {min_temp:.1f}°C", 
        showarrow=True, arrowhead=2, bgcolor="blue", font=dict(color="white")
    )

    # Style layout
    fig_temp.update_layout(
        title="Temperature Trend (Next 5 Days)",
        xaxis_title="Date-Time",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    # Enhanced Humidity Trend
    st.subheader("💧 Humidity Trend")
    fig_humidity = go.Figure()
    fig_humidity.add_trace(go.Scatter(
        x=df['datetime'], 
        y=df['humidity'], 
        mode='lines+markers', 
        line=dict(color='blue', width=2), 
        name="Humidity (%)",
        text=[f"Humidity: {h:.1f}%" for h in df['humidity']],
        hoverinfo="text+x"
    ))

    # Highlight high humidity levels
    high_humidity = df['humidity'].max()
    fig_humidity.add_annotation(
        x=df['datetime'][df['humidity'].idxmax()],
        y=high_humidity,
        text=f"💧 High: {high_humidity:.1f}%",
        showarrow=True, arrowhead=2, bgcolor="blue", font=dict(color="white")
    )

    fig_humidity.update_layout(
        title="Humidity Trend (Next 5 Days)",
        xaxis_title="Date-Time",
        yaxis_title="Humidity (%)",
        template="plotly_white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )
    st.plotly_chart(fig_humidity, use_container_width=True)

    # Enhanced Wind Speed Trend
    st.subheader("💨 Wind Speed Trend")
    fig_wind = go.Figure()
    fig_wind.add_trace(go.Scatter(
        x=df['datetime'], 
        y=df['wind_speed'], 
        mode='lines+markers', 
        line=dict(color='green', width=2), 
        name="Wind Speed (m/s)",
        text=[f"Wind: {w:.1f} m/s" for w in df['wind_speed']],
        hoverinfo="text+x"
    ))

    # Highlight maximum wind speed
    max_wind = df['wind_speed'].max()
    fig_wind.add_annotation(
        x=df['datetime'][df['wind_speed'].idxmax()],
        y=max_wind,
        text=f"🌬️ Max: {max_wind:.1f} m/s",
        showarrow=True, arrowhead=2, bgcolor="green", font=dict(color="white")
    )

    fig_wind.update_layout(
        title="Wind Speed Trend (Next 5 Days)",
        xaxis_title="Date-Time",
        yaxis_title="Wind Speed (m/s)",
        template="plotly_white",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )
    st.plotly_chart(fig_wind, use_container_width=True)

def calculate_comfort_index(temp, humidity, wind_speed):
    """
    Calculates a comfort index on a scale of 0-10 based on weather conditions.
    Higher values indicate better comfort.
    """
    comfort = 10 - (abs(temp - 22) / 2) - (humidity / 20) - (wind_speed / 3)
    comfort = max(0, min(10, comfort))  # Ensure the index is between 0 and 10
    return round(comfort, 1)

def display_comfort_index(weather_data):
    """Display the comfort index."""
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    comfort_index = calculate_comfort_index(temp, humidity, wind_speed)

    st.subheader("🌟 Comfort Index")
    if comfort_index >= 8:
        st.success(f"Comfort Level: {comfort_index} / 10 😊 (Excellent)")
    elif comfort_index >= 5:
        st.info(f"Comfort Level: {comfort_index} / 10 🙂 (Moderate)")
    else:
        st.warning(f"Comfort Level: {comfort_index} / 10 😓 (Uncomfortable)")

def suggest_outdoor_activities(weather_data):
    """Suggest suitable outdoor activities based on current weather."""
    temp = weather_data['main']['temp']
    wind_speed = weather_data['wind']['speed']
    description = weather_data['weather'][0]['description']

    st.subheader("🚴 Outdoor Activity Suggestions")
    if "rain" in description or "shower" in description:
        st.write("☔ It's rainy. Indoor activities like reading or watching movies are recommended.")
    elif temp > 30:
        st.write("🌞 It's hot. Stay hydrated and avoid strenuous outdoor activities.")
    elif wind_speed > 8:
        st.write("💨 It's windy. Consider activities like kite flying or windsurfing.")
    else:
        st.write("🌳 Weather is perfect for a picnic, jogging, or cycling. Enjoy the outdoors!")

def display_clothing_suggestions(weather_data):
    """Provide clothing suggestions based on temperature and weather conditions."""
    temp = weather_data['main']['temp']
    description = weather_data['weather'][0]['description']

    st.subheader("👕 Clothing Suggestions")
    if temp < 15:
        st.write("🧥 It's cold. Wear warm clothes like jackets, sweaters, and scarves.")
    elif temp > 30:
        st.write("🩳 It's hot. Opt for light, breathable clothing like shorts and T-shirts.")
    elif "rain" in description or "shower" in description:
        st.write("☂️ It's rainy. Carry an umbrella and wear waterproof clothing.")
    else:
        st.write("👖 The weather is pleasant. Casual wear will be comfortable today.")

def display_health_advisory(weather_data):
    """Provide health advisories based on weather conditions."""
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']

    st.subheader("🩺 Health Advisory")
    if humidity > 80:
        st.write("💧 **High Humidity**: Stay cool and drink water. Avoid prolonged outdoor exposure.")
    if temp > 35:
        st.write("🌞 **Heat Advisory**: Use sunscreen and stay hydrated to avoid heat exhaustion.")
    if temp < 10:
        st.write("🥶 **Cold Advisory**: Wear layers to prevent cold-related illnesses.")
    st.write("🫁 For sensitive individuals, monitor air quality before outdoor activities.")


# Main App
def main():
    st.title("Weather Dashboard 🌤️")
    st.caption("Get real-time weather updates and 5-day forecasts for any city in India.")

    # User Input for Location
    location = st.text_input("Enter a location in India :")
    
    if location:
        lat, lng = get_coordinates(GEOCODE_API_KEY, location)
        if lat and lng:
            st.success(f"Location Coordinates: Latitude {lat}, Longitude {lng}")
            
            # Fetch and Display Current Weather
            with st.spinner("Fetching current weather..."):
                weather_data = get_weather(lat, lng)
                if weather_data:
                    display_current_weather(weather_data)  # Default current weather display
                    display_lifestyle_tips(weather_data)  # Lifestyle tips based on weather
                    display_comfort_index(weather_data)   # Unique Comfort Index
                    display_clothing_suggestions(weather_data)  # Clothing suggestions
                    display_health_advisory(weather_data)  # Health advisory based on weather conditions

            # Fetch and Display Forecast Data
            with st.spinner("Fetching 5-day forecast..."):
                forecast_data = get_forecast(lat, lng)
                if forecast_data:
                    summary = summarize_forecast(forecast_data)
                    display_forecast_summary(summary)  # Daily weather summary
                    display_trend_graphs(forecast_data)  # Temperature, Humidity, Wind trend # Daylight hours visualization # Weather alerts like storms or rain
                    suggest_outdoor_activities(weather_data)  # Activity suggestions for users
  # Add this line

if __name__ == "__main__":
    main()
