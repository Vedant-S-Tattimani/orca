import asyncio
import httpx

async def submit_query():
    base_url = "http://127.0.0.1:8000"
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Register a researcher
        await client.post(f"{base_url}/api/v1/auth/register", json={
            "email": "testres2@example.com",
            "password": "password",
            "full_name": "Test Res2",
            "role": "researcher"
        })
        
        login_res = await client.post(f"{base_url}/api/v1/auth/login", data={
            "username": "testres2@example.com",
            "password": "password"
        })
        token = login_res.json()["access_token"]
        
        # Submit query
        res = await client.post(
            f"{base_url}/api/query",
            json={"text": "What is the sea surface temperature and wind speed in Kochi Port?"},
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Query submitted:", res.status_code, res.json())
        
        query_id = res.json()["query_id"]
        
        # Poll for result
        for i in range(10):
            await asyncio.sleep(2)
            poll = await client.get(f"{base_url}/api/result/{query_id}")
            if poll.status_code == 200:
                print("Result:", poll.json()["risk_level"])
                break
        
        # Call historical trends again
        hist = await client.get(
            f"{base_url}/api/v1/historical/trends?location=Kochi%20Port&days=30",
            headers={"Authorization": f"Bearer {token}"}
        )
        print("Hist data first item:", hist.json().get("data", [])[-1] if hist.json().get("data") else "No data")

if __name__ == "__main__":
    asyncio.run(submit_query())
