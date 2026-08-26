"""
Port Database Service for ORCA
Provides a central source of truth for major Indian ports, search, and coordinates.
"""
from typing import Dict, Any, List, Optional
import logging
from app.database import db_manager

logger = logging.getLogger(__name__)

class PortService:
    """
    Central database service for marine port coordinates and details using MongoDB.
    """

    def __init__(self):
        pass

    async def get_all_ports(self) -> List[Dict[str, Any]]:
        """Return all ports in the database"""
        db = db_manager.get_db()
        if db is None:
            return []
        
        cursor = db["ports"].find({}, {"_id": 0})
        return await cursor.to_list(length=1000)

    async def search_ports(self, query: str) -> List[Dict[str, Any]]:
        """Search ports by name, code or ID"""
        query_clean = query.strip()
        if not query_clean:
            return []
            
        db = db_manager.get_db()
        if db is None:
            return []
            
        # Using regex for case-insensitive search
        regex = {"$regex": query_clean, "$options": "i"}
        cursor = db["ports"].find({
            "$or": [
                {"name": regex},
                {"portCode": regex},
                {"id": regex}
            ]
        }, {"_id": 0})
        
        return await cursor.to_list(length=100)

    async def get_port_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific port by exact or close name match"""
        name_clean = name.strip()
        db = db_manager.get_db()
        if db is None:
            return None
            
        regex = {"$regex": name_clean, "$options": "i"}
        port = await db["ports"].find_one({"name": regex}, {"_id": 0})
        return port

    async def get_port_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Retrieve a port by code (e.g. INBOM)"""
        code_clean = code.strip().upper()
        db = db_manager.get_db()
        if db is None:
            return None
            
        port = await db["ports"].find_one({"portCode": code_clean}, {"_id": 0})
        return port

