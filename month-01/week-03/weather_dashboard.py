import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "https://api.openweathermap.org/data/2.5"
CACHE_DIR = Path("weather_cache")
CACHE_EXPIRY_MINUTES = 30


class WeatherAPIClient:
    """
    Handles HTTP communication with the OpenWeatherMap API and manages JSON caching.
    """

    def __init__(self, api_key: str, cache_dir: Path = CACHE_DIR):
        """
        Initialize the API client with an API key and cache directory.

        Args:
            api_key: The OpenWeatherMap API key.
            cache_dir: Directory to store cached JSON files.
        """
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_current(self, city: str) -> Dict:
        """
        Fetch current weather for a city, checking the cache first.

        Args:
            city: Name of the city.

        Returns:
            Dictionary containing current weather data.

        Raises:
            ValueError: If the API key is missing.
            requests.HTTPError: For specific API errors (404, 429, etc.).
            ConnectionError: For network failures.
        """
        endpoint = "/weather"
        params = {"q": city, "appid": self.api_key, "units": "imperial"}
        return self._make_request(endpoint, params)

    def get_forecast(self, city: str) -> Dict:
        """
        Fetch a 5-day forecast for a city, checking the cache first.

        Args:
            city: Name of the city.

        Returns:
            Dictionary containing forecast data.
        """
        endpoint = "/forecast"
        params = {"q": city, "appid": self.api_key, "units": "imperial"}
        return self._make_request(endpoint, params)

    def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """
        Execute an HTTP request with error handling and cache logic.

        Args:
            endpoint: The API endpoint path (e.g., '/weather').
            params: Query parameters for the request.

        Returns:
            The JSON response from the API.

        Raises:
            ValueError: If the API key is missing.
            requests.HTTPError: For API errors.
            ConnectionError: For network failures.
        """
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is missing. Set OPENWEATHER_API_KEY environment variable.")

        url = f"{BASE_URL}{endpoint}"
        cache_key = self._get_cache_key(endpoint, params)

        # Check cache first
        cached_data = self._get_cache(cache_key)
        if cached_data:
            logger.info(f"Cache hit for {cache_key}")
            return cached_data

        # Make API request
        try:
            logger.info(f"Fetching data from API for {cache_key}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
            return response.json()

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"City not found: {params.get('q')}")
                raise requests.HTTPError("City not found") from e
            elif e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After", "1")
                logger.error(f"Rate limit exceeded. Please wait {retry_after} minutes.")
                raise requests.HTTPError(f"Rate limit exceeded. Retry after {retry_after} minutes.") from e
            else:
                logger.error(f"API Error: {e}")
                raise

        except requests.ConnectionError:
            logger.error("Network failure. Unable to connect to API.")
            raise ConnectionError("Network failure. Check your internet connection.")

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """
        Generate a unique cache key based on city and endpoint.

        Args:
            endpoint: The API endpoint path.
            params: Query parameters.

        Returns:
            A string hash representing the cache key.
        """
        city = params.get("q", "")
        return f"{city}_{endpoint.replace('/', '_')}"

    def _get_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached data if it exists and is fresh.

        Args:
            cache_key: The unique identifier for the cache entry.

        Returns:
            Cached data dictionary if fresh, None otherwise.
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            # Check if cache is fresh (less than 30 minutes old)
            if datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime) < timedelta(minutes=CACHE_EXPIRY_MINUTES):
                return data
            else:
                logger.debug(f"Cache expired for {cache_key}")
                return None
        except (json.JSONDecodeError, OSError):
            return None

    def _set_cache(self, cache_key: str, data: Dict) -> None:
        """
        Save response data to a cache file.

        Args:
            cache_key: The unique identifier for the cache entry.
            data: The data dictionary to cache.
        """
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(data, f)
            logger.debug(f"Saved to cache: {cache_key}")
        except OSError as e:
            logger.warning(f"Failed to write cache file: {e}")


@dataclass
class WeatherData:
    """
    Dataclass representing parsed current weather information.
    """
    city: str
    country: str
    temperature: float  # °F
    feels_like: float
    humidity: int
    pressure: int
    visibility: int
    dew_point: float
    cloudiness: int
    wind_speed: float
    conditions: str
    icon_code: str
    timestamp: datetime

    @property
    def temperature_c(self) -> float:
        """Convert temperature to Celsius."""
        return (self.temperature - 32) * 5 / 9

    @property
    def wind_description(self) -> str:
        """Return a human-readable wind description."""
        speed = self.wind_speed
        if speed < 4:
            return "Light breeze"
        elif speed < 11:
            return "Moderate breeze"
        elif speed < 19:
            return "Strong breeze"
        elif speed < 29:
            return "High wind"
        else:
            return "Stormy"


