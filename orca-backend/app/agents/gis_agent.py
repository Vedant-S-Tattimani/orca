"""
GIS / Geospatial Agent for ORCA
Processes boundaries, restricted naval zones, ecologically sensitive areas,
and evaluates geofences and spatial proximity warnings.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent
from ..services.geospatial_service import GeospatialService

logger = logging.getLogger(__name__)


class GISAgent(BaseAgent):
    """
    GIS specialist agent that checks geofences, maritime borders, restricted zones,
    and ecologically sensitive marine protected areas (MPAs).
    """

    def __init__(self):
        super().__init__("gis_agent")
        self.logger = logging.getLogger(f"{__name__}.GISAgent")
        self.geospatial_service = GeospatialService()

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Fetch geofence evaluations and proximity checks from GeospatialService.
        """
        self.logger.info(f"GIS Agent evaluating geofences for point ({latitude}, {longitude})")
        
        try:
            geofences = self.geospatial_service.check_geofences(latitude, longitude)
            
            # Count inside/danger zones
            active_violations = [g for g in geofences if g["inside"]]
            critical_warnings = [g for g in geofences if g["status"] in ["CRITICAL", "WARNING"]]

            return {
                "agent": "gis_agent",
                "geofences": geofences,
                "active_violations_count": len(active_violations),
                "critical_warnings_count": len(critical_warnings),
                "source": "Survey of India + Indian Coast Guard",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "confidence": 0.95,
                "status": "LIVE"
            }
        except Exception as e:
            self.logger.error(f"Error in GIS Agent fetch: {e}")
            raise

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize the GIS structured output format
        """
        if "error" in raw_data:
            return raw_data

        return {
            "agent": "gis_agent",
            "source": raw_data.get("source", "Survey of India"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "confidence": raw_data.get("confidence", 0.95),
            "status": raw_data.get("status", "LIVE"),
            "geofences": raw_data.get("geofences", []),
            "active_violations_count": raw_data.get("active_violations_count", 0),
            "critical_warnings_count": raw_data.get("critical_warnings_count", 0)
        }
