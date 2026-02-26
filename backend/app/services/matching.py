import asyncio
from datetime import datetime
from typing import Optional, List, Dict
from math import radians, sin, cos, sqrt, atan2


class MatchingService:
    """Driver matching and fare calculation service"""
    
    def __init__(self, db):
        self.db = db
        
        # Fare configuration (ZAR)
        self.base_fares = {
            "standard": 15.0,
            "luxury": 25.0,
            "delivery": 20.0
        }
        self.per_km_rate = 8.0
        self.per_minute_rate = 1.5
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
        dropoff: Dict,
        vehicle_type: str = "standard"
    ) -> Dict:
        """Calculate trip fare estimate"""
        
        distance_km = self.calculate_distance(
            pickup["latitude"], pickup["longitude"],
            dropoff["latitude"], dropoff["longitude"]
        )
        
        # Base fare
        base_fare = self.base_fares.get(vehicle_type, 15.0)
        
        # Distance cost
        distance_cost = distance_km * self.per_km_rate
        
        # Surge pricing (rush hours)
        current_hour = datetime.utcnow().hour
        surge_multiplier = 1.5 if current_hour in self.surge_hours else 1.0
        
        # Total
        total = (base_fare + distance_cost) * surge_multiplier
        
        return {
            "base_fare": round(base_fare, 2),
            "distance_km": round(distance_km, 2),
            "distance_cost": round(distance_cost, 2),
            "surge_multiplier": surge_multiplier,
            "total_estimate": round(total, 2),
            "currency": "ZAR"
        }
    
    async def find_nearest_driver(
        self,
        pickup_location: Dict,
        vehicle_type: str,
        excluded_drivers: List[str] = None,
        max_distance_km: float = 5.0
    ) -> Optional[Dict]:
        """Find the nearest available driver"""
        
        excluded_drivers = excluded_drivers or []
        
        # Find drivers who are:
        # - Online/available
        # - Have the right vehicle type
        # - Not in excluded list
        # - Within max distance
        drivers = await self.db.drivers.find({
            "status": "available",
            "vehicle_type": vehicle_type,
            "driver_id": {"$nin": excluded_drivers},
            "location": {"$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [pickup_location["longitude"], pickup_location["latitude"]]
                },
                "$maxDistance": max_distance_km * 1000  # Convert to meters
            }}
        }).limit(5).to_list(length=5)
        
        if not drivers:
            return None
        
        # Return nearest driver
        return drivers[0]
    
    async def request_trip(self, customer_id: str, trip_data: dict) -> dict:
        """Main trip request flow"""
        
        # 1. Validate customer
        customer = await self.db.users.find_one({"_id": customer_id})
        if not customer:
            raise ValueError("Customer not found")
        
        # 2. Check for existing active trip
        active_trip = await self.db.trips.find_one({
            "customer_id": customer_id,
            "status": {"$in": ["requested", "driver_assigned", "in_progress"]}
        })
        if active_trip:
            raise ValueError("Customer already has an active trip")
        
        # 3. Calculate fare
        fare_estimate = await self.calculate_fare(
            trip_data["pickup_location"],
            trip_data["dropoff_location"],
            trip_data.get("vehicle_type", "standard")
        )
        
        # 4. Create trip record
        from app.models.trip import Trip, TripStatus
        trip = Trip(
            customer_id=customer_id,
            pickup_location=trip_data["pickup_location"],
            dropoff_location=trip_data["dropoff_location"],
            vehicle_type=trip_data.get("vehicle_type", "standard"),
            fare=fare_estimate
        )
        
        result = await self.db.trips.insert_one(trip.dict())
        trip_id = result.inserted_id
        
        # 5. Find and assign driver (async in background)
        asyncio.create_task(self._assign_driver(trip_id, trip.dict(), fare_estimate))
        
        return {
            "trip_id": str(trip_id),
            "status": "requested",
            "fare_estimate": fare_estimate,
            "message": "Finding nearby drivers..."
        }
    
    async def _assign_driver(self, trip_id, trip_data: dict, fare_estimate: dict):
        """Assign a driver to the trip with retry logic"""
        
        max_attempts = 3
        attempted_drivers = []
        
        for attempt in range(max_attempts):
            driver = await self.find_nearest_driver(
                trip_data["pickup_location"],
                trip_data.get("vehicle_type", "standard"),
                attempted_drivers
            )
            
            if driver:
                # Assign driver
                await self.db.trips.update_one(
                    {"_id": trip_id},
                    {
                        "$set": {
                            "driver_id": driver["_id"],
                            "status": "driver_assigned",
                            "driver_assigned_at": datetime.utcnow()
                        }
                    }
                )
                
                # Notify driver (push notification)
                await self._notify_driver(driver["_id"], str(trip_id))
                return
            
            attempted_drivers.append(driver["_id"] if driver else None)
            await asyncio.sleep(2)  # Wait before retry
        
        # No driver found
        await self.db.trips.update_one(
            {"_id": trip_id},
            {"$set": {"status": "cancelled", "cancel_reason": "no_drivers_available"}}
        )
        
        # Notify customer
        await self._notify_customer(trip_data["customer_id"], "No drivers available. Please try again.")
    
    async def _notify_driver(self, driver_id: str, trip_id: str):
        """Send push notification to driver"""
        # TODO: Implement Firebase Cloud Messaging
        notification = {
            "driver_id": driver_id,
            "trip_id": trip_id,
            "type": "trip_request",
            "message": "New trip request nearby!",
            "created_at": datetime.utcnow()
        }
        await self.db.notifications.insert_one(notification)
    
    async def _notify_customer(self, customer_id: str, message: str):
        """Send push notification to customer"""
        notification = {
            "customer_id": customer_id,
            "type": "trip_update",
            "message": message,
            "created_at": datetime.utcnow()
        }
        await self.db.notifications.insert_one(notification)
