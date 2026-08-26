"""
Sea-state agent for ORCA - handles INCOIS wave/swell/tide data
Specialist agent for sea-state conditions
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

from .base_agent import BaseAgent
from ..services.incois_client import INCOISClient
from ..config import settings

logger = logging.getLogger(__name__)

class SeaStateAgent(BaseAgent):
    """
    Sea-state specialist agent that fetches data from INCOIS (Indian National Centre for Ocean Information Services)
    or other ocean state sources for wave, swell, current, and tide data
    """

    def __init__(self):
        super().__init__("sea_state")
        self.logger = logging.getLogger(f"{__name__}.SeaStateAgent")
        # Initialize INCOIS client with configuration
        self.incois_client = INCOISClient(
            api_key=settings.INCOIS_API_KEY,
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
        Fetch sea-state data from INCOIS or ocean APIs

        In production, this calls actual INCOIS APIs for sea-state data
        Falls back to mock data if API is unavailable
        """
        self.logger.info(f"Fetching sea-state data for ({latitude}, {longitude}) from {start_time} to {end_time}")

        try:
            # Attempt to fetch real data from INCOIS
            sea_state_data = await self.incois_client.get_sea_state_forecast(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km
            )

            # Ensure we have the required agent field
            if "agent" not in sea_state_data:
                sea_state_data["agent"] = "sea_state"
            sea_state_data["data_status"] = "LIVE"

            self.logger.debug(f"Fetched sea-state data from INCOIS: {sea_state_data}")
            return sea_state_data

        except Exception as e:
            self.logger.warning(f"Failed to fetch real INCOIS data, falling back to simulated: {e}")
            # Fall back to mock data generation for resilience
            mock_data = self._generate_mock_sea_state_data(latitude, longitude, start_time, end_time)
            mock_data["data_status"] = "SIMULATED"
            mock_data["source"] = "INCOIS (Simulated)"
            mock_data["confidence"] = 0.4
            return mock_data

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw sea-state data to structured format
        For the sea-state agent, the fetch method already returns structured data,
        but this method ensures consistency with the base agent interface
        """
        # If there's an error, return as-is
        if "error" in raw_data:
            return raw_data

        # Ensure all required fields are present
        structured = {
            "agent": "sea_state",
            "source": raw_data.get("source", "unknown"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
            "confidence": raw_data.get("confidence", 0.0)
        }

        # Copy all sea-state-specific fields
        sea_state_fields = [
            "wave_height_m", "wave_period_s", "swell_height_m", "swell_direction_deg",
            "current_speed_knots", "current_direction_deg", "tide_height_m",
            "sea_surface_temp_c", "salinity_psu", "forecast_hours"
        ]

        for field in sea_state_fields:
            if field in raw_data:
                structured[field] = raw_data[field]

        return structured

    def _generate_mock_sea_state_data(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """
        Generate mock sea-state data for fallback when INCOIS API is unavailable
        Preserves the same structure as real API responses
        """
        self.logger.info("Generating mock sea-state data as fallback")

        # Simulate API call delay to maintain consistent timing
        import asyncio
        import random

        # Generate realistic mock sea-state data
        # Base values typical for coastal waters
        base_wave_height = random.uniform(0.5, 3.0)  # meters
        base_wave_period = random.uniform(5, 15)    # seconds
        base_swell_height = random.uniform(0.2, 2.0) # meters
        base_swell_direction = random.uniform(0, 360) # degrees
        base_current_speed = random.uniform(0.5, 3.0) # knots
        base_current_direction = random.uniform(0, 360) # degrees
        base_tide_height = random.uniform(-1.5, 2.0)  # meters (relative to MSL)

        # Add some temporal variation
        hour = start_time.hour
        # Tidal variation (simplified)
        tide_modifier = 0.5 * random.uniform(-1, 1) * abs((hour - 12) / 6)  # Simple tidal model

        sea_state_data = {
            "agent": "sea_state",
            "wave_height_m": round(base_wave_height + random.uniform(-0.3, 0.3), 2),
            "wave_period_s": round(base_wave_period + random.uniform(-2, 2), 1),
            "swell_height_m": round(base_swell_height + random.uniform(-0.2, 0.2), 2),
            "swell_direction_deg": round(base_swell_direction + random.uniform(-15, 15), 1),
            "current_speed_knots": round(base_current_speed + random.uniform(-0.5, 0.5), 2),
            "current_direction_deg": round(base_current_direction + random.uniform(-10, 10), 1),
            "tide_height_m": round(base_tide_height + tide_modifier, 2),
            "sea_surface_temp_c": round(random.uniform(26, 30), 1),  # Often correlated
            "salinity_psu": round(random.uniform(33, 37), 1),
            "source": "INCOIS (Mock Fallback)",
            "timestamp": start_time.isoformat() + "Z",
            "confidence": 0.6,  # Lower confidence for mock data
            "forecast_hours": int((end_time - start_time).total_seconds() / 3600)
        }

        self.logger.debug(f"Generated mock sea-state data: {sea_state_data}")
        return sea_state_data

    async def check_health(self) -> Dict[str, str]:
        """Check health of INCOIS services"""
        try:
            is_healthy = await self.incois_client.health_check()
            if is_healthy:
                return {"status": "ok", "note": "INCOIS Wave Buoys Transmitting"}
            else:
                return {"status": "degraded", "note": "INCOIS API unreachable. Using fallback."}
        except Exception as e:
            return {"status": "failed", "note": f"Agent error: {str(e)}"}


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from datetime import datetime, timedelta

    async def test_sea_state_agent():
        agent = SeaStateAgent()

        # Test with Kollam coordinates
        latitude = 8.8932
        longitude = 76.6141
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=5)

        result = await agent.process(latitude, longitude, start_time, end_time)
        print("Sea-State Agent Result:")
        print(result)

    # Run the test
    asyncio.run(test_sea_state_agent())