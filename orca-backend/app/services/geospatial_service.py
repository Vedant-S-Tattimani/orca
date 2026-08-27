"""
Geospatial and Geofencing Service for ORCA
Defines maritime boundaries, restricted areas, ecologically sensitive zones,
and evaluates spatial intersections and proximity.
"""
import math
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging
from app.db import db_manager

logger = logging.getLogger(__name__)

class GeofenceCache:
    IMBL_SRI_LANKA = []
    IMBL_PAKISTAN = []
    ECO_GULF_OF_MANNAR = []
    ECO_SUNDARBANS = []
    RESTRICTED_LAKSHADWEEP = []

    @classmethod
    async def load_from_db(cls):
        db = db_manager.db
        if db is None:
            logger.warning("No DB connection to load geofences. Boundaries will be empty.")
            return

        cursor = db["geofences"].find({})
        docs = await cursor.to_list(length=100)
        
        for doc in docs:
            if doc["id"] == "IMBL_SRI_LANKA":
                cls.IMBL_SRI_LANKA = doc["coordinates"]
            elif doc["id"] == "IMBL_PAKISTAN":
                cls.IMBL_PAKISTAN = doc["coordinates"]
            elif doc["id"] == "ECO_GULF_OF_MANNAR":
                cls.ECO_GULF_OF_MANNAR = doc["coordinates"]
            elif doc["id"] == "ECO_SUNDARBANS":
                cls.ECO_SUNDARBANS = doc["coordinates"]
            elif doc["id"] == "RESTRICTED_LAKSHADWEEP":
                cls.RESTRICTED_LAKSHADWEEP = doc["coordinates"]
        
        logger.info(f"Loaded {len(docs)} geofences from MongoDB.")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    R = 6371.0  # Earth's radius
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def point_to_segment_distance_km(lat: float, lon: float, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Approximate distance from a point to a line segment in kilometers"""
    # Check distance to endpoints first
    d1 = haversine_km(lat, lon, lat1, lon1)
    d2 = haversine_km(lat, lon, lat2, lon2)
    
    # Vector projection projection math in flat plane (satisfactory for short segments)
    d_lat = lat2 - lat1
    d_lon = lon2 - lon1
    segment_len_sq = d_lat**2 + d_lon**2
    if segment_len_sq == 0:
        return d1
        
    t = ((lat - lat1) * d_lat + (lon - lon1) * d_lon) / segment_len_sq
    t = max(0.0, min(1.0, t))  # Clamp to segment
    
    proj_lat = lat1 + t * d_lat
    proj_lon = lon1 + t * d_lon
    
    return haversine_km(lat, lon, proj_lat, proj_lon)


def point_in_polygon(lat: float, lon: float, polygon: List[List[float]]) -> bool:
    """Ray casting algorithm to check if coordinate is inside a polygon [lat, lon] lists"""
    if not polygon:
        return False
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0][1], polygon[0][0]  # lon, lat
    for i in range(n + 1):
        p2x, p2y = polygon[i % n][1], polygon[i % n][0]
        if lon > min(p1x, p2x):
            if lon <= max(p1x, p2x):
                if lat <= max(p1y, p2y):
                    if p1x != p2x:
                        xinters = (lon - p1x) * (p2y - p1y) / (p2x - p1x) + p1y
                    if p1y == p2y or lat <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


class GeospatialService:
    """
    Evaluates geospatial boundaries, restricted areas, international border lines,
    and returns alerts and distance assessments.
    """

    def __init__(self):
        pass

    def check_geofences(self, latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """
        Check coordinates against all configured geofences and boundaries.
        Returns detailed diagnostic alerts.
        """
        results = []

        # 1. Sri Lanka Border Check
        sri_lanka_dist = float('inf')
        for i in range(len(GeofenceCache.IMBL_SRI_LANKA) - 1):
            d = point_to_segment_distance_km(
                latitude, longitude,
                GeofenceCache.IMBL_SRI_LANKA[i][0], GeofenceCache.IMBL_SRI_LANKA[i][1],
                GeofenceCache.IMBL_SRI_LANKA[i+1][0], GeofenceCache.IMBL_SRI_LANKA[i+1][1]
            )
            sri_lanka_dist = min(sri_lanka_dist, d)

        sl_status = "INFO"
        if sri_lanka_dist < 5.0:
            sl_status = "CRITICAL"
        elif sri_lanka_dist < 15.0:
            sl_status = "WARNING"
        elif sri_lanka_dist < 30.0:
            sl_status = "WATCH"

        results.append({
            "geofence_name": "India - Sri Lanka International Maritime Boundary Line",
            "type": "IMBL",
            "distance_km": round(sri_lanka_dist, 2),
            "status": sl_status,
            "inside": False,
            "description": f"Distance to India-Sri Lanka IMBL is {round(sri_lanka_dist, 1)} km. Avoid crossing without authorization.",
            "recommended_action": "Maintain course away from the boundary line." if sl_status != "INFO" else "None"
        })

        # 2. Pakistan Border Check
        pakistan_dist = float('inf')
        for i in range(len(GeofenceCache.IMBL_PAKISTAN) - 1):
            d = point_to_segment_distance_km(
                latitude, longitude,
                GeofenceCache.IMBL_PAKISTAN[i][0], GeofenceCache.IMBL_PAKISTAN[i][1],
                GeofenceCache.IMBL_PAKISTAN[i+1][0], GeofenceCache.IMBL_PAKISTAN[i+1][1]
            )
            pakistan_dist = min(pakistan_dist, d)

        pak_status = "INFO"
        if pakistan_dist < 10.0:
            pak_status = "CRITICAL"
        elif pakistan_dist < 25.0:
            pak_status = "WARNING"
        elif pakistan_dist < 50.0:
            pak_status = "WATCH"

        results.append({
            "geofence_name": "India - Pakistan International Maritime Boundary Line",
            "type": "IMBL",
            "distance_km": round(pakistan_dist, 2),
            "status": pak_status,
            "inside": False,
            "description": f"Distance to India-Pakistan IMBL is {round(pakistan_dist, 1)} km. Border region is highly sensitive.",
            "recommended_action": "Alter course immediately away from boundary line." if pak_status in ["CRITICAL", "WARNING"] else "Monitor border proximity."
        })

        # 3. Lakshadweep Restricted Naval Exercise Area Check
        is_in_lakshadweep = point_in_polygon(latitude, longitude, GeofenceCache.RESTRICTED_LAKSHADWEEP)
        lak_dist = 0.0
        if not is_in_lakshadweep:
            lak_dist = float('inf')
            if GeofenceCache.RESTRICTED_LAKSHADWEEP:
                for i in range(len(GeofenceCache.RESTRICTED_LAKSHADWEEP) - 1):
                    d = point_to_segment_distance_km(
                        latitude, longitude,
                        GeofenceCache.RESTRICTED_LAKSHADWEEP[i][0], GeofenceCache.RESTRICTED_LAKSHADWEEP[i][1],
                        GeofenceCache.RESTRICTED_LAKSHADWEEP[i+1][0], GeofenceCache.RESTRICTED_LAKSHADWEEP[i+1][1]
                    )
                    lak_dist = min(lak_dist, d)
        
        lak_status = "INFO"
        if is_in_lakshadweep:
            lak_status = "CRITICAL"
        elif lak_dist < 10.0:
            lak_status = "WARNING"
        elif lak_dist < 25.0:
            lak_status = "WATCH"

        results.append({
            "geofence_name": "Lakshadweep Restricted Naval Zone",
            "type": "RESTRICTED",
            "distance_km": round(lak_dist, 2),
            "status": lak_status,
            "inside": is_in_lakshadweep,
            "description": "Within military naval firing exercise zone!" if is_in_lakshadweep else f"Proximity to restricted Naval Exercise Area is {round(lak_dist, 1)} km.",
            "recommended_action": "Evacuate restricted waters immediately!" if is_in_lakshadweep else "Do not enter restricted naval boundaries."
        })

        # 4. Gulf of Mannar Ecological Park Check
        is_in_gom = point_in_polygon(latitude, longitude, GeofenceCache.ECO_GULF_OF_MANNAR)
        gom_dist = 0.0
        if not is_in_gom:
            gom_dist = float('inf')
            for i in range(len(GeofenceCache.ECO_GULF_OF_MANNAR) - 1):
                d = point_to_segment_distance_km(
                    latitude, longitude,
                    GeofenceCache.ECO_GULF_OF_MANNAR[i][0], GeofenceCache.ECO_GULF_OF_MANNAR[i][1],
                    GeofenceCache.ECO_GULF_OF_MANNAR[i+1][0], GeofenceCache.ECO_GULF_OF_MANNAR[i+1][1]
                )
                gom_dist = min(gom_dist, d)
        
        gom_status = "INFO"
        if is_in_gom:
            gom_status = "WARNING"  # MPAs are usually warnings/info rather than military critical entry
        elif gom_dist < 5.0:
            gom_status = "WATCH"

        results.append({
            "geofence_name": "Gulf of Mannar Biosphere Reserve",
            "type": "ECOLOGICAL",
            "distance_km": round(gom_dist, 2),
            "status": gom_status,
            "inside": is_in_gom,
            "description": "Vessel is inside Gulf of Mannar Marine Protected Area (MPA). Strict fishing regulations apply." if is_in_gom else f"Distance to Gulf of Mannar MPA is {round(gom_dist, 1)} km.",
            "recommended_action": "Ensure no illegal trawling or anchoring on coral reefs." if is_in_gom else "Observe local environmental guidelines."
        })

        # 5. Sundarbans Ecologically Sensitive Zone Check
        is_in_sun = point_in_polygon(latitude, longitude, GeofenceCache.ECO_SUNDARBANS)
        sun_dist = 0.0
        if not is_in_sun:
            sun_dist = float('inf')
            for i in range(len(GeofenceCache.ECO_SUNDARBANS) - 1):
                d = point_to_segment_distance_km(
                    latitude, longitude,
                    GeofenceCache.ECO_SUNDARBANS[i][0], GeofenceCache.ECO_SUNDARBANS[i][1],
                    GeofenceCache.ECO_SUNDARBANS[i+1][0], GeofenceCache.ECO_SUNDARBANS[i+1][1]
                )
                sun_dist = min(sun_dist, d)

        sun_status = "INFO"
        if is_in_sun:
            sun_status = "WARNING"
        elif sun_dist < 8.0:
            sun_status = "WATCH"

        results.append({
            "geofence_name": "Sundarbans Biosphere Reserve",
            "type": "ECOLOGICAL",
            "distance_km": round(sun_dist, 2),
            "status": sun_status,
            "inside": is_in_sun,
            "description": "Vessel is inside the Sundarbans Biosphere Reserve. Speed limits and waste disposal regulations are active." if is_in_sun else f"Distance to Sundarbans MPA is {round(sun_dist, 1)} km.",
            "recommended_action": "Reduce speed below 8 knots and avoid anchoring." if is_in_sun else "Maintain standard eco-vigilance."
        })

        return results
