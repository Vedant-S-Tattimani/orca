import logging
from typing import Optional, Dict, Any
from app.db import db_manager
from datetime import datetime

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.collection_name = "users"

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        db = db_manager.db
        if db is None:
            return None
        collection = db[self.collection_name]
        return await collection.find_one({"email": email})

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        db = db_manager.db
        if db is None:
            raise Exception("Database not connected")
            
        collection = db[self.collection_name]
        
        user_doc = {
            "email": user_data["email"],
            "hashed_password": user_data["hashed_password"],
            "full_name": user_data.get("full_name", ""),
            "role": user_data.get("role", "fisherman"),
            "disabled": user_data.get("disabled", False),
            "created_at": datetime.utcnow()
        }
        
        result = await collection.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        return user_doc
