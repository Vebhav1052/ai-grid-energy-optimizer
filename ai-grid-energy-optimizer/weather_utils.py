"""
weather_utils.py - Weather API Integration Module

This module provides automatic weather data fetching from OpenWeatherMap API.
Fetches real-time temperature, humidity, and cloud cover data by city name.

Usage:
    from weather_utils import get_weather_data
    
    weather = get_weather_data("London")
    if weather:
        print(weather["temperature"])  # 15.5
        print(weather["humidity"])     # 65
        print(weather["cloud_cover"])  # 40
"""

import requests
import os
from typing import Dict, Optional

# OpenWeatherMap API configuration
# Sign up free at: https://openweathermap.org/api
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "demo")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Alternative: Using Open-Meteo API (no API key required)
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_data(city: str, use_openmeteo: bool = True) -> Optional[Dict]:
    """
    Fetch real-time weather data for a given city.
    
    This function automatically retrieves:
    - Temperature (in Celsius)
    - Humidity (0-100%)
    - Cloud Cover (0-100%)
    
    Args:
        city (str): City name (e.g., "London", "New York", "Tokyo")
        use_openmeteo (bool): Use Open-Meteo API (free, no key) vs OpenWeatherMap (requires key)
    
    Returns:
        Dict: Weather data with keys:
            - temperature: float (°C)
            - humidity: int (0-100%)
            - cloud_cover: int (0-100%)
            - city: str (city name)
            - country: str (country code)
        
        None: If API call fails
    
    Example:
        >>> weather = get_weather_data("London")
        >>> if weather:
        ...     print(f"Temp: {weather['temperature']}°C")
        ...     print(f"Humidity: {weather['humidity']}%")
        ...     print(f"Cloud Cover: {weather['cloud_cover']}%")
    """
    if use_openmeteo:
        return _get_weather_openmeteo(city)
    else:
        return _get_weather_openweathermap(city)


def _get_weather_openmeteo(city: str) -> Optional[Dict]:
    """
    Fetch weather using Open-Meteo API (free, no API key required).
    
    Open-Meteo provides free weather data without requiring authentication.
    This is recommended for hackathons and development.
    
    API Documentation: https://open-meteo.com/en
    """
    try:
        # Step 1: Get coordinates from city name using geocoding API
        geocoding_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        
        geo_response = requests.get(
            OPEN_METEO_GEOCODING_URL,
            params=geocoding_params,
            timeout=5
        )
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            print(f"❌ City not found: {city}")
            return None
        
        # Extract coordinates
        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")
        
        # Step 2: Get weather data using coordinates
        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,cloud_cover",
            "temperature_unit": "celsius"
        }
        
        weather_response = requests.get(
            OPEN_METEO_WEATHER_URL,
            params=weather_params,
            timeout=5
        )
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Extract current weather
        current = weather_data.get("current", {})
        
        return {
            "temperature": float(current.get("temperature_2m", 20.0)),
            "humidity": int(current.get("relative_humidity_2m", 50)),
            "cloud_cover": int(current.get("cloud_cover", 25)),
            "city": city_name,
            "country": country,
            "source": "open-meteo",
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            }
        }
    
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout: API request took too long for {city}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🌐 Connection error: Unable to reach weather API for {city}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"🚨 HTTP error: {e.response.status_code}")
        return None
    except (KeyError, ValueError) as e:
        print(f"⚠️ Data parsing error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error fetching weather for {city}: {str(e)}")
        return None


def _get_weather_openweathermap(city: str) -> Optional[Dict]:
    """
    Fetch weather using OpenWeatherMap API (requires API key).
    
    Requires a free API key from: https://openweathermap.org/api
    Set environment variable: OPENWEATHER_API_KEY
    
    This method is more feature-rich but requires registration.
    """
    if OPENWEATHER_API_KEY == "demo":
        print("⚠️ OpenWeatherMap API key not set.")
        print("   Set OPENWEATHER_API_KEY environment variable or use Open-Meteo (free)")
        return None
    
    try:
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Use Celsius
        }
        
        response = requests.get(
            OPENWEATHER_BASE_URL,
            params=params,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "temperature": float(data.get("main", {}).get("temp", 20.0)),
            "humidity": int(data.get("main", {}).get("humidity", 50)),
            "cloud_cover": int(data.get("clouds", {}).get("all", 25)),
            "city": data.get("name", city),
            "country": data.get("sys", {}).get("country", ""),
            "source": "openweathermap",
            "coordinates": {
                "latitude": data.get("coord", {}).get("lat"),
                "longitude": data.get("coord", {}).get("lon")
            }
        }
    
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout: OpenWeatherMap took too long for {city}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"🌐 Connection error: Unable to reach OpenWeatherMap")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ City not found: {city}")
        elif e.response.status_code == 401:
            print(f"🔑 Invalid API key")
        else:
            print(f"🚨 HTTP error: {e.response.status_code}")
        return None
    except (KeyError, ValueError) as e:
        print(f"⚠️ Data parsing error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None


def validate_weather_data(weather: Dict) -> bool:
    """
    Validate weather data dictionary.
    
    Args:
        weather (Dict): Weather data to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_keys = {"temperature", "humidity", "cloud_cover"}
    
    if not isinstance(weather, dict):
        return False
    
    if not required_keys.issubset(weather.keys()):
        return False
    
    # Validate value ranges
    try:
        temp = float(weather["temperature"])
        humidity = int(weather["humidity"])
        cloud = int(weather["cloud_cover"])
        
        # Reasonable ranges for Earth
        if not (-60 <= temp <= 60):  # -60°C to +60°C
            return False
        if not (0 <= humidity <= 100):
            return False
        if not (0 <= cloud <= 100):
            return False
        
        return True
    except (ValueError, TypeError):
        return False


# ============================================================================
# DEMO & TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🌍 Weather Data Integration - Testing")
    print("=" * 70)
    
    test_cities = ["London", "New York", "Tokyo", "Sydney", "Paris"]
    
    print("\n🔍 Fetching weather for test cities...\n")
    
    for city in test_cities:
        print(f"📍 {city}:")
        weather = get_weather_data(city)
        
        if weather:
            print(f"   ✅ Temperature: {weather['temperature']}°C")
            print(f"      Humidity: {weather['humidity']}%")
            print(f"      Cloud Cover: {weather['cloud_cover']}%")
            print(f"      Location: {weather['city']}, {weather['country']}")
            
            if validate_weather_data(weather):
                print(f"      ✅ Data validation: PASSED\n")
            else:
                print(f"      ⚠️  Data validation: FAILED\n")
        else:
            print(f"   ❌ Failed to fetch data\n")
    
    print("=" * 70)
    print("✅ Weather Integration Test Complete")
    print("=" * 70)
