import asyncio
import httpx

async def test_historical():
    base_url = "http://127.0.0.1:8000"
    async with httpx.AsyncClient() as client:
        # Register a researcher
        reg_res = await client.post(f"{base_url}/api/v1/auth/register", json={
            "email": "testresearcher@example.com",
            "password": "password",
            "full_name": "Test Researcher",
            "role": "researcher"
        })
        
        # Login
        login_res = await client.post(f"{base_url}/api/v1/auth/login", data={
            "username": "testresearcher@example.com",
            "password": "password"
        })
        if login_res.status_code != 200:
            print("Login failed", login_res.text)
            return
            
        token = login_res.json()["access_token"]
        
        # Call historical trends
        res = await client.get(
            f"{base_url}/api/v1/historical/trends?location=Kochi%20Port&days=30",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Status:", res.status_code)
        
        data = res.json()
        print("Response keys:", data.keys())
        if "data" in data and len(data["data"]) > 0:
            print("First item:", data["data"][0])
        else:
            print("No data items found.")

if __name__ == "__main__":
    asyncio.run(test_historical())
