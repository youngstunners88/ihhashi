"""
Database initialization module with environment-driven MongoDB settings.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

logger = logging.getLogger(__name__)

# Global client instance
_mongo_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_db() -> AsyncIOMotorDatabase:
    """
    Connect to MongoDB using environment-driven settings.
    
    Returns:
        AsyncIOMotorDatabase: The database instance.
    """
    global _mongo_client, _db
    
    if _mongo_client is not None:
        return _db
    
    # Use settings from config.py - all env-driven
    connection_options = settings.mongodb_connection_options
    
    logger.info(
        "Connecting to MongoDB with pool settings: "
        f"maxPoolSize={connection_options['maxPoolSize']}, "
        f"minPoolSize={connection_options['minPoolSize']}, "
        f"maxIdleTimeMS={connection_options['maxIdleTimeMS']}, "
        f"waitQueueTimeoutMS={connection_options['waitQueueTimeoutMS']}, "
        f"connectTimeoutMS={connection_options['connectTimeoutMS']}, "
        f"socketTimeoutMS={connection_options['socketTimeoutMS']}, "
        f"serverSelectionTimeoutMS={connection_options['serverSelectionTimeoutMS']}"
    )
    
    _mongo_client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        **connection_options
    )
    
    _db = _mongo_client[settings.MONGODB_DB_NAME]
    
    # Verify connection
    await _mongo_client.admin.command("ping")
    logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")
    
    return _db


async def disconnect_db() -> None:
    """Close MongoDB connection."""
    global _mongo_client, _db
    
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _db = None
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """
    Get the database instance.
    
    Raises:
        RuntimeError: If database is not connected.
    
    Returns:
        AsyncIOMotorDatabase: The database instance.
    """
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Get a database session as an async context manager.
    
    Yields:
        AsyncIOMotorDatabase: The database instance.
    """
    db = get_db()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise


async def check_db_health() -> dict:
    """
    Check database health status.
    
    Returns:
        dict: Health status information.
    """
    try:
        if _mongo_client is None:
            return {
                "status": "disconnected",
                "error": "Client not initialized"
            }
        
        # Ping the server
        await _mongo_client.admin.command("ping")
        
        # Get server info
        server_info = await _mongo_client.server_info()
        
        return {
            "status": "healthy",
            "version": server_info.get("version", "unknown"),
            "database": settings.MONGODB_DB_NAME,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Collection accessors
def get_users_collection():
    """Get users collection."""
    return get_db().users


def get_orders_collection():
    """Get orders collection."""
    return get_db().orders


def get_riders_collection():
    """Get riders collection."""
    return get_db().riders


def get_restaurants_collection():
    """Get restaurants collection."""
    return get_db().restaurants
