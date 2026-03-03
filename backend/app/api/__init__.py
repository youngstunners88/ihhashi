# iHhashi API Routes

from fastapi import APIRouter

auth = APIRouter()
products = APIRouter()
orders = APIRouter()
buyers = APIRouter()


@auth.post("/request-otp")
async def request_otp(phone_number: str):
    """Request OTP for phone number authentication"""
    # TODO: Implement OTP generation and SMS sending via Twilio
    return {"message": f"OTP sent to {phone_number}", "success": True}


@auth.post("/verify-otp")
async def verify_otp(phone_number: str, otp_code: str):
    """Verify OTP and return auth token"""
    # TODO: Implement OTP verification
    return {
        "message": "Authentication successful",
        "token": "mock-jwt-token",
        "buyer": {
            "id": "buyer-123",
            "phone_number": phone_number,
            "is_new": True
        }
    }


@products.get("/")
async def list_products(
    category: str = None,
    search: str = None,
    store_id: str = None,
    limit: int = 20,
    offset: int = 0
):
    """List products with optional filters"""
    # TODO: Implement actual database query
    return {
        "products": [
            {
                "id": "prod-1",
                "name": "Stainless Steel Spork",
                "category": "utensils",
                "price": 45.00,
                "image_url": "https://example.com/spork.jpg"
            },
            {
                "id": "prod-2",
                "name": "Bic Ballpoint Pens (Pack of 10)",
                "category": "stationery",
                "price": 35.00,
                "image_url": "https://example.com/pens.jpg"
            }
        ],
        "total": 2,
        "limit": limit,
        "offset": offset
    }


@products.get("/{product_id}")
async def get_product(product_id: str):
    """Get single product details"""
    return {
        "id": product_id,
        "name": "Stainless Steel Spork",
        "description": "Durable 3-in-1 utensil for everyday use",
        "category": "utensils",
        "price": 45.00,
        "stock_quantity": 50,
        "image_url": "https://example.com/spork.jpg"
    }


@orders.post("/")
async def create_order(order_data: dict):
    """Create a new order"""
    # TODO: Implement order creation
    return {
        "message": "Order created successfully",
        "order_id": "order-123",
        "status": "pending",
        "estimated_delivery": "30-45 minutes"
    }


@orders.get("/{order_id}")
async def get_order(order_id: str):
    """Get order details and status"""
    return {
        "id": order_id,
        "status": "in_transit",
        "items": [
            {"name": "Stainless Steel Spork", "quantity": 2, "price": 45.00}
        ],
        "total": 115.00,
        "delivery_address": "123 Main Street, Johannesburg",
        "rider": {
            "name": "John",
            "phone": "+27821234567",
            "location": {"lat": -26.2041, "lng": 28.0473}
        },
        "estimated_arrival": "12:45"
    }


@orders.get("/")
async def list_buyer_orders(buyer_id: str, limit: int = 10):
    """List orders for a buyer"""
    return {
        "orders": [
            {
                "id": "order-123",
                "status": "delivered",
                "total": 95.00,
                "created_at": "2024-01-15T10:30:00Z",
                "item_count": 2
            }
        ],
        "total": 1
    }


@buyers.get("/me")
async def get_current_buyer():
    """Get current buyer profile"""
    return {
        "id": "buyer-123",
        "phone_number": "+27821234567",
        "full_name": "Thandi Nkosi",
        "addresses": [
            {
                "id": "addr-1",
                "label": "Home",
                "address_line1": "123 Main Street",
                "city": "Johannesburg",
                "is_default": True
            }
        ],
        "total_orders": 5,
        "preferred_categories": ["utensils", "stationery"]
    }


@buyers.post("/addresses")
async def add_address(address_data: dict):
    """Add a new delivery address"""
    return {
        "message": "Address added successfully",
        "address_id": "addr-new"
    }