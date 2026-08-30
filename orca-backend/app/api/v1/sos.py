"""
Fisherman-initiated SOS and Distress endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging
from bson import ObjectId

from app.api.deps import get_current_user, RoleChecker
from app.db import db_manager
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["SOS & Distress"])

class SOSRequest(BaseModel):
    lat: float
    lon: float
    timestamp: Optional[str] = None
    message: Optional[str] = Field(None, max_length=500)

class SOSResolve(BaseModel):
    resolution_note: Optional[str] = Field(None, max_length=500)

@router.post("")
async def trigger_sos(
    request: SOSRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """
    POST /api/v1/sos
    Trigger an emergency distress signal. Available to any logged-in user.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")

    now = datetime.now(timezone.utc)
    user_id = str(current_user["_id"])
    
    # Write to sos_alerts collection
    sos_doc = {
        "user_id": user_id,
        "user_email": current_user.get("email"),
        "user_name": current_user.get("full_name"),
        "user_phone": current_user.get("phone"),
        "location": {"type": "Point", "coordinates": [request.lon, request.lat]},
        "message": request.message,
        "timestamp": request.timestamp or now.isoformat(),
        "created_at": now,
        "resolved": False,
        "resolved_by": None,
        "resolved_at": None,
        "resolution_note": None
    }
    
    try:
        result = await db_manager.db["sos_alerts"].insert_one(sos_doc)
        sos_id = str(result.inserted_id)
        
        # Trigger highest priority Twilio dispatch via background task
        background_tasks.add_task(dispatch_sos_alerts, sos_id, sos_doc)
        
        # Acknowledge payload
        return {
            "status": "success",
            "sos_id": sos_id,
            "message": "SOS received. Help is being dispatched.",
            "instructions": "Keep your phone on. Authorities have your location."
        }
    except Exception as e:
        logger.error(f"Failed to process SOS: {e}")
        raise HTTPException(status_code=500, detail="Failed to process SOS signal")


async def dispatch_sos_alerts(sos_id: str, sos_doc: Dict[str, Any]):
    """Background task to dispatch Twilio alerts to authorities."""
    alert_service = AlertService()
    try:
        # Create an alert doc tailored for SOS
        alert_payload = {
            "title": f"🆘 SOS DISTRESS: {sos_doc.get('user_name', 'Unknown Vessel')}",
            "severity": "CRITICAL",
            "location": f"Lat: {sos_doc['location']['coordinates'][1]}, Lon: {sos_doc['location']['coordinates'][0]}",
            "hazard": f"Manual SOS triggered. Message: {sos_doc.get('message', 'No message')}. Phone: {sos_doc.get('user_phone')}",
            "recommended_action": "Immediate Coast Guard dispatch required.",
            "provenance": "Fisherman SOS App"
        }
        
        # We want to dispatch this immediately to all registered coastal authorities.
        # Since AlertService._dispatch_sms normally relies on location subscriptions,
        # we'll specifically look for users with 'coastal_authority' role and alert them.
        
        db = db_manager.db
        if db is not None:
            cursor = db["users"].find({"role": {"$in": ["coastal_authority", "disaster_management"]}})
            authorities = await cursor.to_list(length=50)
            
            import os
            from twilio.rest import Client
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            from_phone = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
            
            if account_sid and auth_token:
                client = Client(account_sid, auth_token)
                message_body = (
                    f"{alert_payload['title']}\n"
                    f"Loc: {alert_payload['location']}\n"
                    f"Detail: {alert_payload['hazard']}"
                )
                for auth in authorities:
                    phone = auth.get("phone")
                    if phone:
                        try:
                            client.messages.create(body=message_body, from_=from_phone, to=phone)
                            logger.info(f"Dispatched SOS {sos_id} to authority {auth.get('email')}")
                        except Exception as te:
                            logger.error(f"Twilio SOS dispatch failed for {phone}: {te}")
            else:
                logger.warning("Twilio credentials missing. Skipped authority SMS dispatch.")
        
        # Also push a standard DB alert so it appears on dashboards
        await alert_service.push_alert(alert_payload)
        
    except Exception as e:
        logger.error(f"Error in background SOS dispatch: {e}")


@router.get("")
async def get_sos_alerts(
    current_user: Dict = Depends(RoleChecker(["coastal_authority", "disaster_management"]))
):
    """
    GET /api/v1/sos
    View all recent SOS alerts (unresolved first, then by recency).
    Requires coastal_authority role.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    cursor = db_manager.db["sos_alerts"].find({}).sort([("resolved", 1), ("created_at", -1)]).limit(50)
    alerts = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if "created_at" in doc:
            doc["created_at"] = doc["created_at"].isoformat()
        alerts.append(doc)
        
    return {"status": "success", "data": alerts}


@router.patch("/{sos_id}/resolve")
async def resolve_sos(
    sos_id: str,
    payload: SOSResolve,
    current_user: Dict = Depends(get_current_user)
):
    """
    PATCH /api/v1/sos/{id}/resolve
    Mark an SOS alert as handled/resolved.
    """
    if db_manager.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    try:
        obj_id = ObjectId(sos_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid SOS ID format")
        
    # Check authorization
    sos_alert = await db_manager.db["sos_alerts"].find_one({"_id": obj_id})
    if not sos_alert:
        raise HTTPException(status_code=404, detail="SOS not found")
        
    user_role = current_user.get("role", "")
    is_authority = user_role in ["coastal_authority", "disaster_management"]
    is_owner = sos_alert.get("user_id") == current_user.get("sub")
    
    if not (is_authority or is_owner):
        raise HTTPException(status_code=403, detail="Not authorized to resolve this SOS")
        
    result = await db_manager.db["sos_alerts"].update_one(
        {"_id": obj_id},
        {"$set": {
            "resolved": True,
            "resolved_by": current_user.get("email"),
            "resolved_at": datetime.now(timezone.utc),
            "resolution_note": payload.resolution_note
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SOS alert not found")
        
    return {"status": "success", "message": "SOS resolved successfully"}
