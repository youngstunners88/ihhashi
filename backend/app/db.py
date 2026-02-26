from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, TEXT

_client: AsyncIOMotorClient | None = None
_db = None

async def connect_db(mongodb_url: str, db_name: str = "ihhashi"):
    """Establish MongoDB connection"""
    global _client, _db
    _client = AsyncIOMotorClient(mongodb_url)
    _db = _client[db_name]
    # Verify connection
    await _client.admin.command("ping")
    print("✅ MongoDB connected")
    
    # Create indexes
    await create_indexes(_db)
    return _db

async def close_db():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
        print("✅ MongoDB disconnected")

def get_db():
    """Dependency for route handlers"""
    if _db is None:
        raise RuntimeError("Database not connected")
    return _db

async def create_indexes(db):
    """Create database indexes for performance"""
    # Users collection
    users = db.users
    await users.create_index([("email", ASCENDING)], unique=True, name="idx_email_unique")
    await users.create_index([("phone", ASCENDING)], unique=True, name="idx_phone_unique", sparse=True)
    await users.create_index([("location", "2dsphere")], name="idx_location_geo")
    await users.create_index([("role", ASCENDING), ("is_active", ASCENDING)], name="idx_role_active")
    
    # Merchants - full-text search
    merchants = db.merchants
    await merchants.create_index([("name", TEXT), ("description", TEXT)], name="idx_merchant_search")
    await merchants.create_index([("location", "2dsphere")], name="idx_merchant_geo")
    await merchants.create_index([("is_active", ASCENDING)], name="idx_merchant_active")
    
    # Orders
    orders = db.orders
    await orders.create_index([("buyer_id", ASCENDING), ("status", ASCENDING)], name="idx_buyer_status")
    await orders.create_index([("driver_id", ASCENDING), ("status", ASCENDING)], name="idx_driver_status")
    await orders.create_index([("merchant_id", ASCENDING)], name="idx_merchant_orders")
    await orders.create_index([("created_at", ASCENDING)], name="idx_created_at")
    
    # Products
    products = db.products
    await products.create_index([("merchant_id", ASCENDING), ("is_available", ASCENDING)], name="idx_merchant_products")
    await products.create_index([("category", ASCENDING)], name="idx_category")
    
    # Trips
    trips = db.trips
    await trips.create_index([("driver_id", ASCENDING), ("status", ASCENDING)], name="idx_driver_trips")
    await trips.create_index([("location", "2dsphere")], name="idx_trip_location")
    
    print("✅ Database indexes created")
