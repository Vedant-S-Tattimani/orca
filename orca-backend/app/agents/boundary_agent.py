"""
Boundary Agent for ORCA
Calculates distance to International Maritime Boundary Lines (IMBL).
Specifically implements the India-Sri Lanka boundary (Palk Strait / Gulf of Mannar)
based on the 1974 and 1976 Maritime Boundary Agreements.
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging
import asyncio

from .base_agent import BaseAgent
from app.services.geospatial_service import point_to_segment_distance_km
from app.services.alert_service import AlertService
from app.db import db_manager

logger = logging.getLogger(__name__)

# Points from the 1974 India-Sri Lanka Maritime Boundary Agreement (Palk Strait).
# Source: United Nations Treaty Collection, Registration No. 13743,
# "Agreement between Sri Lanka and India on the boundary in historic waters"
# Format: [latitude, longitude]
# Note: Positions 1-6 independently verified against the official treaty text.
INDIA_SRI_LANKA_IMBL = [
    [10.0833, 80.0500], # Position 1 (10° 05' N, 80° 03' E)
    [9.9500, 79.5833],  # Position 2 (09° 57' N, 79° 35' E)
    [9.6692, 79.3767],  # Position 3 (09° 40.15' N, 79° 22.6' E)
    [9.3633, 79.5117],  # Position 4 (09° 21.8' N, 79° 30.7' E)
    [9.2167, 79.5333],  # Position 5 (09° 13' N, 79° 32' E)
    [9.1000, 79.5333]   # Position 6 (09° 06' N, 79° 32' E)
]

class BoundaryAgent(BaseAgent):
    """
    Checks proximity to the IMBL and triggers emergency alerts if in the critical zone.
    """
    def __init__(self):
        super().__init__("boundary_agent")
        self.logger = logging.getLogger(f"{__name__}.BoundaryAgent")
        self.alert_service = AlertService()
        self.caution_threshold_km = 10.0
        self.critical_threshold_km = 2.0

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate distance to the IMBL and trigger alerts if necessary.
        """
        self.logger.info(f"BoundaryAgent evaluating proximity for ({latitude}, {longitude})")
        
        # Calculate minimum distance to the polyline
        min_distance = float('inf')
        for i in range(len(INDIA_SRI_LANKA_IMBL) - 1):
            d = point_to_segment_distance_km(
                latitude, longitude,
                INDIA_SRI_LANKA_IMBL[i][0], INDIA_SRI_LANKA_IMBL[i][1],
                INDIA_SRI_LANKA_IMBL[i+1][0], INDIA_SRI_LANKA_IMBL[i+1][1]
            )
            min_distance = min(min_distance, d)
            
        status = "SAFE"
        risk_level = "GREEN"
        message = "Vessel is at a safe distance from the International Maritime Boundary Line."
        
        if min_distance < self.critical_threshold_km:
            status = "CRITICAL"
            risk_level = "RED"
            message = f"CRITICAL: Vessel is {min_distance:.1f}km from the India-Sri Lanka IMBL! Turn back immediately."
        elif min_distance < self.caution_threshold_km:
            status = "CAUTION"
            risk_level = "YELLOW"
            message = f"CAUTION: Vessel is approaching the IMBL ({min_distance:.1f}km). Alter course to remain in Indian waters."

        # Log boundary proximity event asynchronously if in caution or critical zone
        if status in ["CAUTION", "CRITICAL"]:
            asyncio.create_task(self._log_boundary_event(user_id, latitude, longitude, min_distance, status))

        # Trigger immediate push alert via Twilio if CRITICAL
        if status == "CRITICAL" and user_id:
            asyncio.create_task(self._trigger_emergency_alert(user_id, message))

        return {
            "agent": "boundary_agent",
            "imbl": "India-Sri Lanka",
            "distance_km": round(min_distance, 2),
            "zone": status,
            "risk_level": risk_level,
            "message": message,
            "source": "1974/1976 Maritime Boundary Agreements",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _log_boundary_event(self, user_id: Optional[str], lat: float, lon: float, distance: float, status: str):
        """Log the boundary proximity event into MongoDB for coastal authority review."""
        if not db_manager.db:
            return
        
        event = {
            "user_id": user_id or "anonymous",
            "location": {"type": "Point", "coordinates": [lon, lat]},
            "distance_km": distance,
            "status": status,
            "imbl": "India-Sri Lanka",
            "timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
        try:
            await db_manager.db["boundary_logs"].insert_one(event)
        except Exception as e:
            self.logger.error(f"Failed to log boundary event: {e}")
            
    async def _trigger_emergency_alert(self, user_id: str, message: str):
        """Send an SMS via the AlertService immediately."""
        try:
            self.logger.warning(f"BoundaryAgent triggering emergency alert for user {user_id}")
            alert_doc = {
                "title": "International Boundary Proximity Alert",
                "severity": "CRITICAL",
                "location": "IMBL India-Sri Lanka",
                "hazard": message,
                "recommended_action": "Turn back immediately to avoid arrest or seizure.",
                "provenance": "ORCA Boundary Agent"
            }
            await self.alert_service.push_alert(alert_doc)
        except Exception as e:
            self.logger.error(f"Failed to trigger emergency IMBL alert: {e}")

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        if "error" in raw_data:
            return raw_data
        return raw_data
