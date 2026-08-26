"""
Open-Meteo Marine Weather API client for ORCA
Handles marine forecasts, wave height, wave period, ocean currents, sea surface temperature, etc.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class OpenMeteoMarineClient(BaseAPIClient):
    """
    Client for Open-Meteo Marine Weather API
    Fetches marine data including wave height, wave period, ocean currents, sea surface temperature, etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,  # Open-Meteo does not require an API key
        base_url: str = "https://marine-api.open-meteo.com/v1/marine",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize Open-Meteo Marine Weather API client

        Args:
            api_key: Not used for Open-Meteo (kept for interface consistency)
            base_url: Base URL for Open-Meteo Marine API
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

    async def get_marine_forecast(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        hourly: Optional[List[str]] = None,
        daily: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get marine forecast for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            forecast_days: Number of forecast days (1-16)
            hourly: List of hourly variables to fetch
            daily: List of daily variables to fetch

        Returns:
            Marine forecast data
        """
        # Default hourly and daily variables for marine data if not specified
        # Based on Open-Meteo Marine API documentation: https://open-meteo.com/en/docs/marine-weather-api
        if hourly is None:
            hourly = [
                "wave_height",
                "wave_direction",
                "wave_period",
                "wind_wave_height",
                "wind_wave_direction",
                "wind_wave_period",
                "swell_wave_height",
                "swell_wave_direction",
                "swell_wave_period",
                "ocean_current_velocity",
                "ocean_current_direction",
                "sea_surface_temperature",
                "wind_speed_10m",
                "wind_direction_10m"
            ]
        if daily is None:
            daily = [
                "wave_height_max",
                "wave_direction_dominant",
                "wave_period_max",
                "wind_wave_height_max",
                "swell_wave_height_max",
                "sea_surface_temperature_max",
                "sea_surface_temperature_min",
                "wind_speed_10m_max"
                # Note: ocean_current_velocity_max is not available in marine API daily params
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
            self.logger.info(f"Fetching Open-Meteo marine forecast for ({latitude}, {longitude})")
            response = await self.get(endpoint, params=params)
            return self._parse_marine_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching Open-Meteo marine forecast: {str(e)}")
            raise

    def _parse_marine_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse Open-Meteo marine response into standardized format

        Args:
            raw_data: Raw response from Open-Meteo Marine API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed marine data in ORCA standard format
        """
        parsed = {
            "agent": "sea_state",
            "source": "Open-Meteo",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.9  # High confidence for Open-Meteo data
        }

        # Extract current marine conditions (first hourly entry) if available
        if "hourly" in raw_data and raw_data["hourly"]:
            hourly_data = raw_data["hourly"]
            # Get the most recent hour (index 0)
            if "wave_height" in hourly_data and len(hourly_data["wave_height"]) > 0:
                wave_height = hourly_data["wave_height"][0]
                if wave_height is not None:
                    parsed["wave_height_m"] = float(wave_height)
            if "wave_direction" in hourly_data and len(hourly_data["wave_direction"]) > 0:
                wave_direction = hourly_data["wave_direction"][0]
                if wave_direction is not None:
                    parsed["wave_direction_deg"] = float(wave_direction)
            if "wave_period" in hourly_data and len(hourly_data["wave_period"]) > 0:
                wave_period = hourly_data["wave_period"][0]
                if wave_period is not None:
                    parsed["wave_period_s"] = float(wave_period)
            if "wind_wave_height" in hourly_data and len(hourly_data["wind_wave_height"]) > 0:
                wind_wave_height = hourly_data["wind_wave_height"][0]
                if wind_wave_height is not None:
                    parsed["wind_wave_height_m"] = float(wind_wave_height)
            if "wind_wave_direction" in hourly_data and len(hourly_data["wind_wave_direction"]) > 0:
                wind_wave_direction = hourly_data["wind_wave_direction"][0]
                if wind_wave_direction is not None:
                    parsed["wind_wave_direction_deg"] = float(wind_wave_direction)
            if "wind_wave_period" in hourly_data and len(hourly_data["wind_wave_period"]) > 0:
                wind_wave_period = hourly_data["wind_wave_period"][0]
                if wind_wave_period is not None:
                    parsed["wind_wave_period_s"] = float(wind_wave_period)
            if "swell_wave_height" in hourly_data and len(hourly_data["swell_wave_height"]) > 0:
                swell_wave_height = hourly_data["swell_wave_height"][0]
                if swell_wave_height is not None:
                    parsed["swell_wave_height_m"] = float(swell_wave_height)
            if "swell_wave_direction" in hourly_data and len(hourly_data["swell_wave_direction"]) > 0:
                swell_wave_direction = hourly_data["swell_wave_direction"][0]
                if swell_wave_direction is not None:
                    parsed["swell_wave_direction_deg"] = float(swell_wave_direction)
            if "swell_wave_period" in hourly_data and len(hourly_data["swell_wave_period"]) > 0:
                swell_wave_period = hourly_data["swell_wave_period"][0]
                if swell_wave_period is not None:
                    parsed["swell_wave_period_s"] = float(swell_wave_period)
            if "ocean_current_velocity" in hourly_data and len(hourly_data["ocean_current_velocity"]) > 0:
                ocean_current_velocity = hourly_data["ocean_current_velocity"][0]
                if ocean_current_velocity is not None:
                    # Convert m/s to knots (1 m/s = 1.94384 knots)
                    parsed["ocean_current_speed_knots"] = float(ocean_current_velocity) * 1.94384
            if "ocean_current_direction" in hourly_data and len(hourly_data["ocean_current_direction"]) > 0:
                ocean_current_direction = hourly_data["ocean_current_direction"][0]
                if ocean_current_direction is not None:
                    parsed["ocean_current_direction_deg"] = float(ocean_current_direction)
            if "sea_surface_temperature" in hourly_data and len(hourly_data["sea_surface_temperature"]) > 0:
                sea_surface_temperature = hourly_data["sea_surface_temperature"][0]
                if sea_surface_temperature is not None:
                    parsed["sea_surface_temp_c"] = float(sea_surface_temperature)
            if "wind_speed_10m" in hourly_data and len(hourly_data["wind_speed_10m"]) > 0:
                wind_speed_10m = hourly_data["wind_speed_10m"][0]
                if wind_speed_10m is not None:
                    # Also store wind data that might be useful for marine conditions
                    parsed["wind_speed_kmh"] = float(wind_speed_10m) * 3.6  # m/s to km/h
            if "wind_direction_10m" in hourly_data and len(hourly_data["wind_direction_10m"]) > 0:
                wind_direction_10m = hourly_data["wind_direction_10m"][0]
                if wind_direction_10m is not None:
                    parsed["wind_direction_deg"] = float(wind_direction_10m)

        # Extract daily forecast summary (today)
        if "daily" in raw_data and raw_data["daily"]:
            daily_data = raw_data["daily"]
            if "wave_height_max" in daily_data and len(daily_data["wave_height_max"]) > 0:
                parsed["wave_height_max_m"] = float(daily_data["wave_height_max"][0])
            if "wave_direction_dominant" in daily_data and len(daily_data["wave_direction_dominant"]) > 0:
                parsed["wave_direction_dominant_deg"] = float(daily_data["wave_direction_dominant"][0])
            if "wave_period_max" in daily_data and len(daily_data["wave_period_max"]) > 0:
                parsed["wave_period_max_s"] = float(daily_data["wave_period_max"][0])
            if "sea_surface_temperature_max" in daily_data and len(daily_data["sea_surface_temperature_max"]) > 0:
                parsed["sea_surface_temp_max_c"] = float(daily_data["sea_surface_temperature_max"][0])
            if "sea_surface_temperature_min" in daily_data and len(daily_data["sea_surface_temperature_min"]) > 0:
                parsed["sea_surface_temp_min_c"] = float(daily_data["sea_surface_temperature_min"][0])
            if "wind_speed_10m_max" in daily_data and len(daily_data["wind_speed_10m_max"]) > 0:
                wind_speed_10m_max = daily_data["wind_speed_10m_max"][0]
                if wind_speed_10m_max is not None:
                    parsed["wind_speed_max_kmh"] = float(wind_speed_10m_max) * 3.6

        # Set forecast hours (default to 7 days * 24 hours)
        parsed["forecast_hours"] = 7 * 24

        return parsed

    async def health_check(self) -> bool:
        """
        Check if Open-Meteo Marine service is accessible

        Returns:
            True if service is responsive, False otherwise
        """
        try:
            # Try a simple request for a known location (e.g., middle of Indian Ocean)
            await self.get("", params={
                "latitude": 0.0,
                "longitude": 70.0,
                "hourly": "wave_height",
                "forecast_days": 1
            })
            return True
        except Exception as e:
            self.logger.warning(f"Open-Meteo Marine health check failed: {str(e)}")
            return False