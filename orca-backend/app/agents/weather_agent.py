"""
Weather agent for ORCA - handles IMD wind/rain/visibility data
Specialist agent for weather-related marine conditions
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent
from ..services.imd_client import IMDClient
from ..config import settings

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """
    Weather specialist agent that fetets data from IMD (India Meteorological Department)
    or other weather sources for marine conditions
    """

    def __init__(self):
        super().__init__("weather")
        self.logger = logging.getLogger(f"{__name__}.WeatherAgent")
        # Initialize IMD client with configuration
        self.imd_client = IMDClient(
            api_key=settings.IMD_API_KEY,
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
        Fetch weather data from IMD or weather APIs

        In production, this calls actual IMD APIs for weather data
        Falls back to mock data if API is unavailable
        """
        self.logger.info(f"Fetching weather data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        # Start with mock data as base
        base_data = self._generate_mock_weather_data(latitude, longitude, start_time, end_time)
        weather_data = {}  # to collect real data from API

        try:
            # Attempt to fetch real data from IMD
            weather_data = await self.imd_client.get_weather_forecast(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km
            )
        except Exception as e:
            self.logger.warning(f"Failed to fetch real IMD data: {e}")

        # Update base_data with any real data we managed to fetch
        if weather_data:
            base_data.update(weather_data)

        # Ensure agent field is set to "weather"
        base_data["agent"] = "weather"

        # Set source and data_status based on what data we were able to fetch from API
        if weather_data:
            base_data["source"] = "IMD"
            base_data["data_status"] = "LIVE"
            base_data["confidence"] = 0.9
        else:
            base_data["source"] = "IMD (Simulated)"
            base_data["data_status"] = "SIMULATED"
            base_data["confidence"] = 0.4

        # Set timestamp if not already set by the API (but note: our mock data has it, and real data might overwrite)
        if "timestamp" not in base_data:
            base_data["timestamp"] = start_time.isoformat() + "Z"

        # Set forecast hours if not already set by the API
        if "forecast_hours" not in base_data:
            base_data["forecast_hours"] = int((end_time - start_time).total_seconds() / 3600)

        self.logger.debug(f"Fetched weather data: {base_data}")
        return base_data

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw weather data to structured format
        For the weather agent, the fetch method already returns structured data,
        but this method ensures consistency with the base agent interface
        """
        # If there's an error, return as-is
        if "error" in raw_data:
            return raw_data

        # Ensure all required fields are present
        structured = {
            "agent": "weather",
            "source": raw_data.get("source", "unknown"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
            "confidence": raw_data.get("confidence", 0.0)
        }

        # Copy all weather-specific fields
        weather_fields = [
            "wind_speed_kmh", "wind_direction_deg", "rainfall_mm",
            "visibility_km", "temperature_c", "humidity_percent",
            "pressure_hpa", "forecast_hours"
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
        Generate mock weather data for fallback when IMD API is unavailable
        Preserves the same structure as real API responses
        """
        self.logger.info("Generating mock weather data as fallback")

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
            "agent": "weather",
            "wind_speed_kmh": round(base_wind + wind_modifier, 1),
            "wind_direction_deg": round(random.uniform(0, 360), 1),
            "rainfall_mm": round(max(0, base_rainfall + random.uniform(-2, 2)), 1),
            "visibility_km": round(base_visibility + random.uniform(-3, 3), 1),
            "temperature_c": round(base_temp + temp_modifier, 1),
            "humidity_percent": round(base_humidity + random.uniform(-5, 5), 1),
            "pressure_hpa": round(random.uniform(1000, 1020), 1),
            "source": "IMD (Mock Fallback)",
            "timestamp": start_time.isoformat() + "Z",
            "confidence": 0.6,  # Lower confidence for mock data
            "forecast_hours": int((end_time - start_time).total_seconds() / 3600)
        }

        self.logger.debug(f"Generated mock weather data: {weather_data}")
        return weather_data

    async def check_health(self) -> Dict[str, str]:
        """Check health of IMD services"""
        try:
            is_healthy = await self.imd_client.health_check()
            if is_healthy:
                return {"status": "ok", "note": "IMD Satellite Link Online"}
            else:
                return {"status": "degraded", "note": "Primary IMD Link offline. Using fallback data."}
        except Exception as e:
            return {"status": "failed", "note": f"Agent error: {str(e)}"}


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta

    async def test_weather_agent():
        agent = WeatherAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        result = await agent.process(latitude, longitude, start_time, end_time)
        print("Weather Agent Result:")
        print(result)

    # Run the test
    asyncio.run(test_weather_agent())