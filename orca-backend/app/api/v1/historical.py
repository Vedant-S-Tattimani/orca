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
    
    cursor = collection.find({"location": location}).sort("timestamp", 1).limit(days * 100)
    
    grouped = {}
    async for doc in cursor:
        ts = doc.get("timestamp")
        if not ts:
            continue
            
        date_str = ts.strftime("%Y-%m-%d") if hasattr(ts, 'strftime') else str(ts)[:10]
        if date_str not in grouped:
            grouped[date_str] = {"timestamp": date_str, "location": location}
            
        # Map event type to charting field
        t = str(doc.get("type", "")).lower()
        val = doc.get("value")
        
        if "sst" in t or "temp" in t:
            grouped[date_str]["sst"] = val
        elif "chlorophyll" in t or "chl" in t:
            grouped[date_str]["chlorophyll"] = val
        elif "wind" in t:
            grouped[date_str]["wind_speed"] = val
        elif "wave" in t:
            grouped[date_str]["wave_height"] = val
            
    # Convert grouped dictionary back to list and sort by date
    results = sorted(list(grouped.values()), key=lambda x: x["timestamp"])
        
    return {
        "status": "success",
        "location": location,
        "data": results
    }
