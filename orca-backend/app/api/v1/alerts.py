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

from app.api.deps import RoleChecker
from typing import List

allow_coastal_auth = RoleChecker(["coastal_authority", "admin"])

class ManualAdvisoryRequest(BaseModel):
    title: str = Field(..., description="Title of the advisory")
    severity: str = Field(..., description="Severity (HIGH, EXTREME, etc.)")
    location: str = Field(..., description="Affected location/region")
    hazard: str = Field(..., description="Description of the hazard")
    recommended_action: str = Field(..., description="Action to take")

@router.post("/advisory", summary="Manual advisory override for coastal authorities", dependencies=[Depends(allow_coastal_auth)])
async def create_manual_advisory(request: ManualAdvisoryRequest, db = Depends(get_db)):
    """
    Create a manual hazard advisory, overriding or supplementing the automated Risk Engine.
    Requires coastal_authority role.
    """
    from app.services.alert_service import AlertService
    alert_svc = AlertService()
    
    alert_data = request.dict()
    alert_data["provenance"] = "Coastal Authority (Manual Override)"
    
    try:
        alert_id = await alert_svc.push_alert(alert_data)
        return {"status": "ok", "message": "Manual advisory dispatched", "alert_id": alert_id}
    except Exception as e:
        logger.error(f"Failed to dispatch manual advisory: {e}")
        raise HTTPException(status_code=500, detail="Failed to dispatch advisory")

@router.get("/audit", summary="Alert dispatch audit log", dependencies=[Depends(allow_coastal_auth)])
async def get_alert_audit_log(limit: int = 50, db = Depends(get_db)):
    """
    View a record of all dispatched alerts.
    Requires coastal_authority role.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    cursor = db["hazard_advisories"].find({}).sort("created_at", -1).limit(limit)
    advisories = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings
    for adv in advisories:
        adv["_id"] = str(adv["_id"])
        
    return {"status": "ok", "count": len(advisories), "audit_log": advisories}

@router.get("/region", summary="Region-wide advisory view", dependencies=[Depends(allow_coastal_auth)])
async def get_region_wide_advisories(db = Depends(get_db)):
    """
    View all active advisories across all zones at once.
    Requires coastal_authority role.
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    # Active advisories are those that haven't expired (TTL index handles deletion, so all in collection are active)
    cursor = db["hazard_advisories"].find({}).sort("created_at", -1)
    advisories = await cursor.to_list(length=100)
    
    for adv in advisories:
        adv["_id"] = str(adv["_id"])
        
    return {"status": "ok", "active_advisories": advisories}
