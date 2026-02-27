import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from math import radians, sin, cos, sqrt, atan2


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
        self.surge_hours = [7, 8, 17, 18, 19]  # Morning and evening rush
    
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
        """Calculate delivery fee estimate"""
        
        distance_km = self.calculate_distance(
            pickup["latitude"], pickup["longitude"],
            delivery["latitude"], delivery["longitude"]
        )
        
        # Base fee
        base_fee = self.base_fees.get(vehicle_type, 15.0)
        
        # Distance cost
        distance_cost = distance_km * self.per_km_rate
        
        # Surge pricing (rush hours)
        current_hour = datetime.utcnow().hour
        surge_multiplier = 1.3 if current_hour in self.surge_hours else 1.0
        
        # Total
        total = (base_fee + distance_cost) * surge_multiplier
        
        return {
            "base_fee": round(base_fee, 2),
            "distance_km": round(distance_km, 2),
            "distance_cost": round(distance_cost, 2),
            "surge_multiplier": surge_multiplier,
            "total_estimate": round(total, 2),
            "currency": "ZAR"
        }
    
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
    
    async def request_delivery(self, customer_id: str, delivery_data: dict) -> dict:
        """Main delivery request flow"""
        
        # 1. Validate customer
        customer = await self.db.users.find_one({"_id": customer_id})
        if not customer:
            raise ValueError("Customer not found")
        
        # 2. Check for existing active delivery
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
        
        # 5. Find and assign rider (async in background)
        asyncio.create_task(self._assign_rider(delivery_id, delivery.dict(), fare_estimate))
        
        return {
            "delivery_id": str(delivery_id),
            "status": "pending",
            "fare_estimate": fare_estimate,
            "message": "Finding nearby riders..."
        }
    
    async def _assign_rider(self, delivery_id, delivery_data: dict, fare_estimate: dict):
        """Assign a rider to the delivery with retry logic"""
        
        max_attempts = 3
        attempted_riders = []
        
        for attempt in range(max_attempts):
            rider = await self.find_nearest_rider(
                delivery_data["pickup_location"],
                delivery_data.get("vehicle_type", "bike"),
                attempted_riders
            )
            
            if rider:
                # Assign rider
                await self.db.deliveries.update_one(
                    {"_id": delivery_id},
                    {
                        "$set": {
                            "rider_id": rider["_id"],
                            "status": "rider_assigned",
                            "rider_assigned_at": datetime.utcnow()
                        }
                    }
                )
                
                # Notify rider (push notification)
                await self._notify_rider(rider["_id"], str(delivery_id))
                return
            
            attempted_riders.append(rider["_id"] if rider else None)
            await asyncio.sleep(2)  # Wait before retry
        
        # No rider found
        await self.db.deliveries.update_one(
            {"_id": delivery_id},
            {"$set": {"status": "cancelled", "cancel_reason": "no_riders_available"}}
        )
        
        # Notify customer
        await self._notify_customer(delivery_data["customer_id"], "No riders available. Please try again.")
    
    async def _notify_rider(self, rider_id: str, delivery_id: str):
        """Send push notification to rider"""
        # TODO: Implement Firebase Cloud Messaging
        notification = {
            "rider_id": rider_id,
            "delivery_id": delivery_id,
            "type": "delivery_request",
            "message": "New delivery request nearby!",
            "created_at": datetime.utcnow()
        }
        await self.db.notifications.insert_one(notification)
    
    async def _notify_customer(self, customer_id: str, message: str):
        """Send push notification to customer"""
        notification = {
            "customer_id": customer_id,
            "type": "delivery_update",
            "message": message,
            "created_at": datetime.utcnow()
        }
        await self.db.notifications.insert_one(notification)
    
    async def _notify_merchant(self, merchant_id: str, message: str, delivery_id: str = None):
        """Send push notification to merchant"""
        notification = {
            "merchant_id": merchant_id,
            "delivery_id": delivery_id,
            "type": "delivery_update",
            "message": message,
            "created_at": datetime.utcnow()
        }
        await self.db.notifications.insert_one(notification)
