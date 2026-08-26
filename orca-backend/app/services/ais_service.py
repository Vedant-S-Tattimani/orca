"""
AIS Vessel Registry Service for ORCA
Provides a central simulated registry of vessels in Indian waters.
Each record carries provenance indicating it is SIMULATED.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import math
import logging
from app.database import db_manager

logger = logging.getLogger(__name__)

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers"""
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class AISService:
    """
    AIS registry service to serve vessel telemetry using MongoDB.
    """

    def __init__(self):
        pass

    async def get_all_vessels(self) -> List[Dict[str, Any]]:
        """Return all vessels with fresh timestamps"""
        now_str = datetime.utcnow().isoformat() + "Z"
        
        db = db_manager.get_db()
        if db is None:
            return []
            
        cursor = db["vessels"].find({}, {"_id": 0})
        vessels = await cursor.to_list(length=1000)
        
        for v in vessels:
            v["timestamp"] = now_str
            
        return vessels

    async def lookup_vessel(self, query: str) -> Optional[Dict[str, Any]]:
        """Lookup a vessel by name or MMSI"""
        query_clean = query.strip()
        now_str = datetime.utcnow().isoformat() + "Z"
        
        db = db_manager.get_db()
        if db is None:
            return None
            
        regex = {"$regex": query_clean, "$options": "i"}
        v = await db["vessels"].find_one({
            "$or": [
                {"mmsi": query_clean},
                {"name": regex}
            ]
        }, {"_id": 0})
        
        if v:
            v["timestamp"] = now_str
            
        return v

    async def find_nearby_vessels(self, latitude: float, longitude: float, radius_km: float = 100.0) -> List[Dict[str, Any]]:
        """Find all vessels within a specific radius in kilometers"""
        now_str = datetime.utcnow().isoformat() + "Z"
        
        db = db_manager.get_db()
        if db is None:
            return []
            
        cursor = db["vessels"].find({}, {"_id": 0})
        all_vessels = await cursor.to_list(length=1000)
        
        nearby = []
        for v in all_vessels:
            dist = haversine_km(latitude, longitude, v["latitude"], v["longitude"])
            if dist <= radius_km:
                v["timestamp"] = now_str
                v["distance_km"] = round(dist, 2)
                nearby.append(v)
                
        return sorted(nearby, key=lambda x: x["distance_km"])

