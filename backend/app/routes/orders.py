"""
Order API routes - Full implementation with MongoDB
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.services.auth import get_current_user
from app.models import (
    Order, OrderCreate, OrderStatus, OrderStatusUpdate,
    OrderItem, DeliveryInfo, User, UserRole
)
from app.database import get_collection
from app.utils.validation import safe_object_id

router = APIRouter(prefix="/orders", tags=["orders"])


def order_from_doc(doc: dict) -> dict:
    """Convert MongoDB doc to order dict"""
    if doc:
        doc["id"] = str(doc.get("_id", doc.get("id")))
    return doc


async def calculate_delivery_fee(store_location: dict, delivery_location: dict) -> float:
    """Calculate delivery fee based on distance"""
    # Base fee: R15
    # Per km: R8
    # Max distance: 15km
    
    import math
    
    lat1 = store_location.get("latitude", 0)
    lon1 = store_location.get("longitude", 0)
    lat2 = delivery_location.get("latitude", 0)
    lon2 = delivery_location.get("longitude", 0)
    
    # Haversine formula
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    # Calculate fee
    base_fee = 15.0
    per_km = 8.0
    fee = base_fee + (distance * per_km)
    
    return min(fee, 150.0)  # Cap at R150


async def find_nearest_available_rider(lat: float, lng: float, max_distance_km: float = 5.0):
    """Find the nearest available rider"""
    drivers_col = get_collection("drivers")
    
    # Geo query for nearby available drivers
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [lng, lat]},
                "distanceField": "distance",
                "maxDistance": max_distance_km * 1000,  # Convert to meters
                "query": {"status": "available"},
                "spherical": True
            }
        },
        {"$limit": 1}
    ]
    
    # Fallback if no geo index
    try:
        cursor = drivers_col.aggregate(pipeline)
        riders = await cursor.to_list(length=1)
        if riders:
            return riders[0]
    except Exception:
        pass
    
    # Simple fallback - find any available driver
    rider = await drivers_col.find_one({"status": "available"})
    return rider


@router.post("/", response_model=dict)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new order"""
    orders_col = get_collection("orders")
    buyers_col = get_collection("buyers")
    products_col = get_collection("products")
    stores_col = get_collection("stores")
    
    # Validate buyer exists
    buyer = await buyers_col.find_one({"id": current_user.id})
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer profile not found")
    
    # Get delivery address
    delivery_address = None
    for addr in buyer.get("addresses", []):
        if addr.get("id") == order_data.delivery_address_id:
            delivery_address = addr
            break
    
    if not delivery_address:
        raise HTTPException(status_code=400, detail="Delivery address not found")
    
    # Get store info - using safe ObjectId
    try:
        store = await stores_col.find_one({"_id": safe_object_id(order_data.store_id)})
    except HTTPException:
        raise HTTPException(status_code=404, detail="Store not found")
    
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    # Validate and build order items
    items = []
    subtotal = 0.0
    
    for item in order_data.items:
        try:
            product = await products_col.find_one({
                "_id": safe_object_id(item["product_id"]),
                "store_id": order_data.store_id
            })
        except HTTPException:
            raise HTTPException(
                status_code=404, 
                detail=f"Product {item['product_id']} not found"
            )
        
        if not product:
            raise HTTPException(
                status_code=404, 
                detail=f"Product {item['product_id']} not found in store"
            )
        
        if product.get("stock_quantity", 0) < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.get('name')}"
            )
        
        item_total = product["price"] * item["quantity"]
        items.append({
            "product_id": item["product_id"],
            "product_name": product["name"],
            "quantity": item["quantity"],
            "unit_price": product["price"],
            "total_price": item_total
        })
        subtotal += item_total
    
    # Calculate delivery fee
    delivery_fee = await calculate_delivery_fee(
        store.get("location", {}),
        delivery_address
    )
    
    # Create order document
    order_doc = {
        "buyer_id": current_user.id,
        "store_id": order_data.store_id,
        "items": items,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": subtotal + delivery_fee,
        "currency": "ZAR",
        "status": OrderStatus.PENDING.value,
        "status_history": [{
            "status": OrderStatus.PENDING.value,
            "timestamp": datetime.utcnow().isoformat(),
            "by": current_user.id
        }],
        "delivery_info": {
            "address_label": delivery_address.get("label", ""),
            "address_line1": delivery_address.get("address_line1", ""),
            "address_line2": delivery_address.get("address_line2"),
            "city": delivery_address.get("city", ""),
            "area": delivery_address.get("area"),
            "latitude": delivery_address.get("latitude"),
            "longitude": delivery_address.get("longitude"),
            "delivery_instructions": delivery_address.get("delivery_instructions"),
            "recipient_phone": buyer.get("phone_number", "")
        },
        "created_at": datetime.utcnow(),
        "payment_method": order_data.payment_method,
        "payment_status": "pending",
        "buyer_notes": order_data.buyer_notes
    }
    
    result = await orders_col.insert_one(order_doc)
    order_doc["id"] = str(result.inserted_id)
    
    # TODO: Send notification to merchant
    # TODO: Initiate payment if card/wallet
    
    return {
        "message": "Order created successfully",
        "order_id": order_doc["id"],
        "total": order_doc["total"],
        "delivery_fee": delivery_fee,
        "estimated_delivery": "30-45 minutes"
    }


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get order details"""
    orders_col = get_collection("orders")
    
    order = None
    try:
        order = await orders_col.find_one({"_id": safe_object_id(order_id)})
    except HTTPException:
        order = await orders_col.find_one({"id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check access
    if order["buyer_id"] != current_user.id and order.get("rider_id") != current_user.id:
        if order["store_id"] != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Access denied")
    
    order["id"] = str(order["_id"])
    return {"order": order}


@router.get("/{order_id}/track")
async def track_order(order_id: str):
    """Track order status and rider location (public endpoint for order page)"""
    orders_col = get_collection("orders")
    drivers_col = get_collection("drivers")
    
    order = None
    try:
        order = await orders_col.find_one({"_id": safe_object_id(order_id)})
    except HTTPException:
        order = await orders_col.find_one({"id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    response = {
        "order_id": order_id,
        "status": order["status"],
        "created_at": order.get("created_at"),
        "estimated_delivery": order.get("estimated_delivery"),
        "rider": None,
        "rider_location": None
    }
    
    # If rider assigned, get their details
    if order.get("rider_id"):
        rider = await drivers_col.find_one({"id": order["rider_id"]})
        if rider:
            response["rider"] = {
                "name": rider.get("full_name", "Driver"),
                "phone": rider.get("phone"),
                "rating": rider.get("rating", 5.0),
                "vehicle": rider.get("vehicle", {})
            }
            
            if rider.get("current_location"):
                response["rider_location"] = {
                    "latitude": rider["current_location"].get("latitude"),
                    "longitude": rider["current_location"].get("longitude"),
                    "last_updated": rider["current_location"].get("last_updated")
                }
    
    return response


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update order status (merchant/rider only)"""
    orders_col = get_collection("orders")
    
    order = None
    try:
        order = await orders_col.find_one({"_id": safe_object_id(order_id)})
    except HTTPException:
        order = await orders_col.find_one({"id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate permissions
    valid_roles = [UserRole.MERCHANT, UserRole.DRIVER, UserRole.ADMIN]
    if current_user.role not in valid_roles:
        raise HTTPException(status_code=403, detail="Not authorized to update order status")
    
    # Validate status transition
    current_status = OrderStatus(order["status"])
    new_status = status_update.status
    
    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
        OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
        OrderStatus.READY: [OrderStatus.PICKED_UP, OrderStatus.CANCELLED],
        OrderStatus.PICKED_UP: [OrderStatus.IN_TRANSIT],
        OrderStatus.IN_TRANSIT: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: []
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )
    
    # Update order
    update_doc = {
        "status": new_status.value,
        "updated_at": datetime.utcnow()
    }
    
    # Add to status history
    status_entry = {
        "status": new_status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "by": current_user.id,
        "notes": status_update.notes
    }
    
    await orders_col.update_one(
        {"_id": order["_id"]},
        {
            "$set": update_doc,
            "$push": {"status_history": status_entry}
        }
    )
    
    # If delivered, update stats
    if new_status == OrderStatus.DELIVERED:
        await orders_col.update_one(
            {"_id": order["_id"]},
            {"$set": {"delivered_at": datetime.utcnow()}}
        )
        # TODO: Update buyer stats, rider earnings, store stats
    
    return {
        "message": "Status updated",
        "order_id": order_id,
        "status": new_status.value
    }


@router.get("/")
async def get_orders(
    status: Optional[OrderStatus] = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Get orders based on user role"""
    orders_col = get_collection("orders")
    
    # Build query based on role
    query = {}
    
    if current_user.role == UserRole.BUYER:
        query["buyer_id"] = current_user.id
    elif current_user.role == UserRole.DRIVER:
        query["rider_id"] = current_user.id
    elif current_user.role == UserRole.MERCHANT:
        query["store_id"] = current_user.id
    # Admin sees all
    
    if status:
        query["status"] = status.value
    
    # Get total count
    total = await orders_col.count_documents(query)
    
    # Get orders
    cursor = orders_col.find(query).sort("created_at", -1).skip(offset).limit(limit)
    orders = await cursor.to_list(length=limit)
    
    for order in orders:
        order["id"] = str(order["_id"])
    
    return {
        "orders": orders,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Cancel an order (buyer only, before rider pickup)"""
    orders_col = get_collection("orders")
    
    order = None
    try:
        order = await orders_col.find_one({"_id": safe_object_id(order_id)})
    except HTTPException:
        order = await orders_col.find_one({"id": order_id})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Only buyer can cancel
    if order["buyer_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Only the buyer can cancel")
    
    # Check if cancellable
    if order["status"] not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel order at this stage"
        )
    
    # Update order
    status_entry = {
        "status": OrderStatus.CANCELLED.value,
        "timestamp": datetime.utcnow().isoformat(),
        "by": current_user.id,
        "notes": f"Cancelled by buyer. Reason: {reason or 'Not specified'}"
    }
    
    await orders_col.update_one(
        {"_id": order["_id"]},
        {
            "$set": {
                "status": OrderStatus.CANCELLED.value,
                "cancelled_at": datetime.utcnow(),
                "cancellation_reason": reason
            },
            "$push": {"status_history": status_entry}
        }
    )
    
    # TODO: Refund if paid
    
    return {
        "message": "Order cancelled",
        "order_id": order_id,
        "refund_amount": order["total"] if order["payment_status"] == "paid" else 0
    }
