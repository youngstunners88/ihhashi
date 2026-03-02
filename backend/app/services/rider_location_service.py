"""
Rider Location Tracking Service with throttling and cleanup.
Uses Redis geospatial indexes for efficient queries.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.config import settings
from app.database import get_db
from app.services.redis_cache import redis_cache

logger = logging.getLogger(__name__)


@dataclass
class LocationUpdate:
    """Rider location update data."""
    rider_id: str
    latitude: float
    longitude: float
    accuracy: Optional[float]
    heading: Optional[float]
    speed: Optional[float]
    timestamp: datetime


class RiderLocationService:
    """
    Service for managing rider locations.
    Features:
    - Throttled updates (max 1 per 5 seconds per rider)
    - Redis geospatial indexes
    - Automatic cleanup of stale locations
    """
    
    # Throttling: minimum seconds between updates from same rider
    UPDATE_THROTTLE_SECONDS = 5
    
    # Staleness threshold: riders offline for this long are cleaned up
    STALE_THRESHOLD_MINUTES = 30
    
    # Redis key for geospatial index
    GEO_KEY = "rider:locations"
    
    # Redis key prefix for rider metadata
    META_PREFIX = "rider:meta"
    
    @classmethod
    async def update_location(
        cls,
        rider_id: str,
        latitude: float,
        longitude: float,
        accuracy: Optional[float] = None,
        heading: Optional[float] = None,
        speed: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Update rider location with throttling.
        
        Returns:
            Tuple of (success, message)
        """
        # Check throttling
        throttle_key = f"rider:{rider_id}:last_update"
        last_update = await redis_cache.get(throttle_key)
        
        if last_update:
            last_time = datetime.fromisoformat(last_update) if isinstance(last_update, str) else last_update
            elapsed = (datetime.utcnow() - last_time).total_seconds()
            
            if elapsed < cls.UPDATE_THROTTLE_SECONDS:
                return False, (
                    f"Update throttled. Please wait "
                    f"{cls.UPDATE_THROTTLE_SECONDS - elapsed:.1f} seconds"
                )
        
        # Validate coordinates
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return False, "Invalid coordinates"
        
        try:
            # Update geospatial index in Redis
            # Using redis-py geoadd command
            redis_client = redis_cache._client
            if redis_client:
                await redis_client.geoadd(
                    cls.GEO_KEY,
                    (longitude, latitude, rider_id)
                )
            
            # Store metadata
            meta_key = f"{cls.META_PREFIX}:{rider_id}"
            await redis_cache.set_json(
                meta_key,
                {
                    "rider_id": rider_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "accuracy": accuracy,
                    "heading": heading,
                    "speed": speed,
                    "updated_at": datetime.utcnow().isoformat(),
                    "status": "online"
                },
                expire=3600  # 1 hour TTL
            )
            
            # Update throttling timestamp
            await redis_cache.set(
                throttle_key,
                datetime.utcnow().isoformat(),
                expire=60  # 1 minute expiry for throttle key
            )
            
            # Also persist to MongoDB for history
            await cls._persist_location_history(
                rider_id, latitude, longitude, accuracy, heading, speed
            )
            
            return True, "Location updated"
            
        except Exception as e:
            logger.error(f"Failed to update rider location: {e}")
            return False, f"Update failed: {str(e)}"
    
    @classmethod
    async def _persist_location_history(
        cls,
        rider_id: str,
        latitude: float,
        longitude: float,
        accuracy: Optional[float],
        heading: Optional[float],
        speed: Optional[float]
    ):
        """Persist location to MongoDB for tracking history."""
        db = get_db()
        
        # Only store every 5th update to reduce DB load
        counter_key = f"rider:{rider_id}:update_counter"
        counter = await redis_cache.get(counter_key) or 0
        counter = int(counter) + 1
        
        if counter >= 5:
            # Store in MongoDB
            await db.rider_locations.insert_one({
                "rider_id": rider_id,
                "location": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]  # GeoJSON format
                },
                "accuracy": accuracy,
                "heading": heading,
                "speed": speed,
                "timestamp": datetime.utcnow()
            })
            counter = 0
        
        await redis_cache.set(counter_key, counter, expire=3600)
    
    @classmethod
    async def get_rider_location(cls, rider_id: str) -> Optional[Dict]:
        """Get current location of a rider."""
        meta_key = f"{cls.META_PREFIX}:{rider_id}"
        return await redis_cache.get_json(meta_key)
    
    @classmethod
    async def find_nearby_riders(
        cls,
        latitude: float,
        longitude: float,
        radius_km: float = 5,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find riders within radius of a point.
        Uses Redis GEORADIUS for efficient geospatial queries.
        """
        try:
            redis_client = redis_cache._client
            if not redis_client:
                return []
            
            # Query Redis geospatial index
            results = await redis_client.georadius(
                cls.GEO_KEY,
                longitude,
                latitude,
                radius_km,
                unit="km",
                withdist=True,  # Include distance
                withcoord=True,  # Include coordinates
                count=limit,
                sort="ASC"  # Closest first
            )
            
            riders = []
            for result in results:
                rider_id = result[0]
                distance = result[1]
                coords = result[2]
                
                # Get metadata
                meta = await cls.get_rider_location(rider_id)
                
                if meta:
                    # Check if not stale
                    updated_at = datetime.fromisoformat(meta.get("updated_at", "2000-01-01"))
                    if datetime.utcnow() - updated_at < timedelta(minutes=cls.STALE_THRESHOLD_MINUTES):
                        riders.append({
                            "rider_id": rider_id,
                            "distance_km": float(distance),
                            "latitude": coords[1],
                            "longitude": coords[0],
                            **meta
                        })
            
            return riders
            
        except Exception as e:
            logger.error(f"Failed to find nearby riders: {e}")
            return []
    
    @classmethod
    async def set_rider_offline(cls, rider_id: str):
        """Mark rider as offline and remove from active index."""
        try:
            redis_client = redis_cache._client
            if redis_client:
                # Remove from geospatial index
                await redis_client.zrem(cls.GEO_KEY, rider_id)
            
            # Update metadata
            meta_key = f"{cls.META_PREFIX}:{rider_id}"
            meta = await redis_cache.get_json(meta_key)
            if meta:
                meta["status"] = "offline"
                meta["offline_at"] = datetime.utcnow().isoformat()
                await redis_cache.set_json(meta_key, meta, expire=86400)  # Keep for 24 hours
            
            logger.info(f"Rider {rider_id} marked as offline")
            
        except Exception as e:
            logger.error(f"Failed to set rider offline: {e}")
    
    @classmethod
    async def cleanup_stale_locations(cls) -> int:
        """
        Cleanup riders that have been offline for more than threshold.
        Returns number of cleaned up riders.
        """
        try:
            redis_client = redis_cache._client
            if not redis_client:
                return 0
            
            # Get all riders from geospatial index
            all_riders = await redis_client.zrange(cls.GEO_KEY, 0, -1)
            
            cleaned = 0
            cutoff_time = datetime.utcnow() - timedelta(minutes=cls.STALE_THRESHOLD_MINUTES)
            
            for rider_id in all_riders:
                meta_key = f"{cls.META_PREFIX}:{rider_id}"
                meta = await redis_cache.get_json(meta_key)
                
                if meta:
                    updated_at = datetime.fromisoformat(meta.get("updated_at", "2000-01-01"))
                    
                    if updated_at < cutoff_time:
                        # Remove stale rider
                        await redis_client.zrem(cls.GEO_KEY, rider_id)
                        await redis_cache.delete(meta_key)
                        cleaned += 1
                        
                        logger.info(f"Cleaned up stale location for rider {rider_id}")
            
            logger.info(f"Location cleanup completed: {cleaned} riders removed")
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale locations: {e}")
            return 0
    
    @classmethod
    async def get_active_riders_count(cls) -> int:
        """Get count of currently active riders."""
        try:
            redis_client = redis_cache._client
            if not redis_client:
                return 0
            
            return await redis_client.zcard(cls.GEO_KEY)
        except Exception:
            return 0
    
    @classmethod
    async def get_rider_location_history(
        cls,
        rider_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Get historical location data for a rider from MongoDB."""
        db = get_db()
        
        cursor = db.rider_locations.find({
            "rider_id": rider_id,
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }).sort("timestamp", 1)
        
        return await cursor.to_list(length=None)


# Global service instance
rider_location_service = RiderLocationService()
