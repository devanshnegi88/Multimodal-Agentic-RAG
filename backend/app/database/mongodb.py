"""
MongoDB async client using Motor
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.utils.logger import logger

client: AsyncIOMotorClient = None


async def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    logger.info(f"Connected to MongoDB at {settings.MONGODB_URL}")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")


def get_database():
    return client[settings.MONGODB_DB_NAME]
