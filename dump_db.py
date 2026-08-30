import asyncio
from pymongo import MongoClient
import json
from bson import json_util

def dump_db():
    print("Connecting to MongoDB...")
    # The actual configured database URL
    client = MongoClient("mongodb+srv://jotmarr8_db_user:1uQpFd0Jq0gyMVhr@orca.ijuokku.mongodb.net/?appName=orca1uQpFd0Jq0gyMVhr")
    db = client["orca"]
    
    print("\n--- Latest historical_readings Document ---")
    reading_doc = db["historical_readings"].find_one(sort=[("_id", -1)])
    if reading_doc:
        print(json.dumps(json.loads(json_util.dumps(reading_doc)), indent=2))
    else:
        print("No historical_readings found!")
        
    print("\n--- Latest user_queries Document ---")
    query_doc = db["user_queries"].find_one(sort=[("_id", -1)])
    if query_doc:
        print(json.dumps(json.loads(json_util.dumps(query_doc)), indent=2))
    else:
        print("No user_queries found!")

if __name__ == "__main__":
    dump_db()
