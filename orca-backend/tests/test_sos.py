import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.auth_service import create_access_token
from app.db import db_manager, connect_to_mongo, close_mongo_connection
import uuid

def run_tests():
    with TestClient(app) as client:
        # 1. Trigger SOS (mock current_user)
        from app.api.deps import get_current_user
        
        # Override get_current_user for the SOS trigger
        app.dependency_overrides[get_current_user] = lambda: {
            "_id": "test_fish_id", "email": "fisherman@orca.com", 
            "role": "fisherman", "full_name": "Test Fish", "phone": "+123"
        }
        
        res1 = client.post(
            "/api/v1/sos",
            json={
                "lat": 10.5,
                "lon": 75.5,
                "message": "Engine failure taking on water"
            }
        )
        assert res1.status_code == 200, res1.text
        sos_data = res1.json()
        print("SOS Trigger Response:", sos_data)
        sos_id = sos_data["sos_id"]
        
        # 2. View SOS list (need to override RoleChecker, which is tricky)
        # Instead, let's just use the DB directly for verification, or use a real token
        pass

@pytest.mark.asyncio
async def test_all():
    await connect_to_mongo()
    
    # Create test users in DB
    db = db_manager.db
    fish_email = f"fish_{uuid.uuid4().hex[:6]}@orca.com"
    auth_email = f"auth_{uuid.uuid4().hex[:6]}@orca.com"
    
    await db["users"].insert_one({"email": fish_email, "role": "fisherman", "full_name": "F", "password_hash": "xxx"})
    await db["users"].insert_one({"email": auth_email, "role": "coastal_authority", "full_name": "A", "password_hash": "xxx"})
    
    fish_token = create_access_token(data={"sub": fish_email, "role": "fisherman"})
    auth_token = create_access_token(data={"sub": auth_email, "role": "coastal_authority"})
    
    with TestClient(app) as client:
        res1 = client.post(
            "/api/v1/sos",
            headers={"Authorization": f"Bearer {fish_token}"},
            json={"lat": 10.5, "lon": 75.5, "message": "Engine failure taking on water"}
        )
        print("Trigger:", res1.json())
        sos_id = res1.json()["sos_id"]
        
        res2 = client.get("/api/v1/sos", headers={"Authorization": f"Bearer {auth_token}"})
        print("List:", len(res2.json()["data"]), "items")
        
        res3 = client.patch(
            f"/api/v1/sos/{sos_id}/resolve",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"resolution_note": "Rescued"}
        )
        print("Resolve:", res3.json())
        
        res4 = client.get("/api/v1/sos", headers={"Authorization": f"Bearer {auth_token}"})
        resolved_sos = [a for a in res4.json()["data"] if a["_id"] == sos_id][0]
        print("Resolved SOS status:", resolved_sos["resolved"])

    await close_mongo_connection()