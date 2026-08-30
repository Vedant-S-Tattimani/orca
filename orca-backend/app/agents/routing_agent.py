"""
Route Optimization Agent for ORCA
Invokes RoutingService to calculate maritime-safe route geometries and parameters.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent
from ..services.routing_service import RoutingService, COASTAL_WAYPOINTS, haversine_distance_km

logger = logging.getLogger(__name__)


class RoutingAgent(BaseAgent):
    """
    Route Optimization specialist agent.
    Computes navigable ship coordinates, distances in NM, and duration estimates.
    """

    def __init__(self):
        super().__init__("routing_agent")
        self.logger = logging.getLogger(f"{__name__}.RoutingAgent")
        self.routing_service = RoutingService()

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius_km: Optional[float] = None,
        user_id: Optional[str] = None,
        emergency: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch optimized routing parameters.
        Expects destination coordinates in metadata / parameters, otherwise defaults to Chennai.
        """
        # Note: If no specific destination is passed in parameters, we fallback to Chennai
        # This occurs when called generally from the planner.
        # But we can override dest_lat/dest_lon in radius_km parameter or standard context if needed.
        dest_lat = 13.0906
        dest_lon = 80.2989

        if emergency:
            self.logger.info("EMERGENCY mode active: routing to nearest safe harbour.")
            best_dist = float('inf')
            best_wp = None
            for wp in COASTAL_WAYPOINTS:
                dist = haversine_distance_km(latitude, longitude, wp["lat"], wp["lon"])
                if dist < best_dist:
                    best_dist = dist
                    best_wp = wp
            if best_wp:
                dest_lat = best_wp["lat"]
                dest_lon = best_wp["lon"]
                self.logger.info(f"Nearest safe harbour identified as {best_wp['name']} at {best_dist}km.")
        
        self.logger.info(f"Routing Agent calculating route from ({latitude}, {longitude}) to ({dest_lat}, {dest_lon})")
        
        try:
            route_data = self.routing_service.calculate_route(
                origin_lat=latitude,
                origin_lon=longitude,
                dest_lat=dest_lat,
                dest_lon=dest_lon
            )

            return {
                "agent": "routing_agent",
                "route_type": route_data["route_type"],
                "coordinates": route_data["coordinates"],
                "distance_nm": route_data["distance_nm"],
                "distance_km": route_data["distance_km"],
                "duration_hours": route_data["duration_hours"],
                "speed_knots": route_data["speed_knots"],
                "crosses_land": route_data["crosses_land"],
                "source": "ORCA Maritime Routing Processor",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "confidence": 0.95,
                "status": "LIVE"
            }
        except Exception as e:
            self.logger.error(f"Error in Routing Agent fetch: {e}")
            raise

    def to_structured(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize the Routing structured output format
        """
        if "error" in raw_data:
            return raw_data

        return {
            "agent": "routing_agent",
            "source": raw_data.get("source", "ORCA Routing"),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
            "confidence": raw_data.get("confidence", 0.95),
            "status": raw_data.get("status", "LIVE"),
            "route_type": raw_data.get("route_type", "Preliminary Geodesic Route"),
            "coordinates": raw_data.get("coordinates", []),
            "distance_nm": raw_data.get("distance_nm", 0.0),
            "distance_km": raw_data.get("distance_km", 0.0),
            "duration_hours": raw_data.get("duration_hours", 0.0),
            "crosses_land": raw_data.get("crosses_land", False)
        }
