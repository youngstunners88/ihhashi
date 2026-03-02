"""
Main FastAPI application with Redis pub/sub consumer for horizontal WS scaling.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import connect_db, disconnect_db
from app.routes import websocket
from app.routes.websocket import PUBSUB_HANDLERS
from app.services.pubsub_manager import PubSubManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global pubsub consumer task
_pubsub_consumer_task: asyncio.Task | None = None


async def _pubsub_consumer() -> None:
    """
    Pub/Sub consumer task that subscribes to order/rider/user channels
    and fans out messages to local manager connections.
    Ignores messages from the same instance_id.
    """
    logger.info(f"Starting pub/sub consumer for instance: {settings.INSTANCE_ID}")
    
    # Get all channels to subscribe to
    channels = list(PUBSUB_HANDLERS.keys())
    
    if not channels:
        logger.warning("No pub/sub handlers registered")
        return
    
    try:
        # Initialize pub/sub manager
        await PubSubManager.initialize()
        
        # Register handlers
        for channel, handler in PUBSUB_HANDLERS.items():
            PubSubManager.register_handler(channel, handler)
        
        # Start consuming messages
        pubsub = await PubSubManager.get_instance()
        await pubsub.start_consumer(channels)
        
        # Keep the task running
        while True:
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        logger.info("Pub/sub consumer task cancelled")
        raise
    except Exception as e:
        logger.error(f"Pub/sub consumer error: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager with proper startup/shutdown handling.
    """
    global _pubsub_consumer_task
    
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Instance ID: {settings.INSTANCE_ID}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Connect to database
    await connect_db()
    
    # Start pub/sub consumer for horizontal scaling
    try:
        _pubsub_consumer_task = asyncio.create_task(_pubsub_consumer())
        logger.info("Pub/sub consumer task started")
    except Exception as e:
        logger.error(f"Failed to start pub/sub consumer: {e}")
        # Don't fail startup if Redis is not available
        # The app can still work for single-instance deployments
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Cancel pub/sub consumer task cleanly
    if _pubsub_consumer_task and not _pubsub_consumer_task.done():
        logger.info("Cancelling pub/sub consumer task...")
        _pubsub_consumer_task.cancel()
        try:
            await _pubsub_consumer_task
        except asyncio.CancelledError:
            pass
        logger.info("Pub/sub consumer task cancelled")
    
    # Stop pub/sub manager
    await PubSubManager.shutdown()
    
    # Disconnect from database
    await disconnect_db()
    
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Delivery App API with WebSocket support",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(websocket.router, prefix="/api/v1")
    
    return app


# Create the application instance
app = create_application()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "instance_id": settings.INSTANCE_ID,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.database import check_db_health
    
    db_health = await check_db_health()
    redis_health = await PubSubManager.get_connection_info()
    
    status_code = 200
    if db_health["status"] != "healthy":
        status_code = 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if status_code == 200 else "unhealthy",
            "database": db_health,
            "redis": redis_health,
            "instance_id": settings.INSTANCE_ID,
        }
    )


@app.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes."""
    return {"ready": True}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (placeholder)."""
    return {"todo": "implement prometheus metrics"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        workers=1 if settings.is_development else 4,
    )