@dataclass
class ForecastDay:
    """
    Dataclass representing a single day in the forecast.
    """
    date: datetime
    high_temp: float  # °F
    low_temp: float
    conditions: str
    precipitation_chance: int  # %
    pressure: int
    visibility: int
    dew_point: float
    cloudiness: int


class WeatherAnalyzer:
    """
    Processes weather data to generate summaries and trends.
    """

    def summarize_forecast(self, forecast_days: List[ForecastDay]) -> Dict:
        """
        Generate a summary of the forecast including stats.

        Args:
            forecast_days: List of ForecastDay objects.

        Returns:
            Dictionary containing summary statistics.
        """
        if not forecast_days:
            return {}

        temps = [day.high_temp for day in forecast_days]
        avg_temp = sum(temps) / len(temps)
        avg_precip = sum(day.precipitation_chance for day in forecast_days) / len(forecast_days)
        best_day = self.get_best_day(forecast_days)
        worst_day = self.get_worst_day(forecast_days)

        return {
            "average_high_temp": round(avg_temp, 1),
            "average_precipitation": round(avg_precip, 1),
            "best_day": best_day.date.strftime("%Y-%m-%d"),
            "best_day_conditions": best_day.conditions,
            "worst_day": worst_day.date.strftime("%Y-%m-%d"),
            "worst_day_conditions": worst_day.conditions
        }

    def get_trend(self, forecast_days: List[ForecastDay]) -> str:
        """
        Determine if the forecast is warming, cooling, or stable.

        Args:
            forecast_days: List of ForecastDay objects.

        Returns:
            String: "warming", "cooling", or "stable".
        """
        if len(forecast_days) < 2:
            return "stable"

        highs = [day.high_temp for day in forecast_days]
        # Compare first day high with last day high
        change = highs[-1] - highs[0]

        if change > 1.0:
            return "warming"
        elif change < -1.0:
            return "cooling"
        else:
            return "stable"

    def get_best_day(self, forecast_days: List[ForecastDay]) -> ForecastDay:
        """
        Identify the day with the best weather conditions.

        Args:
            forecast_days: List of ForecastDay objects.

        Returns:
            ForecastDay object representing the best day.
        """
        if not forecast_days:
            return ForecastDay(datetime.now(), 0, 0, "", 0, 0, 0, 0, 0)

        # Simple heuristic: Highest temperature, lowest precipitation, lowest cloudiness
        def score(day: ForecastDay) -> float:
            return (day.high_temp * 0.5) - (day.precipitation_chance * 0.3) - (day.cloudiness * 0.1)

        return max(forecast_days, key=score)

    def get_worst_day(self, forecast_days: List[ForecastDay]) -> ForecastDay:
        """
        Identify the day with the worst weather conditions.

        Args:
            forecast_days: List of ForecastDay objects.

        Returns:
            ForecastDay object representing the worst day.
        """
        if not forecast_days:
            return ForecastDay(datetime.now(), 0, 0, "", 0, 0, 0, 0, 0)

        # Simple heuristic: Lowest temperature, highest precipitation, highest cloudiness
        def score(day: ForecastDay) -> float:
            return (day.low_temp * 0.5) + (day.precipitation_chance * 0.4) + (day.cloudiness * 0.1)

        return min(forecast_days, key=score)


