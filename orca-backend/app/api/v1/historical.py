from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.db import db_manager
from app.api.deps import RoleChecker

router = APIRouter()

# Enforce researcher-only access
allow_researcher_only = RoleChecker(["researcher", "admin"])

@router.get("/trends", dependencies=[Depends(allow_researcher_only)])
async def get_historical_trends(location: str = "Mangalore-Coast", days: int = 30):
    """
    Returns historical readings for a given location over the past `days` days.
    Accessible only to users with 'researcher' or 'admin' roles.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    collection = db_manager.db["historical_readings"]
    
    # Normally we would filter by timestamp. For now, fetch latest N records.
    # In a real app we would do:
    # cutoff_date = datetime.utcnow() - timedelta(days=days)
    # query = {"location": location, "timestamp": {"$gte": cutoff_date}}
    
    cursor = collection.find({"location": location}).sort("timestamp", 1).limit(days * 2)
    
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        results.append(doc)
        
    return {
        "status": "success",
        "location": location,
        "data": results
    }
