"""
MongoDB Database Connection Module for iHhashi

Provides:
- Connection pooling for efficient database connections
- Timeout settings for production reliability
- Proper connection cleanup on shutdown
- Health check utilities
"""

import logging
from typing import Optional
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.driver_info import DriverInfo

from app.config import settings

logger = logging.getLogger(__name__)

# Global database client and database reference
client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None


async def connect_db():
    """
    Initialize MongoDB connection with pooling and proper configuration.
    
    Call this on application startup.
    """
    global client, database
    
    if client is not None:
        logger.warning("Database already connected")
        return
    
    try:
        # Connection pooling configuration
        # maxPoolSize: Maximum number of connections in the pool
        # minPoolSize: Minimum connections to maintain
        # maxIdleTimeMS: Close idle connections after this time
        # waitQueueTimeoutMS: Max time to wait for an available connection
        # connectTimeoutMS: Connection timeout
        # socketTimeoutMS: Socket operation timeout
        # serverSelectionTimeoutMS: Time to find a suitable server
        
        client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=30000,        # 30 seconds
            waitQueueTimeoutMS=5000,    # 5 seconds
            connectTimeoutMS=5000,      # 5 seconds
            socketTimeoutMS=30000,      # 30 seconds
            serverSelectionTimeoutMS=5000,  # 5 seconds
            retryWrites=True,
            retryReads=True,
            driver=DriverInfo(name="iHhashi", version="0.3.0"),
        )
        
        database = client[settings.db_name]
        
        # Test the connection
        await database.command("ping")
        logger.info(f"Connected to MongoDB: {settings.db_name}")
        
        # Log pool stats in debug mode
        if settings.debug:
            logger.debug(f"MongoDB connection pool initialized with maxPoolSize=100")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_db():
    """
    Close the MongoDB connection and cleanup resources.
    
    Call this on application shutdown.
    """
    global client, database
    
    if client is not None:
        try:
            client.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
        finally:
            client = None
            database = None


def get_collection(name: str):
    """
    Get a MongoDB collection by name.
    
    Args:
        name: Collection name
    
    Returns:
        The MongoDB collection
    
    Raises:
        RuntimeError if database is not connected
    """
    if database is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return database[name]


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency to get database instance.
    
    Returns:
        The database instance
    
    Raises:
        RuntimeError if database is not connected
    """
    if database is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return database


@asynccontextmanager
async def get_db_session():
    """
    Context manager for database operations.
    
    Usage:
        async with get_db_session() as db:
            collection = db["users"]
            await collection.find_one({"_id": user_id})
    """
    db = await get_database()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database operation error: {e}")
        raise


async def health_check() -> dict:
    """
    Perform a health check on the database connection.
    
    Returns:
        dict with health status information
    """
    if client is None or database is None:
        return {
            "status": "unhealthy",
            "message": "Database not connected"
        }
    
    try:
        # Ping the database
        start_time = __import__("time").time()
        await database.command("ping")
        latency_ms = (__import__("time").time() - start_time) * 1000
        
        # Get server info
        server_info = await client.server_info()
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "mongodb_version": server_info.get("version", "unknown"),
            "database": settings.db_name,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }


async def get_pool_stats() -> dict:
    """
    Get connection pool statistics.
    
    Note: Motor/PyMongo doesn't expose all pool stats directly,
    but we can provide some useful information.
    """
    if client is None:
        return {"status": "not_initialized"}
    
    try:
        # These are configured values, not runtime stats
        return {
            "status": "initialized",
            "database": settings.db_name,
            "configured_max_pool_size": 100,
            "configured_min_pool_size": 10,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# Collection name constants for consistency
COLLECTIONS = {
    "users": "users",
    "merchants": "merchants",
    "orders": "orders",
    "deliveries": "deliveries",
    "riders": "riders",
    "drivers": "drivers",
    "payments": "payments",
    "notifications": "notifications",
    "verifications": "verifications",
    "accounts": "accounts",
    "products": "products",
    "reviews": "reviews",
    "refunds": "refunds",
}


def users_collection():
    """Get the users collection."""
    return get_collection(COLLECTIONS["users"])


def merchants_collection():
    """Get the merchants collection."""
    return get_collection(COLLECTIONS["merchants"])


def orders_collection():
    """Get the orders collection."""
    return get_collection(COLLECTIONS["orders"])


def deliveries_collection():
    """Get the deliveries collection."""
    return get_collection(COLLECTIONS["deliveries"])


def riders_collection():
    """Get the riders collection."""
    return get_collection(COLLECTIONS["riders"])


def drivers_collection():
    """Get the drivers collection."""
    return get_collection(COLLECTIONS["drivers"])


def payments_collection():
    """Get the payments collection."""
    return get_collection(COLLECTIONS["payments"])


def notifications_collection():
    """Get the notifications collection."""
    return get_collection(COLLECTIONS["notifications"])


# Import index management
from app.database.indexes import ensure_indexes, get_index_stats, drop_all_indexes

__all__ = [
    "connect_db",
    "close_db",
    "get_collection",
    "get_database",
    "get_db_session",
    "health_check",
    "get_pool_stats",
    "ensure_indexes",
    "get_index_stats",
    "drop_all_indexes",
    "COLLECTIONS",
    "users_collection",
    "merchants_collection",
    "orders_collection",
    "deliveries_collection",
    "riders_collection",
    "drivers_collection",
    "payments_collection",
    "notifications_collection",
    "client",
    "database",
]
