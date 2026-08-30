import asyncio
import httpx
from pymongo import MongoClient

async def test_db_insertion():
    base_url = "http://127.0.0.1:8000"
    
    # 1. Fire a query to ORCA
    query_data = {
        "text": "Is it safe to go fishing near Kochi tomorrow?",
        "language": "en"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("Submitting query to ORCA...")
        res = await client.post(f"{base_url}/api/query", json=query_data)
        if res.status_code != 200:
            print("Failed to query:", res.text)
            return
            
        data = res.json()
        query_id = data.get("query_id")
        print(f"Query accepted (ID: {query_id}), polling for completion...")
        
        for _ in range(30):
            status_res = await client.get(f"{base_url}/api/result/{query_id}")
            if status_res.status_code == 200:
                card = status_res.json()
                if card.get("status") == "done":
                    print("Query processing complete!")
                    break
            await asyncio.sleep(2)
        else:
            print("Query timed out or never reached 'done' status.")
        
    # 2. Check MongoDB for user_queries and historical_readings
    print("Checking MongoDB...")
    client = MongoClient("mongodb+srv://jotmarr8_db_user:1uQpFd0Jq0gyMVhr@orca.ijuokku.mongodb.net/?appName=orca1uQpFd0Jq0gyMVhr")
    db = client["test"] # orca.ijuokku connects to 'test' by default usually, wait, db = client.get_default_database() in app/db.py uses test when no db in path. Let me try test.
    # Wait, in db.py:
    # if settings.MONGODB_URL and "/" in settings.MONGODB_URL.split("?")[-1]: 
    #   db_manager.db = db_manager.client.get_default_database()
    # else: 
    #   db_manager.db = db_manager.client["orca"]
    # So the db name used by the backend is "orca" since there is no path.
    db = client["orca"]
    
    print("\n--- Latest user_queries Document ---")
    query_doc = db["user_queries"].find_one(sort=[("created_at", -1)])
    if query_doc:
        query_doc["_id"] = str(query_doc["_id"])
        print(query_doc)
    else:
        print("No user_queries found!")
        
    print("\n--- Latest historical_readings Document ---")
    reading_doc = db["historical_readings"].find_one(sort=[("created_at", -1)])
    if reading_doc:
        reading_doc["_id"] = str(reading_doc["_id"])
        print(reading_doc)
    else:
        print("No historical_readings found!")

if __name__ == "__main__":
    asyncio.run(test_db_insertion())
