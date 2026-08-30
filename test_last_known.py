import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token
from app.db import db_manager, connect_to_mongo, close_mongo_connection
import uuid
from datetime import datetime, timezone, timedelta

async def test_all():
    await connect_to_mongo()
    
    # Create test user in DB
    db = db_manager.db
    fish_email = f"fish_{uuid.uuid4().hex[:6]}@orca.com"
    
    res = await db["users"].insert_one({"email": fish_email, "role": "fisherman", "full_name": "F", "password_hash": "xxx"})
    user_id = str(res.inserted_id)
    
    # Insert a 4-hour old query
    old_time = datetime.now(timezone.utc) - timedelta(hours=4)
    await db["user_queries"].insert_one({
        "user_id": user_id,
        "query_id": "test_query_123",
        "status": "done",
        "risk_level": "medium",
        "reasoning": "Test advisory",
        "recommendation": "Be careful",
        "created_at": old_time
    })
    
    fish_token = create_access_token(data={"sub": fish_email, "role": "fisherman"})
    
    with TestClient(app) as client:
        res1 = client.get(
            "/api/v1/advisory/last-known",
            headers={"Authorization": f"Bearer {fish_token}"}
        )
        assert res1.status_code == 200, res1.text
        data = res1.json()["data"]
        print("Last Known Advisory:", data)
        assert data["stale"] == True
        assert data["risk_level"] == "medium"

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_all())
