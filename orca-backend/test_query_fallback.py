import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token
from app.db import db_manager, connect_to_mongo, close_mongo_connection
import uuid
from datetime import datetime, timezone, timedelta
import unittest.mock as mock
import sys

async def test_fallback():
    await connect_to_mongo()
    db = db_manager.db
    fish_email = f"fish_{uuid.uuid4().hex[:6]}@orca.com"
    res = await db["users"].insert_one({"email": fish_email, "role": "fisherman", "full_name": "F", "password_hash": "xxx"})
    user_id = str(res.inserted_id)
    
    old_time = datetime.now(timezone.utc) - timedelta(hours=4)
    await db["user_queries"].insert_one({
        "user_id": user_id,
        "query_id": "test_query_123",
        "status": "done",
        "risk_level": "medium",
        "reasoning": "Previous test advisory reasoning",
        "recommendation": "Be careful",
        "created_at": old_time
    })
    
    fish_token = create_access_token(data={"sub": fish_email, "role": "fisherman"})
    
    with TestClient(app) as client:
        # Mock planner to throw an exception
        with mock.patch('app.orchestrator.planner.Planner.create_agent_plan', side_effect=Exception('Timeout simulated!')):
            res1 = client.post(
                "/api/query",
                headers={"Authorization": f"Bearer {fish_token}"},
                json={"text": "Is it safe in Kochi?", "lat": 9.9, "lon": 76.2}
            )
            assert res1.status_code == 200, res1.text
            query_id = res1.json()["query_id"]
            
            # Poll result
            import time
            for _ in range(5):
                res2 = client.get(f"/api/result/{query_id}")
                data = res2.json()
                if data["status"] != "processing":
                    break
                time.sleep(1)
            
            assert data.get("stale") == True
            assert "Live retrieval failed" in data["reasoning"]
            print("TEST PASSED: Fallback condition successful")

    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_fallback())
