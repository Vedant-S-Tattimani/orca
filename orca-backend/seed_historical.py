import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

async def seed_historical():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["orca"]
    collection = db["historical_readings"]
    
    locations = ["Mangalore-Coast", "Kochi-Coast", "Mumbai-Coast"]
    
    # Clear existing data
    await collection.delete_many({})
    
    print("Generating mock historical data...")
    docs = []
    base_time = datetime.utcnow()
    
    for loc in locations:
        for day in range(30, -1, -1):
            for hour in [0, 6, 12, 18]:
                timestamp = base_time - timedelta(days=day, hours=hour)
                
                # Create a slight trend for realism
                sst_base = 28.0 + (day / 15.0)  # slightly warmer in past
                chlorophyll_base = 1.2 + (random.random() * 0.5)
                wind_base = 15.0 + random.uniform(-5, 10)
                
                docs.append({
                    "location": loc,
                    "timestamp": timestamp,
                    "sst": round(sst_base + random.uniform(-0.5, 0.5), 2),
                    "chlorophyll": round(chlorophyll_base, 2),
                    "wind_speed": round(wind_base, 2),
                    "wave_height": round(wind_base * 0.1, 2)
                })
                
    await collection.insert_many(docs)
    print(f"Successfully inserted {len(docs)} historical records.")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_historical())
