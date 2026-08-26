"""
Open-Meteo Marine Agent for ORCA
Handles marine data from Open-Meteo Marine API as an alternative/source to INCOIS
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent
from ..services.openmeteo_marine_client import OpenMeteoMarineClient
from ..config import settings

logger = logging.getLogger(__name__)


class OpenMeteoMarineAgent(BaseAgent):
    """
    Sea-state specialist agent that fetches data from Open-Meteo Marine API
    Can be used as an alternative to INCOIS or as a fallback
    """

    def __init__(self):
        super().__init__("openmeteo_marine")
        self.logger = logging.getLogger(f"{__name__}.OpenMeteoMarineAgent")
        # Initialize Open-Meteo Marine client
        self.marine_client = OpenMeteoMarineClient(
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
        Fetch marine data from Open-Meteo Marine API

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            start_time: Start of the time window
            end_time: End of the time window
            radius_km: Search radius in kilometers (not used by Open-Meteo but kept for interface consistency)

        Returns:
            Marine data dictionary
        """
        self.logger.info(f"Fetching Open-Meteo marine data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        try:
            # Calculate forecast hours based on time window
            forecast_hours = int((end_time - start_time).total_seconds() / 3600)
            # Limit to reasonable values (Open-Meteo supports up to 16 days hourly)
            forecast_days = min(max(1, forecast_hours // 24), 16)

            # Fetch real data from Open-Meteo Marine
            marine_data = await self.marine_client.get_marine_forecast(
                latitude=latitude,
                longitude=longitude,
                forecast_days=forecast_days
            )

            # Ensure we have the required agent field
            if "agent" not in marine_data:
                marine_data["agent"] = "openmeteo_marine"
            marine_data["data_status"] = "LIVE"

            self.logger.debug(f"Fetched Open-Meteo marine data: {marine_data}")
            return marine_data

        except Exception as e:
            self.logger.warning(f"Failed to fetch real Open-Meteo marine data: {e}")
            mock_data = self._generate_mock_marine_data(latitude, longitude, start_time, end_time)
            mock_data["data_status"] = "SIMULATED"
            return mock_data

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw Open-Meteo marine data to structured format
        For this agent, the fetch method already returns structured data,
        but this method ensures consistency with the base agent interface
        """
        # If there's an error, return as-is
        if "error" in raw_data:
            return raw_data

        # Ensure all required fields are present
        structured = {
            "agent": "openmeteo_marine",
            "source": raw_data.get("source", "Open-Meteo"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "confidence": raw_data.get("confidence", 0.0)
        }

        # Copy all marine-specific fields
        marine_fields = [
            "wave_height_m", "wave_direction_deg", "wave_period_s",
            "wind_wave_height_m", "wind_wave_direction_deg", "wind_wave_period_s",
            "swell_wave_height_m", "swell_wave_direction_deg", "swell_wave_period_s",
            "ocean_current_speed_knots", "ocean_current_direction_deg",
            "sea_surface_temp_c", "forecast_hours",
            "wave_height_max_m", "wave_direction_dominant_deg", "wave_period_max_s",
            "sea_surface_temp_max_c", "sea_surface_temp_min_c",
            "ocean_current_speed_max_knots"
        ]

        for field in marine_fields:
            if field in raw_data:
                structured[field] = raw_data[field]

        return structured

    def _generate_mock_marine_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate mock marine data for fallback when Open-Meteo Marine API is unavailable
        Preserves the same structure as real API responses
        """
        self.logger.info("Generating mock Open-Meteo marine data as fallback")

        # Simulate API call delay to maintain consistent timing
        import asyncio
        import random

        # Generate realistic mock marine data
        # Base values typical for coastal waters
        base_wave_height = random.uniform(0.5, 3.0)  # meters
        base_wave_direction = random.uniform(0, 360)  # degrees
        base_wave_period = random.uniform(5, 15)     # seconds
        base_swell_height = random.uniform(0.2, 2.0)  # meters
        base_swell_direction = random.uniform(0, 360) # degrees
        base_swell_period = random.uniform(5, 20)     # seconds
        base_wind_wave_height = random.uniform(0.3, 1.5) # meters
        base_wind_wave_direction = random.uniform(0, 360) # degrees
        base_wind_wave_period = random.uniform(3, 10)   # seconds
        base_current_speed = random.uniform(0.5, 3.0)   # knots
        base_current_direction = random.uniform(0, 360) # degrees
        base_sea_surface_temp = random.uniform(26, 30)  # °C

        # Add some temporal variation
        hour = start_time.hour
        # Diurnal variation for temperature
        temp_modifier = 0
        if 6 <= hour <= 18:  # Daytime
            temp_modifier = 0
        else:  # Nighttime
            temp_modifier = -2

        marine_data = {
            "agent": "openmeteo_marine",
            "wave_height_m": round(base_wave_height + random.uniform(-0.3, 0.3), 2),
            "wave_direction_deg": round(base_wave_direction + random.uniform(-15, 15), 1),
            "wave_period_s": round(base_wave_period + random.uniform(-2, 2), 1),
            "swell_wave_height_m": round(base_swell_height + random.uniform(-0.2, 0.2), 2),
            "swell_wave_direction_deg": round(base_swell_direction + random.uniform(-15, 15), 1),
            "swell_wave_period_s": round(base_swell_period + random.uniform(-3, 3), 1),
            "wind_wave_height_m": round(base_wind_wave_height + random.uniform(-0.2, 0.2), 2),
            "wind_wave_direction_deg": round(base_wind_wave_direction + random.uniform(-15, 15), 1),
            "wind_wave_period_s": round(base_wind_wave_period + random.uniform(-2, 2), 1),
            "ocean_current_speed_knots": round(base_current_speed + random.uniform(-0.5, 0.5), 2),
            "ocean_current_direction_deg": round(base_current_direction + random.uniform(-10, 10), 1),
            "sea_surface_temp_c": round(base_sea_surface_temp + temp_modifier, 1),
            "source": "Open-Meteo Marine (Mock Fallback)",
            "timestamp": start_time.isoformat() + "Z",
            "confidence": 0.6,  # Lower confidence for mock data
            "forecast_hours": int((end_time - start_time).total_seconds() / 3600)
        }

        # Add some daily max/min values
        marine_data["wave_height_max_m"] = round(marine_data["wave_height_m"] + random.uniform(0.2, 0.8), 2)
        marine_data["wave_direction_dominant_deg"] = marine_data["wave_direction_deg"]
        marine_data["wave_period_max_s"] = round(marine_data["wave_period_s"] + random.uniform(0, 3), 1)
        marine_data["sea_surface_temp_max_c"] = round(marine_data["sea_surface_temp_c"] + random.uniform(0, 2), 1)
        marine_data["sea_surface_temp_min_c"] = round(marine_data["sea_surface_temp_c"] - random.uniform(0, 2), 1)
        marine_data["ocean_current_speed_max_knots"] = round(marine_data["ocean_current_speed_knots"] + random.uniform(0, 1), 2)

        self.logger.debug(f"Generated mock Open-Meteo marine data: {marine_data}")
        return marine_data

    async def health_check(self) -> bool:
        """
        Check if Open-Meteo Marine service is accessible

        Returns:
            True if service is responsive, False otherwise
        """
        return await self.marine_client.health_check()


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta

    async def test_openmeteo_marine_agent():
        agent = OpenMeteoMarineAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        result = await agent.process(latitude, longitude, start_time, end_time)
        print("Open-Meteo Marine Agent Result:")
        print(result)

    # Run the test
    asyncio.run(test_openmeteo_marine_agent())