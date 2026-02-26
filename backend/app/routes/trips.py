from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from app.services.auth import get_current_user
from app.services.matching import MatchingService
from app.models.trip import Trip, TripRequest, TripStatus, TripLocationUpdate
from app.database import get_database
from datetime import datetime

router = APIRouter()


@router.post("/request")
async def request_trip(
    trip_request: TripRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Request a new trip (taxi/delivery)
    """
    if current_user.get("user_type") != "customer":
        raise HTTPException(status_code=403, detail="Only customers can request trips")
    
    matching_service = MatchingService(db)
    
    try:
        trip_data = {
            "pickup_location": {
                "latitude": trip_request.pickup_latitude,
                "longitude": trip_request.pickup_longitude,
                "address": trip_request.pickup_address
            },
            "dropoff_location": {
                "latitude": trip_request.dropoff_latitude,
                "longitude": trip_request.dropoff_longitude,
                "address": trip_request.dropoff_address
            },
            "vehicle_type": trip_request.vehicle_type,
            "payment_method": trip_request.payment_method
        }
        
        result = await matching_service.request_trip(
            str(current_user["_id"]),
            trip_data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active")
async def get_active_trip(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get current active trip for user
    """
    user_id = str(current_user["_id"])
    
    # Check as customer
    trip = await db.trips.find_one({
        "customer_id": user_id,
        "status": {"$in": ["requested", "driver_assigned", "driver_arrived", "in_progress"]}
    })
    
    # Check as driver
    if not trip:
        trip = await db.trips.find_one({
            "driver_id": user_id,
            "status": {"$in": ["driver_assigned", "driver_arrived", "in_progress"]}
        })
    
    if not trip:
        return {"status": "no_active_trip"}
    
    return Trip(**trip).dict()


@router.post("/{trip_id}/accept")
async def accept_trip(
    trip_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Driver accepts trip request
    """
    if current_user.get("user_type") != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can accept trips")
    
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["status"] != "requested":
        raise HTTPException(status_code=400, detail="Trip already assigned")
    
    # Assign driver
    await db.trips.update_one(
        {"_id": trip_id},
        {
            "$set": {
                "driver_id": str(current_user["_id"]),
                "status": "driver_assigned",
                "driver_assigned_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Trip accepted", "trip_id": trip_id}


@router.post("/{trip_id}/arrived")
async def driver_arrived(
    trip_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Driver has arrived at pickup
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["driver_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not your trip")
    
    await db.trips.update_one(
        {"_id": trip_id},
        {"$set": {"status": "driver_arrived"}}
    )
    
    return {"message": "Status updated", "status": "driver_arrived"}


@router.post("/{trip_id}/start")
async def start_trip(
    trip_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Start the trip (driver picks up customer)
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["driver_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not your trip")
    
    await db.trips.update_one(
        {"_id": trip_id},
        {
            "$set": {
                "status": "in_progress",
                "pickup_time": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Trip started", "status": "in_progress"}


@router.post("/{trip_id}/complete")
async def complete_trip(
    trip_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Complete the trip
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["driver_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not your trip")
    
    await db.trips.update_one(
        {"_id": trip_id},
        {
            "$set": {
                "status": "completed",
                "dropoff_time": datetime.utcnow(),
                "payment_status": "pending"  # Will be updated after payment
            }
        }
    )
    
    return {"message": "Trip completed", "status": "completed"}


@router.post("/{trip_id}/cancel")
async def cancel_trip(
    trip_id: str,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Cancel a trip
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    user_id = str(current_user["_id"])
    is_customer = trip["customer_id"] == user_id
    is_driver = trip.get("driver_id") == user_id
    
    if not (is_customer or is_driver):
        raise HTTPException(status_code=403, detail="Not your trip")
    
    if trip["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed trip")
    
    await db.trips.update_one(
        {"_id": trip_id},
        {
            "$set": {
                "status": "cancelled",
                "cancel_reason": reason or "cancelled_by_user"
            }
        }
    )
    
    return {"message": "Trip cancelled", "trip_id": trip_id}


@router.post("/{trip_id}/location")
async def update_location(
    trip_id: str,
    location: TripLocationUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Update driver location during trip (for tracking)
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["driver_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not your trip")
    
    # Store location update for real-time tracking
    await db.trip_locations.insert_one({
        "trip_id": trip_id,
        "latitude": location.latitude,
        "longitude": location.longitude,
        "timestamp": datetime.utcnow()
    })
    
    return {"message": "Location updated"}


@router.get("/{trip_id}")
async def get_trip(
    trip_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Get trip details
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    return Trip(**trip).dict()


@router.post("/{trip_id}/share")
async def share_trip(
    trip_id: str,
    emergency_contact_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Share trip with emergency contact (safety feature)
    """
    trip = await db.trips.find_one({"_id": trip_id})
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip["customer_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not your trip")
    
    # Add to shared list
    await db.trips.update_one(
        {"_id": trip_id},
        {"$addToSet": {"trip_shared_with": emergency_contact_id}}
    )
    
    # Notify emergency contact
    await db.notifications.insert_one({
        "user_id": emergency_contact_id,
        "type": "trip_shared",
        "trip_id": trip_id,
        "message": f"Someone shared a trip with you for safety tracking",
        "created_at": datetime.utcnow()
    })
    
    return {"message": "Trip shared with emergency contact"}
