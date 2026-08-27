import logging
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request
from app.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_manager = MongoDB()

async def connect_to_mongo():
    """Create database connection."""
    mongodb_url = settings.MONGODB_URL or "mongodb://localhost:27017"
    try:
        logger.info(f"Connecting to MongoDB...")
        db_manager.client = AsyncIOMotorClient(mongodb_url)
        
        # Determine database name
        if settings.MONGODB_URL and "/" in settings.MONGODB_URL.split("?")[-1]:
            # Extracted from standard connection string format if provided
            db_manager.db = db_manager.client.get_default_database()
        else:
            db_manager.db = db_manager.client["orca"]
            
        logger.info(f"Connected to MongoDB database: {db_manager.db.name}")
        
        # Create indexes
        try:
            # 1. TTL index for hazard_advisories (expires after 30 days = 2592000 seconds)
            await db_manager.db["hazard_advisories"].create_index(
                "created_at", expireAfterSeconds=2592000
            )
            # 2. Location index for faster querying
            await db_manager.db["hazard_advisories"].create_index("location")
            await db_manager.db["historical_readings"].create_index("location")
            await db_manager.db["alert_subscriptions"].create_index("location")
            logger.info("MongoDB indexes verified/created successfully.")
        except Exception as idx_err:
            logger.warning(f"Failed to create some MongoDB indexes: {idx_err}")
            
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close database connection."""
    if db_manager.client:
        logger.info("Closing MongoDB connection...")
        db_manager.client.close()
        logger.info("MongoDB connection closed.")

async def get_db():
    """
    FastAPI dependency that provides the database instance.
    Usage:
        @app.get("/")
        async def root(db = Depends(get_db)):
            ...
    """
    if db_manager.db is None:
        # Failsafe in case it wasn't initialized in startup event
        await connect_to_mongo()
    return db_manager.db
