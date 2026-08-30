from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging
from bson import ObjectId

from app.api.deps import get_current_user
from app.db import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Trips"])

class TripStartRequest(BaseModel):
    vessel_id: Optional[str] = None
    expected_return: Optional[str] = None
    destination: Optional[str] = None

class TripPingRequest(BaseModel):
    lat: float
    lon: float

@router.post("")
async def start_trip(
    request: TripStartRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    POST /api/v1/trips
    Start a new fishing trip.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    now = datetime.now(timezone.utc)
    user_id = str(current_user["_id"])
    
    trip_doc = {
        "user_id": user_id,
        "vessel_id": request.vessel_id,
        "destination": request.destination,
        "expected_return": request.expected_return,
        "start_time": now,
        "end_time": None,
        "status": "active",
        "route": []
    }
    
    result = await db_manager.db["trips"].insert_one(trip_doc)
    
    return {
        "status": "success",
        "trip_id": str(result.inserted_id),
        "message": "Trip started successfully."
    }


@router.post("/{trip_id}/ping")
async def ping_trip(
    trip_id: str,
    request: TripPingRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    POST /api/v1/trips/{trip_id}/ping
    Log a location ping for an active trip.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    try:
        obj_id = ObjectId(trip_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trip ID")
        
    user_id = str(current_user["_id"])
    now = datetime.now(timezone.utc)
    
    ping_point = {
        "lat": request.lat,
        "lon": request.lon,
        "timestamp": now
    }
    
    result = await db_manager.db["trips"].update_one(
        {"_id": obj_id, "user_id": user_id, "status": "active"},
        {"$push": {"route": ping_point}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Active trip not found")
        
    return {"status": "success", "message": "Location logged."}


@router.post("/{trip_id}/end")
async def end_trip(
    trip_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    POST /api/v1/trips/{trip_id}/end
    End an active fishing trip.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    try:
        obj_id = ObjectId(trip_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid trip ID")
        
    user_id = str(current_user["_id"])
    now = datetime.now(timezone.utc)
    
    result = await db_manager.db["trips"].update_one(
        {"_id": obj_id, "user_id": user_id, "status": "active"},
        {"$set": {"status": "completed", "end_time": now}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Active trip not found")
        
    return {"status": "success", "message": "Trip ended successfully."}