class WeatherDisplay:
    """
    Formats and displays weather data in a terminal UI.
    """

    def __init__(self):
        """Initialize the display formatter."""
        pass

    def show_current(self, weather: WeatherData) -> None:
        """
        Display current weather conditions.

        Args:
            weather: WeatherData object.
        """
        print("\n" + "=" * 40)
        print(f"Current Weather in {weather.city}, {weather.country}")
        print("=" * 40)
        print(f"Temperature:    {weather.temperature:.1f}°F ({weather.temperature_c:.1f}°C)")
        print(f"Feels Like:     {weather.feels_like:.1f}°F")
        print(f"Conditions:     {weather.conditions}")
        print(f"Wind:           {weather.wind_speed:.1f} mph - {weather.wind_description}")
        print(f"Humidity:       {weather.humidity}%")
        print(f"Pressure:       {weather.pressure} hPa")
        print(f"Visibility:     {weather.visibility / 1609.34:.1f} miles")
        print(f"Dew Point:      {weather.dew_point:.1f}°F")
        print(f"Cloudiness:     {weather.cloudiness}%")
        print("=" * 40 + "\n")

    def show_forecast(self, days: List[ForecastDay]) -> None:
        """
        Display a formatted 5-day forecast table.

        Args:
            days: List of ForecastDay objects.
        """
        print("\n" + "=" * 80)
        print("5-DAY FORECAST")
        print("=" * 80)
        print(f"{'Date':<12} {'High/Low':<15} {'Conditions':<20} {'Precip':<10} {'Wind':<15}")
        print("-" * 80)

        for day in days:
            date_str = day.date.strftime("%Y-%m-%d")
            temp_str = f"{day.high_temp:.1f}° / {day.low_temp:.1f}°"
            print(f"{date_str:<12} {temp_str:<15} {day.conditions:<20} {day.precipitation_chance:<10}% {day.wind_speed:.1f} mph")

        print("=" * 80 + "\n")

    def show_summary(self, summary: Dict) -> None:
        """
        Display a weekly analysis summary.

        Args:
            summary: Dictionary containing summary statistics.
        """
        print("\n" + "=" * 40)
        print("FORECAST SUMMARY")
        print("=" * 40)
        print(f"Trend:          {summary.get('trend', 'N/A')}")
        print(f"Avg High Temp:  {summary.get('average_high_temp', 'N/A')}°F")
        print(f"Avg Precip:     {summary.get('average_precipitation', 'N/A')}%")
        print(f"Best Day:       {summary.get('best_day', 'N/A')} ({summary.get('best_day_conditions', 'N/A')})")
        print(f"Worst Day:      {summary.get('worst_day', 'N/A')} ({summary.get('worst_day_conditions', 'N/A')})")
        print("=" * 40 + "\n")


def parse_current_weather(api_response: Dict) -> WeatherData:
    """
    Parse raw API response into a WeatherData dataclass.

    Args:
        api_response: Dictionary from API.

    Returns:
        WeatherData object.
    """
    main = api_response.get("main", {})
    weather = api_response.get("weather", [{}])[0]
    wind = api_response.get("wind", {})
    sys = api_response.get("sys", {})
    visibility_m = api_response.get("visibility", 0)

    return WeatherData(
        city=api_response.get("name", "Unknown"),
        country=sys.get("country", ""),
        temperature=main.get("temp"),
        feels_like=main.get("feels_like"),
        humidity=main.get("humidity"),
        pressure=main.get("pressure"),
        visibility=visibility_m,
        dew_point=main.get("dew_point"),
        cloudiness=weather.get("all", 0),
        wind_speed=wind.get("speed"),
        conditions=weather.get("description", "Clear").capitalize(),
        icon_code=weather.get("icon", ""),
        timestamp=datetime.fromtimestamp(api_response.get("dt", 0))
    )


def parse_forecast(api_response: Dict) -> List[ForecastDay]:
    """
    Parse raw API response into a list of ForecastDay dataclasses.

    Args:
        api_response: Dictionary from API.

    Returns:
        List of ForecastDay objects.
    """
    forecast_list = api_response.get("list", [])
    days = []

    for item in forecast_list:
        dt = datetime.fromtimestamp(item.get("dt", 0))
        main = item.get("main", {})
        weather = item.get("weather", [{}])[0]
        wind = item.get("wind", {})
        pop = item.get("pop", 0) * 100  # Convert probability to percentage

        day = ForecastDay(
            date=dt,
            high_temp=main.get("temp_max"),
            low_temp=main.get("temp_min"),
            conditions=weather.get("description", "Clear").capitalize(),
            precipitation_chance=pop,
            pressure=main.get("pressure"),
            visibility=item.get("visibility", 0),
            dew_point=main.get("dew_point"),
            cloudiness=weather.get("all", 0)
        )
        days.append(day)

    return days


def main():
    """
    Main entry point for the weather dashboard.
    """
    # Get API key from environment
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OPENWEATHER_API_KEY environment variable is not set.")
        return

    # Initialize components
    client = WeatherAPIClient(api_key)
    analyzer = WeatherAnalyzer()
    display = WeatherDisplay()

    # Get city input
    city = input("Enter city name: ").strip()
    if not city:
        print("City name cannot be empty.")
        return

    try:
        # Fetch Data
        current_data = client.get_current(city)
        forecast_data = client.get_forecast(city)

        # Parse Data
        current = parse_current_weather(current_data)
        forecast_days = parse_forecast(forecast_data)

        # Display Data
        display.show_current(current)
        display.show_forecast(forecast_days)

        # Analyze and Display Summary
        trend = analyzer.get_trend(forecast_days)
        summary = analyzer.summarize_forecast(forecast_days)
        summary["trend"] = trend
        display.show_summary(summary)

    except ValueError as e:
        print(f"Configuration Error: {e}")
    except requests.HTTPError as e:
        print(f"API Error: {e}")
    except ConnectionError:
        print("Network error. Could not fetch weather data.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()