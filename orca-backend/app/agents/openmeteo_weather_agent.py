"""
Open-Meteo Weather Agent for ORCA
Handles weather data from Open-Meteo API as an alternative/source to IMD
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent
from ..services.openmeteo_weather_client import OpenMeteoWeatherClient
from ..config import settings

logger = logging.getLogger(__name__)


class OpenMeteoWeatherAgent(BaseAgent):
    """
    Weather specialist agent that fetches data from Open-Meteo Weather API
    Can be used as an alternative to IMD or as a fallback
    """

    def __init__(self):
        super().__init__("openmeteo_weather")
        self.logger = logging.getLogger(f"{__name__}.OpenMeteoWeatherAgent")
        # Initialize Open-Meteo Weather client
        self.weather_client = OpenMeteoWeatherClient(
            timeout=30,
            max_retries=3
        )

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch weather data from Open-Meteo Weather API

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_time: Start of the time window
            end_time: End of the time window
            radius_km: Search radius in kilometers (not used by Open-Meteo but kept for interface consistency)

        Returns:
            Weather data dictionary
        """
        self.logger.info(f"Fetching Open-Meteo weather data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        try:
            # Calculate forecast hours based on time window
            forecast_hours = int((end_time - start_time).total_seconds() / 3600)
            # Limit to reasonable values (Open-Meteo supports up to 16 days hourly)
            forecast_days = min(max(1, forecast_hours // 24), 16)

            # Fetch real data from Open-Meteo
            weather_data = await self.weather_client.get_weather_forecast(
                latitude=latitude,
                longitude=longitude,
                forecast_days=forecast_days
            )

            # Ensure we have the required agent field
            if "agent" not in weather_data:
                weather_data["agent"] = "openmeteo_weather"
            weather_data["data_status"] = "LIVE"

            self.logger.debug(f"Fetched Open-Meteo weather data: {weather_data}")
            return weather_data

        except Exception as e:
            self.logger.warning(f"Failed to fetch real Open-Meteo weather data: {e}")
            # Fall back to mock data generation for resilience
            mock_data = self._generate_mock_weather_data(latitude, longitude, start_time, end_time)
            mock_data["data_status"] = "SIMULATED"
            return mock_data

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw Open-Meteo weather data to structured format
        For this agent, the fetch method already returns structured data,
        but this method ensures consistency with the base agent interface
        """
        # If there's an error, return as-is
        if "error" in raw_data:
            return raw_data

        # Ensure all required fields are present
        structured = {
            "agent": "openmeteo_weather",
            "source": raw_data.get("source", "Open-Meteo"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "confidence": raw_data.get("confidence", 0.0)
        }

        # Copy all weather-specific fields
        weather_fields = [
            "temperature_c", "humidity_percent", "rainfall_mm",
            "wind_speed_kmh", "wind_direction_deg", "visibility_km",
            "pressure_hpa", "forecast_hours", "weather_code", "weather_condition",
            "temperature_max_c", "temperature_min_c", "precipitation_sum_mm",
            "wind_speed_max_kmh", "forecast_24h"
        ]

        for field in weather_fields:
            if field in raw_data:
                structured[field] = raw_data[field]

        return structured

    def _generate_mock_weather_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate mock weather data for fallback when Open-Meteo API is unavailable
        Preserves the same structure as real API responses
        """
        self.logger.info("Generating mock Open-Meteo weather data as fallback")

        # Simulate API call delay to maintain consistent timing
        import asyncio
        import random

        # Generate realistic mock data
        base_wind = random.uniform(5, 25)  # km/h
        base_rainfall = random.uniform(0, 10)  # mm/h
        base_visibility = random.uniform(5, 20)  # km
        base_temp = random.uniform(24, 32)  # °C
        base_humidity = random.uniform(60, 85)  # percent

        # Add some variation based on time of day
        hour = start_time.hour
        if 6 <= hour <= 18:  # Daytime
            temp_modifier = 0
            wind_modifier = random.uniform(-2, 3)
        else:  # Nighttime
            temp_modifier = -3
            wind_modifier = random.uniform(-1, 2)

        weather_data = {
            "agent": "openmeteo_weather",
            "wind_speed_kmh": round(base_wind + wind_modifier, 1),
            "wind_direction_deg": round(random.uniform(0, 360), 1),
            "rainfall_mm": round(max(0, base_rainfall + random.uniform(-2, 2)), 1),
            "visibility_km": round(base_visibility + random.uniform(-3, 3), 1),
            "temperature_c": round(base_temp + temp_modifier, 1),
            "humidity_percent": round(base_humidity + random.uniform(-5, 5), 1),
            "pressure_hpa": round(random.uniform(1000, 1020), 1),
            "source": "Open-Meteo (Mock Fallback)",
            "timestamp": start_time.isoformat() + "Z",
            "confidence": 0.6,  # Lower confidence for mock data
            "forecast_hours": int((end_time - start_time).total_seconds() / 3600)
        }

        # Add some optional fields that might be present in real data
        weather_data["weather_code"] = random.choice([0, 1, 2, 3, 61, 63, 65])
        weather_data["weather_condition"] = self._weather_code_to_description(weather_data["weather_code"])

        # Generate mock 24-hour forecast
        from datetime import timedelta
        forecast_24h = []
        base_wind_dir = weather_data["wind_direction_deg"]
        for i in range(24):
            ftime = start_time + timedelta(hours=i)
            # Add some sinusoidal diurnal variation for temperature
            hour_offset = (ftime.hour - 14) / 24.0 * 2 * 3.14159
            import math
            temp_var = math.cos(hour_offset) * 4.0
            
            forecast_24h.append({
                "time": ftime.isoformat() + "Z",
                "temperature_c": round(base_temp + temp_var + random.uniform(-0.5, 0.5), 1),
                "wind_speed_kmh": max(0, round(base_wind + random.uniform(-5, 5), 1)),
                "wind_direction_deg": round((base_wind_dir + random.uniform(-15, 15)) % 360, 1)
            })
        weather_data["forecast_24h"] = forecast_24h

        self.logger.debug(f"Generated mock Open-Meteo weather data: {weather_data}")
        return weather_data

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
        Check if Open-Meteo Weather service is accessible

        Returns:
            True if service is responsive, False otherwise
        """
        return await self.weather_client.health_check()


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta

    async def test_openmeteo_weather_agent():
        agent = OpenMeteoWeatherAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        result = await agent.process(latitude, longitude, start_time, end_time)
        print("Open-Meteo Weather Agent Result:")
        print(result)

    # Run the test
    asyncio.run(test_openmeteo_weather_agent())