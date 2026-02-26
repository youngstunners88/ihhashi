from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from contextlib import asynccontextmanager
import sentry_sdk

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
from app.database import connect_db, close_db, database

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
    await connect_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="iHhashi API",
    description="Buyer-centric delivery platform for South Africa",
    version="0.2.0",
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
    """Health check with database connectivity test"""
    db_status = "disconnected"
    try:
        if database is not None:
            # Ping database
            await database.client.admin.command("ping")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }