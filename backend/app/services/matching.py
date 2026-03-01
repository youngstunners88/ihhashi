"""
Rider matching and delivery fare calculation service - Production ready with transaction locking
"""
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict
from math import radians, sin, cos, sqrt, atan2
from bson import ObjectId
from zoneinfo import ZoneInfo

from app.database import get_collection
from app.utils.validation import safe_object_id
from app.services.delivery_fee import calculate_delivery_fee, is_surge_time, SAST


class MatchingService:
    """Rider matching and delivery fare calculation service"""
    
    def __init__(self, db):
        self.db = db
        
        # Delivery fare configuration (ZAR)
        self.base_fees = {
            "bike": 15.0,
            "car": 25.0,
            "bicycle": 12.0,
            "walking": 10.0
        }
        self.per_km_rate = 6.0
        self.per_minute_rate = 1.0
        self.surge_hours = [7, 8, 17, 18, 19]  # Morning and evening rush in SAST
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km using Haversine formula"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    async def calculate_fare(
        self,
        pickup: Dict,
        delivery: Dict,
        vehicle_type: str = "bike"
    ) -> Dict:
        """Calculate delivery fee estimate using single source of truth."""
        return calculate_delivery_fee(
            pickup["latitude"], pickup["longitude"],
            delivery["latitude"], delivery["longitude"],
            vehicle_type
        )
    
    async def find_nearest_rider(
        self,
        pickup_location: Dict,
        vehicle_type: str,
        excluded_riders: List[str] = None,
        max_distance_km: float = 5.0
    ) -> Optional[Dict]:
        """Find the nearest available rider"""
        
        excluded_riders = excluded_riders or []
        
        # Find riders who are:
        # - Online/available
        # - Have the right vehicle type
        # - Not in excluded list
        # - Within max distance
        riders = await self.db.riders.find({
            "status": "available",
            "vehicle_type": vehicle_type,
            "rider_id": {"$nin": excluded_riders},
            "location": {"$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [pickup_location["longitude"], pickup_location["latitude"]]
                },
                "$maxDistance": max_distance_km * 1000  # Convert to meters
            }}
        }).limit(5).to_list(length=5)
        
        if not riders:
            return None
        
        # Return nearest rider
        return riders[0]
    
    async def find_and_lock_rider(
        self,
        pickup_location: Dict,
        vehicle_type: str,
        delivery_id: ObjectId,
        excluded_riders: List[str] = None,
        max_distance_km: float = 5.0
    ) -> Optional[Dict]:
        """
        Find and atomically lock a rider for assignment.
        
        Uses find_one_and_update to prevent race conditions where
        multiple deliveries try to assign the same rider.
        """
        excluded_riders = excluded_riders or []
        
        # Try to find and lock a rider atomically
        # This prevents race conditions in concurrent assignment scenarios
        rider = await self.db.riders.find_one_and_update(
            {
                "status": "available",
                "vehicle_type": vehicle_type,
                "_id": {"$nin": [safe_object_id(r) for r in excluded_riders if r]},
                "location": {"$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [pickup_location["longitude"], pickup_location["latitude"]]
                    },
                    "$maxDistance": max_distance_km * 1000
                }}
            },
            {
                "$set": {
                    "status": "busy",
                    "locked_for_delivery": delivery_id,
                    "locked_at": datetime.now(timezone.utc)
                }
            },
            return_document=True
        )
        
        return rider
    
    async def request_delivery(self, customer_id: str, delivery_data: dict) -> dict:
        """Main delivery request flow"""
        
        # 1. Validate customer
        customer = await self.db.users.find_one({"_id": safe_object_id(customer_id)})
        if not customer:
            raise ValueError("Customer not found")
        
        # 2. Check for existing active delivery (use atomic check)
        active_delivery = await self.db.deliveries.find_one({
            "customer_id": customer_id,
            "status": {"$in": ["pending", "rider_assigned", "at_merchant", "picked_up", "in_transit"]}
        })
        if active_delivery:
            raise ValueError("Customer already has an active delivery")
        
        # 3. Calculate fare
        fare_estimate = await self.calculate_fare(
            delivery_data["pickup_location"],
            delivery_data["delivery_location"],
            delivery_data.get("vehicle_type", "bike")
        )
        
        # 4. Create delivery record
        from app.models.trip import Delivery, DeliveryStatus
        delivery = Delivery(
            order_id=delivery_data["order_id"],
            customer_id=customer_id,
            merchant_id=delivery_data.get("merchant_id", ""),
            pickup_location=delivery_data["pickup_location"],
            delivery_location=delivery_data["delivery_location"],
            vehicle_type=delivery_data.get("vehicle_type", "bike"),
            item_count=delivery_data.get("item_count", 1),
            special_instructions=delivery_data.get("special_instructions"),
            fare=fare_estimate
        )
        
        result = await self.db.deliveries.insert_one(delivery.dict())
        delivery_id = result.inserted_id
        
        # 5. Find and assign rider with proper locking (async in background)
        asyncio.create_task(self._assign_rider_with_lock(delivery_id, delivery.dict(), fare_estimate))
        
        return {
            "delivery_id": str(delivery_id),
            "status": "pending",
            "fare_estimate": fare_estimate,
            "message": "Finding nearby riders..."
        }
    
    async def _assign_rider_with_lock(self, delivery_id: ObjectId, delivery_data: dict, fare_estimate: dict):
        """
        Assign a rider to the delivery with retry logic and proper locking.
        
        Uses atomic find_and_lock to prevent race conditions.
        """
        
        max_attempts = 3
        attempted_rider_ids = []
        
        for attempt in range(max_attempts):
            # Use atomic find-and-lock instead of separate find + update
            rider = await self.find_and_lock_rider(
                delivery_data["pickup_location"],
                delivery_data.get("vehicle_type", "bike"),
                delivery_id,
                attempted_rider_ids,
                max_distance_km=5.0 + (attempt * 2)  # Expand search radius on retry
            )
            
            if rider:
                try:
                    # Assign rider to delivery
                    result = await self.db.deliveries.update_one(
                        {
                            "_id": delivery_id,
                            "status": "pending"  # Only update if still pending
                        },
                        {
                            "$set": {
                                "rider_id": str(rider["_id"]),
                                "status": "rider_assigned",
                                "rider_assigned_at": datetime.now(timezone.utc)
                            }
                        }
                    )
                    
                    if result.modified_count > 0:
                        # Successfully assigned
                        await self._notify_rider(str(rider["_id"]), str(delivery_id))
                        return
                    else:
                        # Delivery was already assigned by another process
                        # Release the rider lock
                        await self.db.riders.update_one(
                            {"_id": rider["_id"]},
                            {"$set": {"status": "available", "locked_for_delivery": None}}
                        )
                        return
                        
                except Exception as e:
                    # Release rider lock on error
                    await self.db.riders.update_one(
                        {"_id": rider["_id"]},
                        {"$set": {"status": "available", "locked_for_delivery": None}}
                    )
                    raise e
            
            await asyncio.sleep(2)  # Wait before retry
        
        # No rider found after all attempts
        await self.db.deliveries.update_one(
            {"_id": delivery_id},
            {"$set": {"status": "cancelled", "cancel_reason": "no_riders_available"}}
        )
        
        # Notify customer
        await self._notify_customer(delivery_data["customer_id"], "No riders available. Please try again.")
    
    async def _assign_rider(self, delivery_id, delivery_data: dict, fare_estimate: dict):
        """
        DEPRECATED: Use _assign_rider_with_lock instead.
        This method is kept for backwards compatibility but should not be used for new code.
        """
        await self._assign_rider_with_lock(delivery_id, delivery_data, fare_estimate)
    
    async def _notify_rider(self, rider_id: str, delivery_id: str):
        """Persist notification and send FCM push to rider device."""
        notification = {
            "rider_id": rider_id,
            "delivery_id": delivery_id,
            "type": "delivery_request",
            "message": "New delivery request nearby!",
            "created_at": datetime.now(timezone.utc)
        }
        await self.db.notifications.insert_one(notification)

        # Fire FCM if the rider has a stored device token
        rider = await self.db.riders.find_one({"_id": safe_object_id(rider_id)}, {"fcm_token": 1})
        if rider and rider.get("fcm_token"):
            from app.services.fcm import notify_rider_new_delivery
            await notify_rider_new_delivery(
                token=rider["fcm_token"],
                delivery_id=delivery_id,
            )

    async def _notify_customer(self, customer_id: str, message: str, status: str = "pending"):
        """Persist notification and send FCM push to customer device."""
        notification = {
            "customer_id": customer_id,
            "type": "delivery_update",
            "message": message,
            "created_at": datetime.now(timezone.utc)
        }
        await self.db.notifications.insert_one(notification)

        # Fire FCM if the customer has a stored device token
        user = await self.db.users.find_one({"_id": safe_object_id(customer_id)}, {"fcm_token": 1})
        if user and user.get("fcm_token"):
            from app.services.fcm import notify_customer_order_update
            await notify_customer_order_update(
                token=user["fcm_token"],
                order_id="",
                status=status,
                message=message,
            )

    async def _notify_merchant(self, merchant_id: str, message: str, delivery_id: str = None):
        """Persist notification and send FCM push to merchant device."""
        notification = {
            "merchant_id": merchant_id,
            "delivery_id": delivery_id,
            "type": "delivery_update",
            "message": message,
            "created_at": datetime.now(timezone.utc)
        }
        await self.db.notifications.insert_one(notification)

        # Fire FCM if the merchant has a stored device token
        merchant = await self.db.merchants.find_one(
            {"_id": safe_object_id(merchant_id)}, {"fcm_token": 1}
        )
        if merchant and merchant.get("fcm_token"):
            from app.services.fcm import notify_merchant_new_order
            await notify_merchant_new_order(
                token=merchant["fcm_token"],
                order_id=delivery_id or "",
                item_summary=message,
            )
    
    async def release_rider(self, rider_id: str):
        """Release a rider from a delivery assignment"""
        await self.db.riders.update_one(
            {"_id": safe_object_id(rider_id)},
            {
                "$set": {
                    "status": "available",
                    "locked_for_delivery": None,
                    "locked_at": None
                }
            }
        )
