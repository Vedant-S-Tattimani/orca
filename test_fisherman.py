import asyncio
import httpx
from datetime import datetime

async def test_fisherman_role():
    base_url = "http://127.0.0.1:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. Register a fisherman
        email = f"testfisherman{datetime.utcnow().timestamp()}@example.com"
        reg_data = {
            "email": email,
            "password": "password123",
            "full_name": "Test Fisherman",
            "role": "fisherman"
        }
        print(f"Registering fisherman {email}...")
        reg_res = await client.post(f"{base_url}/api/v1/auth/register", json=reg_data)
        if reg_res.status_code != 200:
            print("Registration failed:", reg_res.text)
            return

        # 2. Login to get JWT
        login_data = {
            "username": email,
            "password": "password123"
        }
        print("Logging in...")
        login_res = await client.post(f"{base_url}/api/v1/auth/login", data=login_data)
        if login_res.status_code != 200:
            print("Login failed:", login_res.text)
            return
            
        token = login_res.json()["access_token"]
        print(f"Got JWT Token: {token[:20]}...")
        
        # 3. Try to access coastal authority endpoint
        headers = {"Authorization": f"Bearer {token}"}
        advisory_data = {
            "title": "Test Advisory",
            "severity": "HIGH",
            "location": "Kerala",
            "hazard": "Test Hazard",
            "recommended_action": "Stay safe"
        }
        print("Attempting to create manual advisory (should fail with 403)...")
        advisory_res = await client.post(f"{base_url}/api/v1/alerts/advisory", json=advisory_data, headers=headers)
        
        print(f"Response Code: {advisory_res.status_code}")
        print(f"Response Body: {advisory_res.text}")

if __name__ == "__main__":
    asyncio.run(test_fisherman_role())
