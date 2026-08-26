"""
AIS / Vessel Agent for ORCA
Processes vessel tracking queries and reports nearby ship coordinates.
Marked clearly as SIMULATED to preserve solution credibility.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent
from ..services.ais_service import AISService

logger = logging.getLogger(__name__)


class AISAgent(BaseAgent):
    """
    AIS specialist agent that fetches nearby vessel coordinates and status.
    Returns simulated tracking telemetry with clean provenance headers.
    """

    def __init__(self):
        super().__init__("ais_agent")
        self.logger = logging.getLogger(f"{__name__}.AISAgent")
        self.ais_service = AISService()

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch vessel telemetries around query coords.
        Default search radius is 200km if not specified.
        """
        self.logger.info(f"AIS Agent fetching vessels within radius of ({latitude}, {longitude})")
        
        search_radius = radius_km if radius_km is not None else 200.0
        try:
            nearby_vessels = self.ais_service.find_nearby_vessels(latitude, longitude, search_radius)
            all_vessels = self.ais_service.get_all_vessels()

            return {
                "agent": "ais_agent",
                "nearby_vessels": nearby_vessels,
                "all_registered_vessels": all_vessels,
                "nearby_count": len(nearby_vessels),
                "search_radius_km": search_radius,
                "source": "DG Shipping AIS Receiver Network",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "confidence": 0.9,
                "status": "SIMULATED"
            }
        except Exception as e:
            self.logger.error(f"Error in AIS Agent fetch: {e}")
            raise

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize the AIS structured output format
        """
        if "error" in raw_data:
            return raw_data

        return {
            "agent": "ais_agent",
            "source": raw_data.get("source", "DG Shipping"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "confidence": raw_data.get("confidence", 0.9),
            "status": raw_data.get("status", "SIMULATED"),
            "nearby_vessels": raw_data.get("nearby_vessels", []),
            "all_registered_vessels": raw_data.get("all_registered_vessels", []),
            "nearby_count": raw_data.get("nearby_count", 0),
            "search_radius_km": raw_data.get("search_radius_km", 200.0)
        }
