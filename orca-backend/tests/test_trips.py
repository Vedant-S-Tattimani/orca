import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token
from app.db import db_manager, connect_to_mongo, close_mongo_connection
import uuid

@pytest.mark.asyncio
async def test_trips():
    await connect_to_mongo()
    
    # Create test user in DB
    db = db_manager.db
    fish_email = f"fish_trip_{uuid.uuid4().hex[:6]}@orca.com"
    
    res = await db["users"].insert_one({"email": fish_email, "role": "fisherman", "full_name": "Trip Fish", "password_hash": "xxx"})
    
    fish_token = create_access_token(data={"sub": fish_email, "role": "fisherman"})
    
    with TestClient(app) as client:
        # Start Trip
        res1 = client.post(
            "/api/v1/trips",
            headers={"Authorization": f"Bearer {fish_token}"},
            json={"destination": "Deep Sea", "expected_return": "Tomorrow"}
        )
        assert res1.status_code == 200, res1.text
        trip_data = res1.json()
        print("Start Trip:", trip_data)
        trip_id = trip_data["trip_id"]
        
        # Ping
        res2 = client.post(
            f"/api/v1/trips/{trip_id}/ping",
            headers={"Authorization": f"Bearer {fish_token}"},
            json={"lat": 10.1, "lon": 75.1}
        )
        assert res2.status_code == 200, res2.text
        print("Ping 1:", res2.json())
        
        # Ping 2
        res3 = client.post(
            f"/api/v1/trips/{trip_id}/ping",
            headers={"Authorization": f"Bearer {fish_token}"},
            json={"lat": 10.2, "lon": 75.2}
        )
        assert res3.status_code == 200, res3.text
        print("Ping 2:", res3.json())
        
        # Verify in DB
        doc = await db["trips"].find_one({"_id": res.inserted_id}) # Wait, res.inserted_id is user_id
        from bson import ObjectId
        trip_doc = await db["trips"].find_one({"_id": ObjectId(trip_id)})
        print("Trip route length:", len(trip_doc["route"]))
        assert len(trip_doc["route"]) == 2
        
        # End trip
        res4 = client.post(
            f"/api/v1/trips/{trip_id}/end",
            headers={"Authorization": f"Bearer {fish_token}"}
        )
        assert res4.status_code == 200, res4.text
        print("End trip:", res4.json())
        
        trip_doc2 = await db["trips"].find_one({"_id": ObjectId(trip_id)})
        print("Final Status:", trip_doc2["status"])
        assert trip_doc2["status"] == "completed"

    await close_mongo_connection()