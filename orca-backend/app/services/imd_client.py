"""
IMD (India Meteorological Department) API client for ORCA
Handles weather forecasts, cyclone bulletins, and lightning data
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class IMDClient(BaseAPIClient):
    """
    Client for India Meteorological Department APIs
    Fetches weather data, cyclone information, and lightning nowcasts
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://mausam.imd.gov.in",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize IMD API client

        Args:
            api_key: IMD API key (if required)
            base_url: Base URL for IMD services
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
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get weather forecast for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (optional)

        Returns:
            Weather forecast data
        """
        # Note: This is a placeholder implementation based on typical weather API patterns
        # Actual IMD API endpoints would need to be researched and implemented
        endpoint = "/api/weather/forecast"
        params = {
            "lat": latitude,
            "lon": longitude,
        }
        if radius_km:
            params["radius"] = radius_km

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_weather_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching IMD weather forecast: {str(e)}")
            raise

    async def get_cyclone_info(
        self,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get cyclone information for a specific region

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (optional)

        Returns:
            Cyclone tracking and forecast data
        """
        endpoint = "/api/cyclone/active"
        params = {
            "lat": latitude,
            "lon": longitude,
        }
        if radius_km:
            params["radius"] = radius_km

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_cyclone_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching IMD cyclone info: {str(e)}")
            raise

    async def get_lightning_nowcast(
        self,
        latitude: float,
        longitude: float,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get lightning nowcast/data for a specific location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            radius_km: Search radius in kilometers (optional)

        Returns:
            Lightning probability and activity data
        """
        endpoint = "/api/lightning/nowcast"
        params = {
            "lat": latitude,
            "lon": longitude,
        }
        if radius_km:
            params["radius"] = radius_km

        try:
            response = await self.get(endpoint, params=params)
            return self._parse_lightning_response(response, latitude, longitude)
        except Exception as e:
            self.logger.error(f"Error fetching IMD lightning nowcast: {str(e)}")
            raise

    def _parse_weather_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse IMD weather response into standardized format

        Args:
            raw_data: Raw response from IMD API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed weather data in ORCA standard format
        """
        # This is a placeholder - actual implementation depends on IMD API response structure
        # For now, we'll extract common weather fields if they exist, otherwise provide defaults

        parsed = {
            "agent": "weather",
            "source": "IMD",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.9  # High confidence for official government data
        }

        # Extract common weather fields with fallbacks
        weather_mapping = {
            "wind_speed_kmh": ["wind_speed", "ws", "windSpeed"],
            "wind_direction_deg": ["wind_direction", "wd", "windDir"],
            "rainfall_mm": ["rainfall", "rain", "precipitation"],
            "visibility_km": ["visibility", "vis"],
            "temperature_c": ["temperature", "temp", "t"],
            "humidity_percent": ["humidity", "rh"],
            "pressure_hpa": ["pressure", "pres", "p"]
        }

        for our_key, possible_keys in weather_mapping.items():
            value = None
            for key in possible_keys:
                if key in raw_data:
                    value = raw_data[key]
                    break

            if value is not None:
                # Apply any necessary unit conversions here
                parsed[our_key] = float(value)
            else:
                # Provide reasonable defaults if data not available
                defaults = {
                    "wind_speed_kmh": 15.0,
                    "wind_direction_deg": 180.0,
                    "rainfall_mm": 0.0,
                    "visibility_km": 10.0,
                    "temperature_c": 28.0,
                    "humidity_percent": 75.0,
                    "pressure_hpa": 1013.0
                }
                parsed[our_key] = defaults.get(our_key, 0.0)

        # Add forecast hours if available
        if "forecast_hours" in raw_data:
            parsed["forecast_hours"] = int(raw_data["forecast_hours"])
        else:
            parsed["forecast_hours"] = 5  # Default forecast horizon

        return parsed

    def _parse_cyclone_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse IMD cyclone response into standardized format

        Args:
            raw_data: Raw response from IMD API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed cyclone data in ORCA standard format
        """
        parsed = {
            "agent": "hazard",
            "source": "IMD",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.85
        }

        # Extract cyclone-specific fields
        cyclone_fields = {
            "cyclone_wind_speed_kmh": ["max_wind_speed", "wind_speed"],
            "cyclone_latitude": ["latitude", "lat"],
            "cyclone_longitude": ["longitude", "lon"],
            "cyclone_category": ["category", "storm_category"]
        }

        for our_key, possible_keys in cyclone_fields.items():
            value = None
            for key in possible_keys:
                if key in raw_data:
                    value = raw_data[key]
                    break

            if value is not None:
                parsed[our_key] = float(value) if our_key.endswith(('_latitude', '_longitude', '_wind_speed_kmh')) else str(value)
            else:
                # Defaults for cyclone data
                defaults = {
                    "cyclone_wind_speed_kmh": 0.0,
                    "cyclone_latitude": latitude,
                    "cyclone_longitude": longitude,
                    "cyclone_category": "None"
                }
                parsed[our_key] = defaults.get(our_key, 0.0 if 'speed' in our_key or 'latitude' in our_key or 'longitude' in our_key else "None")

        # Calculate distance to cyclone if coordinates provided
        if "cyclone_latitude" in parsed and "cyclone_longitude" in parsed:
            # Simple distance calculation (more accurate methods could be used)
            lat_diff = abs(parsed["cyclone_latitude"] - latitude)
            lon_diff = abs(parsed["cyclone_longitude"] - longitude)
            # Rough conversion: 1 degree ≈ 111 km
            distance_km = ((lat_diff ** 2) + (lon_diff ** 2)) ** 0.5 * 111
            parsed["cyclone_distance_km"] = round(distance_km, 1)
        else:
            parsed["cyclone_distance_km"] = float('inf')

        return parsed

    def _parse_lightning_response(
        self,
        raw_data: Dict[str, Any],
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Parse IMD lightning response into standardized format

        Args:
            raw_data: Raw response from IMD API
            latitude: Requested latitude
            longitude: Requested longitude

        Returns:
            Parsed lightning data in ORCA standard format
        """
        parsed = {
            "agent": "hazard",
            "source": "IMD",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence": 0.8
        }

        # Extract lightning probability
        lightning_keys = ["lightning_probability", "probability", "lp", "flash_rate"]
        lightning_value = None

        for key in lightning_keys:
            if key in raw_data:
                lightning_value = raw_data[key]
                break

        if lightning_value is not None:
            # Convert to percentage if needed (assuming 0-1 scale might need conversion)
            value = float(lightning_value)
            if value <= 1.0:  # Assume it's a fraction
                parsed["lightning_probability_percent"] = value * 100
            else:  # Assume it's already percentage
                parsed["lightning_probability_percent"] = min(value, 100.0)
        else:
            parsed["lightning_probability_percent"] = 0.0

        # Additional lightning fields if available
        if "flash_density" in raw_data:
            parsed["flash_density_flashes_per_km2_per_min"] = float(raw_data["flash_density"])
        else:
            parsed["flash_density_flashes_per_km2_per_min"] = 0.0

        return parsed

    async def health_check(self) -> bool:
        """
        Check if IMD service is accessible

        Returns:
            True if service is responsive, False otherwise
        """
        try:
            # Try a lightweight endpoint or just test connectivity
            await self.get("/api/health", params={})
            return True
        except Exception:
            # If specific health endpoint doesn't exist, try a basic endpoint
            try:
                await self.get("/api/weather/forecast", params={"lat": 0, "lon": 0})
                return True
            except Exception:
                return False