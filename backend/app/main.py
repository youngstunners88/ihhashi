from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional
import asyncio
import json as _json
import sentry_sdk
import logging

# Real routes only - no mocks
from app.routes.auth import router as auth_router
from app.routes.orders import router as orders_router
from app.routes.merchants import router as merchants_router
from app.routes.riders import router as riders_router
from app.routes.vendors import router as vendors_router
from app.routes.delivery_servicemen import router as servicemen_router
from app.routes.referrals import router as referrals_router
from app.routes.customer_rewards import router as customer_rewards_router
from app.routes import trips, payments
from app.routes.websocket import router as websocket_router
from app.routes.nduna import router as nduna_router
from app.config import settings
from app.database import (
    connect_db, 
    close_db, 
    ensure_indexes,
    health_check as db_health_check,
)
from app.database import database
from app.core.redis_client import init_redis, close_redis, RedisClient, PubSubManager
from app.routes.websocket import manager as ws_manager, INSTANCE_ID as WS_INSTANCE_ID
from app.middleware.rate_limit import setup_rate_limiting

logger = logging.getLogger(__name__)

# Background task reference for pub/sub consumer cleanup
_pubsub_task: Optional[asyncio.Task] = None


async def _pubsub_consumer():
    """
    Background task that subscribes to Redis pub/sub channels and
    fans out received messages to local WebSocket connections.
    This enables multi-instance WebSocket broadcasting.
    """
    pubsub = None
    try:
        client = await RedisClient.get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(
            PubSubManager.CHANNEL_ORDER_UPDATES,
            PubSubManager.CHANNEL_RIDER_UPDATES,
            PubSubManager.CHANNEL_USER_NOTIFICATIONS,
        )
        logger.info("Redis pub/sub consumer listening")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                data = _json.loads(message["data"])

                # Skip messages published by this instance (deduplication)
                if data.get("_origin") == WS_INSTANCE_ID:
                    continue

                channel = message["channel"]

                if channel == PubSubManager.CHANNEL_ORDER_UPDATES:
                    order_id = data.get("order_id")
                    if order_id:
                        await ws_manager.broadcast_order_update(
                            order_id, data.get("data", {})
                        )
                elif channel == PubSubManager.CHANNEL_RIDER_UPDATES:
                    rider_id = data.get("rider_id")
                    if rider_id:
                        await ws_manager.send_to_rider(rider_id, data)
                elif channel == PubSubManager.CHANNEL_USER_NOTIFICATIONS:
                    user_id = data.get("user_id")
                    if user_id:
                        await ws_manager.send_to_user(user_id, data)
            except Exception as e:
                logger.warning(f"Error processing pub/sub message: {e}")

    except asyncio.CancelledError:
        logger.info("Redis pub/sub consumer cancelled")
    except Exception as e:
        logger.error(f"Redis pub/sub consumer error: {e}")
    finally:
        if pubsub:
            try:
                await pubsub.unsubscribe()
                await pubsub.close()
            except Exception:
                pass


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

    # Start Redis pub/sub consumer for multi-instance WebSocket fan-out
    global _pubsub_task
    try:
        _pubsub_task = asyncio.create_task(_pubsub_consumer())
        logger.info("Redis pub/sub consumer task started")
    except Exception as e:
        logger.warning(f"Failed to start pub/sub consumer: {e}")

    logger.info("iHhashi API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down iHhashi API...")

    # Stop pub/sub consumer
    global _pubsub_task
    if _pubsub_task and not _pubsub_task.done():
        _pubsub_task.cancel()
        try:
            await _pubsub_task
        except asyncio.CancelledError:
            pass
        logger.info("Redis pub/sub consumer stopped")

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
    version="1.0.0",
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

# Setup Redis-backed rate limiting
setup_rate_limiting(app)

# ============================================================================
# Create /api/v1 router - matches frontend expectations
# ============================================================================
api_v1 = APIRouter(prefix="/api/v1")

# Mount all real routes under /api/v1
api_v1.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1.include_router(orders_router, prefix="/orders", tags=["orders"])
api_v1.include_router(merchants_router, prefix="/merchants", tags=["merchants"])
api_v1.include_router(riders_router, prefix="/riders", tags=["riders"])
api_v1.include_router(vendors_router, prefix="/vendors", tags=["vendors"])
api_v1.include_router(servicemen_router, prefix="/delivery-servicemen", tags=["delivery-servicemen"])
api_v1.include_router(referrals_router, prefix="/referrals", tags=["referrals"])
api_v1.include_router(customer_rewards_router, prefix="/customer-rewards", tags=["customer-rewards"])
api_v1.include_router(trips.router, prefix="/trips", tags=["trips"])
api_v1.include_router(payments.router, prefix="/payments", tags=["payments"])

# Include the v1 router in main app
app.include_router(api_v1)

# WebSocket and chatbot at different prefixes
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])
app.include_router(nduna_router, prefix="/api/nduna", tags=["nduna-chatbot"])


@app.get("/")
async def root():
    return {
        "name": "iHhashi API",
        "version": "0.4.2",
        "status": "operational",
        "features": [
            "Blue Horse verification",
            "Multi-modal delivery",
            "45-day free trial + referral bonuses",
            "0% tip fee",
            "Hashi Coins rewards for customers",
            "Tiered loyalty program"
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