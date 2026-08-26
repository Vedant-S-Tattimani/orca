import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_db(cls):
        """Create database connection."""
        if not settings.MONGODB_URL:
            logger.warning("MONGODB_URL is not set. Database operations will fail.")
            return

        try:
            logger.info("Connecting to MongoDB...")
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            try:
                cls.db = cls.client.get_default_database()
            except Exception:
                # Fallback if no database provided in URI
                cls.db = cls.client["orca"]
            logger.info(f"Connected to MongoDB database: {cls.db.name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

    @classmethod
    async def close_db(cls):
        """Close database connection."""
        if cls.client:
            logger.info("Closing MongoDB connection...")
            cls.client.close()
            logger.info("MongoDB connection closed.")

    @classmethod
    def get_db(cls):
        """Get the database instance."""
        return cls.db

db_manager = DatabaseManager()
