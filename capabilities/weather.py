"""
Bosco Core - Weather Capability
Get weather information using OpenWeatherMap or other APIs
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any


class Weather:
    """Weather information provider"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENWEATHERMAP_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.default_city = "London"
        
        if not self.api_key:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
            if os.path.exists(config_path):
                try:
                    with open(config_path) as f:
                        config = json.load(f)
                        self.api_key = config.get("openweathermap_api_key", "")
                except:
                    pass
    
    def get_weather(self, city: str = None) -> Dict[str, Any]:
        """Get current weather for a city"""
        city = city or self.default_city
        
        if not self.api_key:
            return self._get_demo_weather(city)
        
        try:
            url = f"{self.base_url}/weather"
            params = {"q": city, "appid": self.api_key, "units": "metric"}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "wind_speed": data["wind"]["speed"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": data.get("message", "Unknown error")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_demo_weather(self, city: str) -> Dict[str, Any]:
        """Demo weather when no API key"""
        return {
            "success": True, "city": city, "country": "XX", "temperature": 20,
            "feels_like": 19, "humidity": 65, "description": "partly cloudy",
            "icon": "02d", "wind_speed": 3.5, "timestamp": datetime.now().isoformat(), "demo": True
        }
    
    def format_weather_response(self, data: Dict) -> str:
        """Format weather data as speech"""
        if not data.get("success"):
            return f"I couldn't retrieve weather. {data.get('error', '')}"
        
        temp = data["temperature"]
        feels = data["feels_like"]
        desc = data["description"]
        city = data["city"]
        
        return f"The weather in {city} is {desc}. Temperature is {temp} degrees, feels like {feels} degrees."


_weather = Weather()


def get_weather(city: str = None) -> Dict:
    return _weather.get_weather(city)


def format_weather_response(data: Dict) -> str:
    return _weather.format_weather_response(data)


if __name__ == "__main__":
    print("Testing Weather...")
    weather = get_weather("London")
    print(format_weather_response(weather))

