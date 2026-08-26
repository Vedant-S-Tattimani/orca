"""
Open-Meteo Weather API client for ORCA
Handles weather forecasts, temperature, wind, precipitation, etc.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class OpenMeteoWeatherClient(BaseAPIClient):
    """
    Client for Open-Meteo Weather API
    Fetches weather data including temperature, wind, precipitation, etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,  # Open-Meteo does not require an API key
        base_url: str = "https://api.open-meteo.com/v1/forecast",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Open-Meteo Weather API client

        Args:
            api_key: Not used for Open-Meteo (kept for interface consistency)
            base_url: Base URL for Open-Meteo Weather API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
        self.logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)

    async def get_weather_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            forecast_days: Number of forecast days (1-16)
            hourly: List of hourly variables to fetch
            daily: List of daily variables to fetch

        Returns:
            Weather forecast data
        """
        # Default hourly and daily variables if not specified
        if hourly is None:
            hourly = [
                "temperature_2m",
                "relative_humidity_2m",
                "dew_point_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "snowfall",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m"
            ]
        if daily is None:
            daily = [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "sunrise",
                "sunset",
                "precipitation_sum",
                "rain_sum",
                "snowfall_sum",
                "precipitation_hours",
                "wind_speed_10m_max",
                "wind_direction_10m_dominant"
            ]

        endpoint = ""  # The base URL already includes the endpoint
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(hourly),
            "daily": ",".join(daily),
            "forecast_days": forecast_days,
            "timezone": "auto"
        }

        try:
            self.logger.info(f"Fetching Open-Meteo weather forecast for ({latitude}, {longitude})")
            response = await self.get(endpoint, params=params)
            return self._parse_weather_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching Open-Meteo weather forecast: {str(e)}")
            raise

    def _parse_weather_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse Open-Meteo weather response into standardized format

        Args:
            raw_data: Raw response from Open-Meteo API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed weather data in ORCA standard format
        """
        parsed = {
            "agent": "weather",
            "source": "Open-Meteo",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.9  # High confidence for Open-Meteo data
        }

        # Extract current weather (first hourly entry) if available
        if "hourly" in raw_data and raw_data["hourly"]:
            hourly_data = raw_data["hourly"]
            # Get the most recent hour (index 0)
            if "temperature_2m" in hourly_data and len(hourly_data["temperature_2m"]) > 0:
                parsed["temperature_c"] = float(hourly_data["temperature_2m"][0])
            if "relative_humidity_2m" in hourly_data and len(hourly_data["relative_humidity_2m"]) > 0:
                parsed["humidity_percent"] = float(hourly_data["relative_humidity_2m"][0])
            if "precipitation" in hourly_data and len(hourly_data["precipitation"]) > 0:
                parsed["rainfall_mm"] = float(hourly_data["precipitation"][0])  # mm/hour
            if "wind_speed_10m" in hourly_data and len(hourly_data["wind_speed_10m"]) > 0:
                parsed["wind_speed_kmh"] = float(hourly_data["wind_speed_10m"][0]) * 3.6  # m/s to km/h
            if "wind_direction_10m" in hourly_data and len(hourly_data["wind_direction_10m"]) > 0:
                parsed["wind_direction_deg"] = float(hourly_data["wind_direction_10m"][0])
            if "weather_code" in hourly_data and len(hourly_data["weather_code"]) > 0:
                parsed["weather_code"] = int(hourly_data["weather_code"][0])
                # We can map weather_code to a description if needed
                parsed["weather_condition"] = self._weather_code_to_description(hourly_data["weather_code"][0])

            # Extract next 24 hours of forecast for graphs
            forecast_24h = []
            if "time" in hourly_data:
                for i in range(min(24, len(hourly_data["time"]))):
                    forecast_24h.append({
                        "time": hourly_data["time"][i],
                        "temperature_c": float(hourly_data["temperature_2m"][i]) if "temperature_2m" in hourly_data and len(hourly_data["temperature_2m"]) > i else None,
                        "wind_speed_kmh": float(hourly_data["wind_speed_10m"][i]) * 3.6 if "wind_speed_10m" in hourly_data and len(hourly_data["wind_speed_10m"]) > i else None,
                        "wind_direction_deg": float(hourly_data["wind_direction_10m"][i]) if "wind_direction_10m" in hourly_data and len(hourly_data["wind_direction_10m"]) > i else None,
                    })
            parsed["forecast_24h"] = forecast_24h

        # Extract daily forecast summary (today)
        if "daily" in raw_data and raw_data["daily"]:
            daily_data = raw_data["daily"]
            if "temperature_2m_max" in daily_data and len(daily_data["temperature_2m_max"]) > 0:
                parsed["temperature_max_c"] = float(daily_data["temperature_2m_max"][0])
            if "temperature_2m_min" in daily_data and len(daily_data["temperature_2m_min"]) > 0:
                parsed["temperature_min_c"] = float(daily_data["temperature_2m_min"][0])
            if "precipitation_sum" in daily_data and len(daily_data["precipitation_sum"]) > 0:
                parsed["precipitation_sum_mm"] = float(daily_data["precipitation_sum"][0])
            if "wind_speed_10m_max" in daily_data and len(daily_data["wind_speed_10m_max"]) > 0:
                parsed["wind_speed_max_kmh"] = float(daily_data["wind_speed_10m_max"][0]) * 3.6

        # Set forecast hours (default to 7 days * 24 hours)
        parsed["forecast_hours"] = 7 * 24

        return parsed

    def _weather_code_to_description(self, code: int) -> str:
        """
        Convert Open-Meteo weather code to a description
        Based on: https://open-meteo.com/en/docs#weathercode
        """
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(code, "Unknown")

    async def health_check(self) -> bool:
        """
        Check if Open-Meteo service is accessible

        Returns:
            True if service is responsive, False otherwise
        """
        try:
            # Try a simple request for a known location (e.g., Greenwich)
            await self.get("", params={
                "latitude": 51.48,
                "longitude": 0.0,
                "hourly": "temperature_2m",
                "forecast_days": 1
            })
            return True
        except Exception as e:
            self.logger.warning(f"Open-Meteo health check failed: {str(e)}")
            return False