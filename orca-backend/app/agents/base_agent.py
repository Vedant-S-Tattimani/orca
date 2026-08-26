"""
Base agent interface for ORCA specialist agents
Defines the common interface that all domain-specific agents must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all specialist agents in ORCA
    Each agent represents a domain expert (weather, sea-state, hazards, etc.)
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

    @abstractmethod
    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch raw data from the agent's data source

        Args:
            latitude: Latitude of the query point
            longitude: Longitude of the query point
            start_time: Start of the time window
            end_time: End of the time window
            radius_km: Optional search radius around the point

        Returns:
            Dictionary containing raw data from the source
            Should include metadata like source, timestamp, confidence
        """
        pass

    @abstractmethod
    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw agent data to structured format

        Args:
            raw_data: Raw data fetched from the data source

        Returns:
            Structured data dictionary with standardized fields
            Must include: source, timestamp, confidence, and domain-specific fields
        """
        pass

    async def process(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Main processing method that combines fetch and to_structured

        Args:
            latitude: Latitude of the query point
            longitude: Longitude of the query point
            start_time: Start of the time window
            end_time: End of the time window
            radius_km: Optional search radius around the point

        Returns:
            Structured data ready for consumption by orchestrator/synthesis
        """
        try:
            self.logger.info(f"Fetching data for {self.agent_name} at ({latitude}, {longitude})")
            raw_data = await self.fetch(latitude, longitude, start_time, end_time, radius_km)
            structured_data = self.to_structured(raw_data)
            self.logger.info(f"Processed data for {self.agent_name}")
            return structured_data
        except Exception as e:
            self.logger.error(f"Error in {self.agent_name} processing: {str(e)}")
            # Return a structured error response
            return {
                "agent": self.agent_name,
                "error": str(e),
                "source": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "confidence": 0.0
            }

    async def check_health(self) -> Dict[str, str]:
        """
        Check the health of the agent and its underlying services.
        
        Returns:
            Dict containing 'status' ('ok', 'degraded', 'failed') and 'note'.
        """
        # Default implementation assumes healthy if agent can be instantiated
        return {
            "status": "ok",
            "note": f"{self.agent_name} is online (simulated)"
        }


# Example of what structured data should look like for each agent type:
# Weather Agent: {
#     "agent": "weather",
#     "wind_speed_kmh": 15.2,
#     "wind_direction_deg": 240,
#     "rainfall_mm": 0.0,
#     "visibility_km": 10.0,
#     "temperature_c": 28.5,
#     "humidity_percent": 75,
#     "source": "IMD",
#     "timestamp": "2026-08-24T05:00:00Z",
#     "confidence": 0.95
# }
#
# Sea-State Agent: {
#     "agent": "sea_state",
#     "wave_height_m": 1.8,
#     "wave_period_s": 8.5,
#     "swell_height_m": 1.2,
#     "swell_direction_deg": 180,
#     "current_speed_knots": 1.5,
#     "current_direction_deg": 90,
#     "tide_height_m": 1.2,
#     "source": "INCOIS",
#     "timestamp": "2026-08-24T05:00:00Z",
#     "confidence": 0.90
# }