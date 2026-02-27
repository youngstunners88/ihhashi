"""
Database indexes for optimal query performance
"""
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


async def create_indexes(db: AsyncIOMotorDatabase):
    """Create all required database indexes"""
    
    indexes_created = []
    
    # Orders collection indexes
    try:
        await db.orders.create_index("buyer_id")
        await db.orders.create_index("store_id")
        await db.orders.create_index("status")
        await db.orders.create_index("created_at")
        await db.orders.create_index([("created_at", -1)])
        await db.orders.create_index([("buyer_id", 1), ("status", 1)])
        await db.orders.create_index([("store_id", 1), ("status", 1)])
        indexes_created.append("orders")
    except Exception as e:
        logger.error(f"Failed to create orders indexes: {e}")
    
    # Users collection indexes
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("phone", unique=True, sparse=True)
        await db.users.create_index([("email", 1), ("is_active", 1)])
        indexes_created.append("users")
    except Exception as e:
        logger.error(f"Failed to create users indexes: {e}")
    
    # Drivers/Riders collection indexes
    try:
        await db.drivers.create_index("status")
        await db.drivers.create_index([("status", 1), ("vehicle_type", 1)])
        # Geo index for location-based queries
        await db.drivers.create_index([("current_location", "2dsphere")])
        indexes_created.append("drivers")
    except Exception as e:
        logger.error(f"Failed to create drivers indexes: {e}")
    
    # Riders collection indexes (for delivery riders)
    try:
        await db.riders.create_index("status")
        await db.riders.create_index([("status", 1), ("vehicle_type", 1)])
        # Geo index for location-based queries
        await db.riders.create_index([("location", "2dsphere")])
        # TTL index for stale locks (auto-release after 10 minutes)
        await db.riders.create_index("locked_at", expireAfterSeconds=600)
        indexes_created.append("riders")
    except Exception as e:
        logger.error(f"Failed to create riders indexes: {e}")
    
    # Payments collection indexes
    try:
        await db.payments.create_index("reference", unique=True)
        await db.payments.create_index("user_id")
        await db.payments.create_index("status")
        await db.payments.create_index([("user_id", 1), ("created_at", -1)])
        indexes_created.append("payments")
    except Exception as e:
        logger.error(f"Failed to create payments indexes: {e}")
    
    # Payment Webhooks collection indexes (idempotency)
    try:
        # Unique index on event_id prevents duplicate webhook processing
        await db.payment_webhooks.create_index("event_id", unique=True)
        await db.payment_webhooks.create_index([("received_at", -1)])
        indexes_created.append("payment_webhooks")
    except Exception as e:
        logger.error(f"Failed to create payment_webhooks indexes: {e}")
    
    # Products collection indexes
    try:
        await db.products.create_index("store_id")
        await db.products.create_index([("store_id", 1), ("category", 1)])
        await db.products.create_index([("store_id", 1), ("is_available", 1)])
        # Text index for search
        await db.products.create_index([("name", "text"), ("description", "text")])
        indexes_created.append("products")
    except Exception as e:
        logger.error(f"Failed to create products indexes: {e}")
    
    # Stores/Merchants collection indexes
    try:
        await db.stores.create_index("owner_id")
        await db.stores.create_index("status")
        await db.stores.create_index([("status", 1), ("is_open", 1)])
        # Geo index for location-based queries
        await db.stores.create_index([("location", "2dsphere")])
        indexes_created.append("stores")
    except Exception as e:
        logger.error(f"Failed to create stores indexes: {e}")
    
    # Deliveries collection indexes
    try:
        await db.deliveries.create_index("customer_id")
        await db.deliveries.create_index("rider_id")
        await db.deliveries.create_index("status")
        await db.deliveries.create_index([("rider_id", 1), ("status", 1)])
        indexes_created.append("deliveries")
    except Exception as e:
        logger.error(f"Failed to create deliveries indexes: {e}")
    
    # Notifications collection indexes
    try:
        await db.notifications.create_index([("user_id", 1), ("created_at", -1)])
        await db.notifications.create_index([("read", 1)])
        # TTL index to auto-delete old notifications (30 days)
        await db.notifications.create_index("created_at", expireAfterSeconds=2592000)
        indexes_created.append("notifications")
    except Exception as e:
        logger.error(f"Failed to create notifications indexes: {e}")
    
    logger.info(f"Created indexes for collections: {', '.join(indexes_created)}")
    return indexes_created


async def ensure_indexes(app):
    """FastAPI startup event to ensure indexes exist"""
    from app.database import get_database
    
    @app.on_event("startup")
    async def startup_event():
        db = get_database()
        await create_indexes(db)


async def get_index_stats(db: AsyncIOMotorDatabase) -> dict:
    """
    Get statistics about indexes in the database.
    
    Args:
        db: Database instance
        
    Returns:
        Dictionary with index statistics per collection
    """
    stats = {}
    
    collections = ["users", "orders", "drivers", "payments", "products", "stores", "deliveries", "notifications"]
    
    for collection_name in collections:
        try:
            collection = db[collection_name]
            indexes = await collection.list_indexes().to_list(length=100)
            stats[collection_name] = {
                "count": len(indexes),
                "indexes": [
                    {
                        "name": idx.get("name"),
                        "keys": list(idx.get("key", {}).keys()),
                        "unique": idx.get("unique", False),
                    }
                    for idx in indexes
                ]
            }
        except Exception as e:
            stats[collection_name] = {"error": str(e)}
    
    return stats


async def drop_all_indexes(db: AsyncIOMotorDatabase) -> dict:
    """
    Drop all non-_id indexes from collections.
    
    WARNING: This is a destructive operation. Use with caution.
    
    Args:
        db: Database instance
        
    Returns:
        Dictionary with results per collection
    """
    results = {}
    
    collections = ["users", "orders", "drivers", "payments", "products", "stores", "deliveries", "notifications"]
    
    for collection_name in collections:
        try:
            collection = db[collection_name]
            await collection.drop_indexes()
            results[collection_name] = {"status": "success", "message": "All indexes dropped"}
        except Exception as e:
            results[collection_name] = {"status": "error", "message": str(e)}
    
    logger.warning(f"Dropped all indexes from collections: {', '.join(collections)}")
    return results
