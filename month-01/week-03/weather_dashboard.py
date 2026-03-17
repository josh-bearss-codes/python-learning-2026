from dataclasses import dataclass
from typing import Optional
import time
from pathlib import Path
from typing import Optional
import requests
from dataclasses import dataclass
import json

@dataclass
class ForecastDay:
    """Represents a single day's forecast."""
    date: str
    high_temp: float
    low_temp: float
    conditions: str
    precipitation_chance: float


@dataclass
class WeatherData:
    """Represents current weather conditions for a location."""
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    conditions: str

class WeatherAPIClient:
    """Client for the OpenWeatherMap API with caching support."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str, cache_dir: Path):
        """Initialize the API client with an API key and cache directory.
        
        Args:
            api_key: OpenWeatherMap API key
            cache_dir: Directory to store cached responses
        """
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current(self, city: str) -> WeatherData:
        """Fetch current weather data for a city.
        
        Args:
            city: City name to fetch weather for
            
        Returns:
            WeatherData object with current conditions
            
        Raises:
            ConnectionError: If network request fails
            Timeout: If request times out
            RuntimeError: For API errors (401, 404, 429, etc.)
        """
        cache_key = f"current_{city.lower().replace(' ', '_')}"
        
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return self._parse_weather_data(cached_data)
        
        params = {"q": city, "appid": self.api_key, "units": "imperial"}
        response = self._make_request("/weather", params)
        
        self._set_cache(cache_key, response)
        return self._parse_weather_data(response)
    
    def get_forecast(self, city: str) -> list[ForecastDay]:
        """Fetch 5-day forecast data for a city.
        
        Args:
            city: City name to fetch forecast for
            
        Returns:
            List of ForecastDay objects
            
        Raises:
            ConnectionError: If network request fails
            Timeout: If request times out
            RuntimeError: For API errors (401, 404, 429, etc.)
        """
        cache_key = f"forecast_{city.lower().replace(' ', '_')}"
        
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return self._parse_forecast_data(cached_data)
        
        params = {"q": city, "appid": self.api_key, "units": "imperial"}
        response = self._make_request("/forecast", params)
        
        self._set_cache(cache_key, response)
        return self._parse_forecast_data(response)
    
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make a request to the OpenWeatherMap API.
        
        Args:
            endpoint: API endpoint path (e.g., '/weather')
            params: Query parameters including API key
            
        Returns:
            JSON response as dictionary
            
        Raises:
            ConnectionError: If network request fails
            Timeout: If request times out
            RuntimeError: For HTTP errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        params.setdefault("appid", self.api_key)
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Network error: {e}") from e
        except requests.exceptions.Timeout as e:
            raise Timeout(f"Request timed out: {e}") from e
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise RuntimeError(f"City not found: {e}") from e
            elif e.response.status_code == 401:
                raise RuntimeError(f"Invalid API key: {e}") from e
            elif e.response.status_code == 429:
                raise RuntimeError(f"Rate limit exceeded: {e}") from e
            else:
                raise RuntimeError(f"HTTP error {e.response.status_code}: {e}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON response: {e}") from e
    
    def _get_cache(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached data if fresh (less than 30 minutes old).
        
        Args:
            cache_key: Key to identify the cache file
            
        Returns:
            Cached data dictionary or None if cache is stale/missing
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
            
            cache_time = cache_data.get("_cache_time", 0)
            if time.time() - cache_time < 1800:  # 30 minutes = 1800 seconds
                return cache_data
            return None
        except (json.JSONDecodeError, IOError):
            return None
    
    def _set_cache(self, cache_key: str, data: dict) -> None:
        """Store data in cache with timestamp.
        
        Args:
            cache_key: Key to identify the cache file
            data: Data to cache
        """
        cache_data = {**data, "_cache_time": time.time()}
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        with open(cache_file, "w") as f:
            json.dump(cache_data, f)
    
    def _parse_weather_data(self, data: dict) -> WeatherData:
        """Parse API response into WeatherData dataclass.
        
        Args:
            data: Raw API response dictionary
            
        Returns:
            WeatherData object
        """
        return WeatherData(
            city=data.get("name", ""),
            country=data.get("sys", {}).get("country", ""),
            temperature=data.get("main", {}).get("temp", 0.0),
            feels_like=data.get("main", {}).get("feels_like", 0.0),
            humidity=data.get("main", {}).get("humidity", 0),
            wind_speed=data.get("wind", {}).get("speed", 0.0),
            conditions=data.get("weather", [{}])[0].get("description", ""),
            icon_code=data.get("weather", [{}])[0].get("icon", ""),
            timestamp=data.get("dt", "")
        )
    
    def _parse_forecast_data(self, data: dict) -> list[ForecastDay]:
        """Parse API forecast response into list of ForecastDay.
        
        Args:
            data: Raw API response dictionary
            
        Returns:
            List of ForecastDay objects
        """
        forecast_days = []
        daily_data = {}
        
        for entry in data.get("list", []):
            date = entry.get("dt_txt", "")[:10]  # Extract YYYY-MM-DD
            
            if date not in daily_data:
                daily_data[date] = {
                    "high": float("-inf"),
                    "low": float("inf"),
                    "conditions": "",
                    "precipitation": 0.0
                }
            
            temp = entry.get("main", {}).get("temp", 0)
            daily_data[date]["high"] = max(daily_data[date]["high"], temp)
            daily_data[date]["low"] = min(daily_data[date]["low"], temp)
            
            weather = entry.get("weather", [{}])[0]
            if weather.get("description"):
                daily_data[date]["conditions"] = weather.get("description")
            
            # Get precipitation if available
            daily_data[date]["precipitation"] += entry.get("pop", 0)
        
        for date, info in daily_data.items():
            forecast_days.append(ForecastDay(
                date=date,
                high_temp=info["high"],
                low_temp=info["low"],
                conditions=info["conditions"],
                precipitation_chance=info["precipitation"]
            ))
        
        return forecast_days
    icon_code: str
    timestamp: str

    @property
    def temperature_c(self) -> float:
        """Converts Fahrenheit temperature to Celsius."""
        return round((self.temperature - 32) * 5 / 9, 2)

    @property
    def wind_description(self) -> str:
        """Returns a descriptive term for the wind speed."""
        if self.wind_speed < 4:
            return "Light breeze"
        elif self.wind_speed < 12:
            return "Moderate"
        elif self.wind_speed < 25:
            return "Strong"
        else:
            return "High"