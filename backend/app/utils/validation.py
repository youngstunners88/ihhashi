"""
Utility functions for validation and error handling
"""
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
import re
from typing import Optional


def safe_object_id(id_str: str) -> ObjectId:
    """
    Safely convert string to ObjectId with proper error handling.
    
    Args:
        id_str: String representation of MongoDB ObjectId
        
    Returns:
        ObjectId instance
        
    Raises:
        HTTPException: 400 if invalid ID format
    """
    try:
        return ObjectId(id_str)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID format")


def validate_sa_phone(phone: str) -> str:
    """
    Validate and normalize South African phone number.
    
    Accepts formats:
    - +27XXXXXXXXX
    - 27XXXXXXXXX
    - 0XXXXXXXXX
    
    Returns normalized format: +27XXXXXXXXX
    """
    if not phone:
        raise HTTPException(status_code=400, detail="Phone number is required")
    
    # Remove spaces and dashes
    phone = re.sub(r'[\s\-]', '', phone)
    
    # Check valid SA number patterns
    patterns = [
        (r'^\+27[6-8]\d{8}$', '+27'),  # Already normalized
        (r'^27[6-8]\d{8}$', '+27'),     # Missing +
        (r'^0[6-8]\d{8}$', '+27'),      # Local format
    ]
    
    for pattern, prefix in patterns:
        if re.match(pattern, phone):
            if phone.startswith('0'):
                return prefix + phone[1:]
            elif phone.startswith('27') and not phone.startswith('+27'):
                return '+' + phone
            return phone
    
    raise HTTPException(
        status_code=400, 
        detail="Invalid South African phone number. Must be format +27XXXXXXXXX"
    )


def validate_payment_amount(amount: float, min_amount: float = 1.0, max_amount: float = 50000.0) -> float:
    """
    Validate payment amount with reasonable limits.
    
    Args:
        amount: Payment amount in ZAR
        min_amount: Minimum allowed (default R1)
        max_amount: Maximum allowed (default R50,000)
        
    Returns:
        Validated amount
        
    Raises:
        HTTPException: 400 if amount out of bounds
    """
    if amount < min_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Amount must be at least R{min_amount}"
        )
    
    if amount > max_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Amount cannot exceed R{max_amount:,.0f}"
        )
    
    return round(amount, 2)


def validate_address(address: dict) -> dict:
    """
    Validate delivery address fields.
    
    Required: address_line1, city
    Optional: address_line2, area, latitude, longitude, delivery_instructions
    """
    if not address:
        raise HTTPException(status_code=400, detail="Address is required")
    
    required_fields = ['address_line1', 'city']
    
    for field in required_fields:
        if not address.get(field):
            raise HTTPException(
                status_code=400, 
                detail=f"Address field '{field}' is required"
            )
    
    # Validate coordinates if provided
    if 'latitude' in address:
        lat = address['latitude']
        if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
            raise HTTPException(status_code=400, detail="Invalid latitude")
    
    if 'longitude' in address:
        lng = address['longitude']
        if not isinstance(lng, (int, float)) or lng < -180 or lng > 180:
            raise HTTPException(status_code=400, detail="Invalid longitude")
    
    return address


def validate_email(email: str) -> str:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not re.match(email_pattern, email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    return email.lower().strip()


def validate_password(password: str) -> str:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=400, 
            detail="Password must be at least 8 characters"
        )
    
    if not re.search(r'[A-Z]', password):
        raise HTTPException(
            status_code=400, 
            detail="Password must contain at least one uppercase letter"
        )
    
    if not re.search(r'[a-z]', password):
        raise HTTPException(
            status_code=400, 
            detail="Password must contain at least one lowercase letter"
        )
    
    if not re.search(r'\d', password):
        raise HTTPException(
            status_code=400, 
            detail="Password must contain at least one number"
        )
    
    return password
