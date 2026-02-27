from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
import sentry_sdk
import logging

from app.api import auth, products, orders, buyers
from app.routes import trips, payments
from app.routes.vendors import router as vendors_router
from app.routes.delivery_servicemen import router as servicemen_router
from app.routes.orders import router as orders_router
from app.routes.merchants import router as merchants_router
from app.routes.riders import router as riders_router
from app.routes.websocket import router as websocket_router
from app.routes.nduna import router as nduna_router
from app.config import settings
from app.database import (
    connect_db, 
    close_db, 
    ensure_indexes,
    health_check as db_health_check,
)
from app.database import database  # Import the global database reference
from app.core.redis_client import init_redis, close_redis

logger = logging.getLogger(__name__)

# Initialize GlitchTip (Sentry-compatible)
if settings.glitchtip_dsn:
    sentry_sdk.init(
        dsn=settings.glitchtip_dsn,
        traces_sample_rate=0.2,
        environment=settings.environment,
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting iHhashi API...")
    
    # Initialize MongoDB connection
    await connect_db()
    logger.info("MongoDB connected")
    
    # Create database indexes
    try:
        index_results = await ensure_indexes(database)
        logger.info(f"Database indexes created: {len(index_results)} collections updated")
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")
    
    # Initialize Redis connection
    try:
        await init_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed (caching disabled): {e}")
    
    logger.info("iHhashi API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down iHhashi API...")
    
    # Close Redis connection
    try:
        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis: {e}")
    
    # Close MongoDB connection
    await close_db()
    logger.info("MongoDB connection closed")

app = FastAPI(
    title="iHhashi API",
    description="Buyer-centric delivery platform for South Africa",
    version="0.3.0",
    lifespan=lifespan
)

# Parse CORS origins from environment
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(buyers.router, prefix="/api/buyers", tags=["buyers"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(payments.router, prefix="/api", tags=["payments"])
app.include_router(vendors_router, prefix="/api/vendors", tags=["vendors"])
app.include_router(servicemen_router, prefix="/api/delivery-servicemen", tags=["delivery-servicemen"])

# New routes - full implementation
app.include_router(orders_router, prefix="/api/v2/orders", tags=["orders-v2"])
app.include_router(merchants_router, prefix="/api/v2/merchants", tags=["merchants"])
app.include_router(riders_router, prefix="/api/v2/riders", tags=["riders"])
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
app.include_router(nduna_router, prefix="/api/nduna", tags=["nduna-chatbot"])


@app.get("/")
async def root():
    return {
        "name": "iHhashi API",
        "version": "0.2.0",
        "status": "operational",
        "features": [
            "Blue Horse verification",
            "Multi-modal delivery",
            "45-day free trial",
            "0% tip fee"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check with database and Redis connectivity test"""
    # Check MongoDB
    db_status = await db_health_check()
    
    # Check Redis
    redis_status = "disconnected"
    try:
        from app.core.redis_client import get_redis
        redis_client = get_redis()
        await redis_client.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"unavailable"
    
    # Determine overall status
    overall_status = "healthy"
    if db_status.get("status") != "healthy":
        overall_status = "degraded"
    elif redis_status != "connected":
        overall_status = "healthy"  # Redis is optional
    
    return {
        "status": overall_status,
        "database": db_status,
        "redis": redis_status,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }