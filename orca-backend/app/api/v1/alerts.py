import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

class SubscribeRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to send SMS to")
    location: str = Field(..., description="Location to monitor")

@router.post("/subscribe", summary="Subscribe to push alerts for a location")
async def subscribe_alerts(request: SubscribeRequest, db = Depends(get_db)):
    """
    Subscribe a phone number to receive alerts for a specific location.
    """
    from datetime import datetime
    
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    collection = db["alert_subscriptions"]
    
    # Check if already subscribed
    existing = await collection.find_one({
        "phone_number": request.phone_number,
        "location": request.location
    })
    
    if existing:
        return {"status": "ok", "message": "Already subscribed to this location"}
        
    doc = {
        "phone_number": request.phone_number,
        "location": request.location,
        "created_at": datetime.utcnow()
    }
    
    await collection.insert_one(doc)
    logger.info(f"Subscribed {request.phone_number} to alerts for {request.location}")
    
    return {"status": "ok", "message": f"Successfully subscribed to alerts for {request.location}"}
