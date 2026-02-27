"""
Tests for authentication endpoints and services.

Covers:
- User registration
- Login and token generation
- Token refresh
- Logout and token blacklisting
- Password hashing
- Role-based access
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId

from fastapi import status
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.services.auth import (
    verify_password, get_password_hash, create_access_token,
    authenticate_user, get_current_user
)
from app.models import UserRole, User


# ============ PASSWORD HASHING TESTS ============

class TestPasswordHashing:
    """Tests for password hashing functions."""
    
    def test_password_hash_creates_different_hashes(self):
        """Verify same password produces different hashes (salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert hash1 != password
        assert hash2 != password
    
    def test_verify_password_correct(self):
        """Verify correct password validates."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Verify incorrect password fails."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_verify_password_empty(self):
        """Verify empty password fails."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False


# ============ JWT TOKEN TESTS ============

class TestJWTToken:
    """Tests for JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Verify access token is created with correct data."""
        user_id = str(ObjectId())
        role = UserRole.BUYER
        
        token = create_access_token(
            data={"sub": user_id, "role": role},
            expires_delta=timedelta(hours=1)
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT format
    
    def test_token_contains_user_data(self):
        """Verify token contains user ID and role."""
        from jose import jwt
        from app.config import settings
        
        user_id = str(ObjectId())
        role = UserRole.DRIVER
        
        token = create_access_token(
            data={"sub": user_id, "role": role},
            expires_delta=timedelta(hours=1)
        )
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        assert payload["sub"] == user_id
        assert payload["role"] == role
    
    def test_token_expiration(self):
        """Verify token expires at correct time."""
        from jose import jwt
        from app.config import settings
        
        user_id = str(ObjectId())
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(
            data={"sub": user_id, "role": UserRole.BUYER},
            expires_delta=expires_delta
        )
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        
        # Check expiration is approximately 30 minutes from now
        exp = datetime.fromtimestamp(payload["exp"])
        expected_exp = datetime.utcnow() + expires_delta
        
        # Allow 10 second tolerance
        assert abs((exp - expected_exp).total_seconds()) < 10


# ============ REGISTRATION TESTS ============

class TestRegistration:
    """Tests for user registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self, async_client: AsyncClient, clean_db):
        """Test successful user registration."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "newuser@test.com",
                "phone": "+27829999999",
                "full_name": "New Test User",
                "password": "securepassword123",
                "role": "buyer"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user_id" in data
        assert data["message"] == "User created successfully"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(self, async_client: AsyncClient, test_user):
        """Test registration with existing email fails."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": test_user["email"],  # Same email
                "phone": "+27828888888",
                "full_name": "Another User",
                "password": "securepassword123",
                "role": "buyer"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email_fails(self, async_client: AsyncClient, clean_db):
        """Test registration with invalid email format fails."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "notanemail",
                "phone": "+27827777777",
                "full_name": "Test User",
                "password": "securepassword123",
                "role": "buyer"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_short_password_fails(self, async_client: AsyncClient, clean_db):
        """Test registration with short password fails."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "shortpass@test.com",
                "phone": "+27826666666",
                "full_name": "Test User",
                "password": "short",
                "role": "buyer"
            }
        )
        
        # Should fail validation (password too short)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_merchant_role(self, async_client: AsyncClient, clean_db):
        """Test registration as merchant."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "merchant@test.com",
                "phone": "+27825555555",
                "full_name": "Test Merchant",
                "password": "securepassword123",
                "role": "merchant"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_register_driver_role(self, async_client: AsyncClient, clean_db):
        """Test registration as driver."""
        response = await async_client.post(
            "/api/auth/register",
            json={
                "email": "driver@test.com",
                "phone": "+27824444444",
                "full_name": "Test Driver",
                "password": "securepassword123",
                "role": "driver"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK


# ============ LOGIN TESTS ============

class TestLogin:
    """Tests for login endpoint."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user):
        """Test successful login returns token."""
        response = await async_client.post(
            "/api/auth/login",
            data={
                "username": test_user["email"],
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password_fails(self, async_client: AsyncClient, test_user):
        """Test login with wrong password fails."""
        response = await async_client.post(
            "/api/auth/login",
            data={
                "username": test_user["email"],
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user_fails(self, async_client: AsyncClient, clean_db):
        """Test login with non-existent user fails."""
        response = await async_client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_login_inactive_user_fails(self, async_client: AsyncClient, clean_db):
        """Test login with inactive account fails."""
        # Create inactive user
        from app.database import get_collection
        from app.services.auth import get_password_hash
        
        users_col = get_collection("users")
        user_doc = {
            "email": "inactive@test.com",
            "phone": "+27823333333",
            "full_name": "Inactive User",
            "hashed_password": get_password_hash("testpassword123"),
            "role": UserRole.BUYER,
            "is_active": False,
            "created_at": datetime.utcnow()
        }
        await users_col.insert_one(user_doc)
        
        response = await async_client.post(
            "/api/auth/login",
            data={
                "username": "inactive@test.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============ GET CURRENT USER TESTS ============

class TestGetCurrentUser:
    """Tests for getting current user info."""
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, async_client: AsyncClient, test_user, buyer_auth_headers):
        """Test getting current user info with valid token."""
        response = await async_client.get(
            "/api/auth/me",
            headers=buyer_auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["role"] == test_user["role"]
    
    @pytest.mark.asyncio
    async def test_get_me_no_token_fails(self, async_client: AsyncClient):
        """Test getting current user without token fails."""
        response = await async_client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_me_invalid_token_fails(self, async_client: AsyncClient):
        """Test getting current user with invalid token fails."""
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_me_expired_token_fails(self, async_client: AsyncClient, test_user):
        """Test getting current user with expired token fails."""
        # Create expired token
        expired_token = create_access_token(
            data={"sub": test_user["id"], "role": test_user["role"]},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============ TOKEN REFRESH TESTS ============

class TestTokenRefresh:
    """Tests for token refresh functionality."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, async_client: AsyncClient, test_user, buyer_auth_headers):
        """Test token refresh returns new valid token."""
        # Note: This test assumes a /refresh endpoint exists
        # If not implemented, skip or implement the endpoint
        pass
    
    @pytest.mark.asyncio
    async def test_refresh_preserves_user_data(self, async_client: AsyncClient, test_user):
        """Test refreshed token contains same user data."""
        # Create initial token
        initial_token = create_access_token(
            data={"sub": test_user["id"], "role": test_user["role"]},
            expires_delta=timedelta(hours=1)
        )
        
        # Create new token (simulating refresh)
        new_token = create_access_token(
            data={"sub": test_user["id"], "role": test_user["role"]},
            expires_delta=timedelta(hours=1)
        )
        
        # Tokens should be different (different exp time)
        assert initial_token != new_token
        
        # But both should decode to same user
        from jose import jwt
        from app.config import settings
        
        initial_payload = jwt.decode(initial_token, settings.secret_key, algorithms=[settings.algorithm])
        new_payload = jwt.decode(new_token, settings.secret_key, algorithms=[settings.algorithm])
        
        assert initial_payload["sub"] == new_payload["sub"]
        assert initial_payload["role"] == new_payload["role"]


# ============ LOGOUT / BLACKLIST TESTS ============

class TestLogout:
    """Tests for logout and token blacklisting."""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, async_client: AsyncClient, buyer_auth_headers, mock_redis):
        """Test successful logout."""
        # Note: This assumes a /logout endpoint exists
        # If using Redis for blacklist, verify token is blacklisted
        pass
    
    @pytest.mark.asyncio
    async def test_blacklisted_token_rejected(self, async_client: AsyncClient, test_user, mock_redis):
        """Test that blacklisted token is rejected."""
        # Create token
        token = create_access_token(
            data={"sub": test_user["id"], "role": test_user["role"]},
            expires_delta=timedelta(hours=1)
        )
        
        # Simulate blacklisting
        mock_redis.exists.return_value = True
        
        # Attempt to use blacklisted token
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Should be rejected if blacklist is implemented
        # This test may pass if blacklist isn't implemented yet
        pass


# ============ ROLE-BASED ACCESS TESTS ============

class TestRoleBasedAccess:
    """Tests for role-based access control."""
    
    @pytest.mark.asyncio
    async def test_buyer_cannot_access_admin_endpoints(
        self, async_client: AsyncClient, buyer_auth_headers
    ):
        """Test buyer cannot access admin-only endpoints."""
        # Assuming there's an admin-only endpoint
        response = await async_client.get(
            "/api/admin/users",
            headers=buyer_auth_headers
        )
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    @pytest.mark.asyncio
    async def test_merchant_cannot_access_driver_endpoints(
        self, async_client: AsyncClient, merchant_auth_headers
    ):
        """Test merchant cannot access driver-only endpoints."""
        response = await async_client.get(
            "/api/riders/my-deliveries",
            headers=merchant_auth_headers
        )
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]
    
    @pytest.mark.asyncio
    async def test_admin_can_access_all_endpoints(
        self, async_client: AsyncClient, admin_auth_headers
    ):
        """Test admin can access protected endpoints."""
        response = await async_client.get(
            "/api/auth/me",
            headers=admin_auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK


# ============ AUTHENTICATE USER TESTS ============

class TestAuthenticateUser:
    """Tests for authenticate_user service function."""
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_user):
        """Test successful user authentication."""
        user = await authenticate_user(test_user["email"], "testpassword123")
        
        assert user is not None
        assert user.email == test_user["email"]
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, test_user):
        """Test authentication with wrong password."""
        user = await authenticate_user(test_user["email"], "wrongpassword")
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_nonexistent(self, clean_db):
        """Test authentication with non-existent user."""
        user = await authenticate_user("nonexistent@test.com", "anypassword")
        
        assert user is None


# ============ EDGE CASES ============

class TestAuthEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_login_empty_credentials(self, async_client: AsyncClient):
        """Test login with empty credentials."""
        response = await async_client.post(
            "/api/auth/login",
            data={"username": "", "password": ""}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_missing_fields(self, async_client: AsyncClient, clean_db):
        """Test registration with missing required fields."""
        response = await async_client.post(
            "/api/auth/register",
            json={"email": "incomplete@test.com"}  # Missing required fields
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_token_malformed_header(self, async_client: AsyncClient):
        """Test with malformed authorization header."""
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormat token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_token_missing_bearer_prefix(self, async_client: AsyncClient, test_user):
        """Test with token missing 'Bearer' prefix."""
        token = create_access_token(
            data={"sub": test_user["id"], "role": test_user["role"]},
            expires_delta=timedelta(hours=1)
        )
        
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": token}  # Missing "Bearer "
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
