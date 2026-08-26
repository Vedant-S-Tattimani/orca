import asyncio
import os
import sys

# Add parent dir to path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db_manager
from app.services.port_service import INDIAN_PORTS
from app.services.ais_service import SIMULATED_VESSELS
from app.services.geospatial_service import (
    IMBL_SRI_LANKA, IMBL_PAKISTAN, 
    ECO_GULF_OF_MANNAR, ECO_SUNDARBANS, RESTRICTED_LAKSHADWEEP
)

async def init_mongo():
    print("Connecting to MongoDB...")
    await db_manager.connect_db()
    db = db_manager.get_db()
    
    if db is None:
        print("Failed to get DB instance")
        return

    print("Initializing collections...")

    # Ports
    ports_coll = db["ports"]
    if await ports_coll.count_documents({}) == 0:
        print(f"Inserting {len(INDIAN_PORTS)} ports...")
        await ports_coll.insert_many(INDIAN_PORTS)
        
        # Create indexes
        await ports_coll.create_index("id", unique=True)
        await ports_coll.create_index("portCode")
        await ports_coll.create_index("name")
    else:
        print("Ports collection already populated.")

    # Vessels
    vessels_coll = db["vessels"]
    if await vessels_coll.count_documents({}) == 0:
        print(f"Inserting {len(SIMULATED_VESSELS)} vessels...")
        await vessels_coll.insert_many(SIMULATED_VESSELS)
        
        # Create indexes
        await vessels_coll.create_index("mmsi", unique=True)
    else:
        print("Vessels collection already populated.")

    # Geofences
    geofences = [
        {"id": "IMBL_SRI_LANKA", "type": "boundary", "name": "IMBL Sri Lanka", "coordinates": IMBL_SRI_LANKA},
        {"id": "IMBL_PAKISTAN", "type": "boundary", "name": "IMBL Pakistan", "coordinates": IMBL_PAKISTAN},
        {"id": "ECO_GULF_OF_MANNAR", "type": "eco_zone", "name": "Gulf of Mannar Ecological Park", "coordinates": ECO_GULF_OF_MANNAR},
        {"id": "ECO_SUNDARBANS", "type": "eco_zone", "name": "Sundarbans Ecologically Sensitive Zone", "coordinates": ECO_SUNDARBANS},
        {"id": "RESTRICTED_LAKSHADWEEP", "type": "restricted", "name": "Lakshadweep Naval Exercise Zone", "coordinates": RESTRICTED_LAKSHADWEEP}
    ]
    geofences_coll = db["geofences"]
    if await geofences_coll.count_documents({}) == 0:
        print(f"Inserting {len(geofences)} geofences...")
        await geofences_coll.insert_many(geofences)
        await geofences_coll.create_index("id", unique=True)
    else:
        print("Geofences collection already populated.")
        
    print("MongoDB initialization complete.")
    await db_manager.close_db()

if __name__ == "__main__":
    asyncio.run(init_mongo())
