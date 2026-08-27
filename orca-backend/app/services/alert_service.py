import logging
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Any
from app.db import db_manager

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.collection_name = "hazard_advisories"

    async def push_alert(self, alert_data: Dict[str, Any]) -> str:
        """Push a new alert into the hazard_advisories collection."""
        db = db_manager.db
        if db is None:
            logger.error("Database not initialized.")
            raise Exception("Database not connected")
            
        collection = db[self.collection_name]
        
        alert_id = f"alert-db-{uuid.uuid4().hex[:8]}"
        doc = {
            "id": alert_id,
            "title": alert_data.get("title", "Advisory"),
            "severity": alert_data.get("severity", "WARNING"),
            "location": alert_data.get("location", "Unknown Location"),
            "time": datetime.utcnow().isoformat() + "Z",
            "hazard": alert_data.get("hazard", "Unknown Hazard"),
            "recommended_action": alert_data.get("recommended_action", "Exercise caution"),
            "provenance": alert_data.get("provenance", "ORCA Alert System"),
            "created_at": datetime.utcnow()
        }
        
        await collection.insert_one(doc)
        logger.info(f"Pushed new hazard advisory alert: {alert_id}")
        
        # Dispatch SMS alerts via Twilio
        await self._dispatch_sms(doc)
        
        # Return the doc without internal mongodb metadata
        doc.pop("_id", None)
        return doc

    async def _dispatch_sms(self, alert_data: Dict[str, Any]):
        """Find subscribers for this location and send SMS via Twilio."""
        db = db_manager.db
        if db is None:
            return
            
        subscriptions = db["alert_subscriptions"]
        location = alert_data.get("location")
        if not location:
            return
            
        # Find subscribers for this location
        cursor = subscriptions.find({"location": location})
        subscribers = await cursor.to_list(length=1000)
        
        if not subscribers:
            logger.info(f"No SMS subscribers found for location: {location}")
            return
            
        # Initialize Twilio (using env vars if available, or mock if not)
        import os
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
        
        if not account_sid or not auth_token:
            logger.warning("Twilio credentials not found in ENV. Skipping SMS dispatch.")
            return
            
        try:
            client = Client(account_sid, auth_token)
            
            message_body = (
                f"ORCA Marine Alert: {alert_data.get('severity')} hazard in {location}.\n"
                f"{alert_data.get('title')}\n"
                f"Action: {alert_data.get('recommended_action')}"
            )
            
            for sub in subscribers:
                to_phone = sub.get("phone_number")
                if to_phone:
                    message = client.messages.create(
                        body=message_body,
                        from_=from_phone,
                        to=to_phone
                    )
                    logger.info(f"Sent SMS to {to_phone}. Twilio SID: {message.sid}")
                    
        except Exception as e:
            logger.error(f"Failed to dispatch SMS via Twilio: {e}")

    async def get_active_alerts(self, max_age_hours: int = 48) -> List[Dict[str, Any]]:
        """Fetch active alerts created within the max age window."""
        db = db_manager.db
        if db is None:
            logger.warning("Database not connected, returning empty list for active alerts.")
            return []
            
        collection = db[self.collection_name]
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        cursor = collection.find({"created_at": {"$gte": cutoff_time}}).sort("created_at", -1)
        
        active_alerts = []
        async for doc in cursor:
            doc.pop("_id", None)
            doc.pop("created_at", None)
            active_alerts.append(doc)
            
        return active_alerts
