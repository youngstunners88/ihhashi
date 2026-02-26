# API Reference

> Backend API endpoints for iHhashi

**Base URL**: `https://api.ihhashi.com` (TBD)

---

## Authentication

### POST /auth/register
Register a new user.

**Body**:
```json
{
  "email": "user@example.com",
  "password": "secure123",
  "phone": "+27123456789",
  "role": "customer"
}
```

### POST /auth/login
Login and get JWT token.

**Body**:
```json
{
  "email": "user@example.com",
  "password": "secure123"
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "abc123",
    "email": "user@example.com",
    "role": "customer"
  }
}
```

---

## Users

### GET /users/me
Get current user profile.

**Headers**: `Authorization: Bearer <token>`

### PUT /users/me
Update current user profile.

**Body**:
```json
{
  "phone": "+27123456789",
  "location": {
    "lat": -26.2041,
    "lng": 28.0473
  }
}
```

---

## Merchants

### GET /merchants
List merchants near location.

**Query**: `?lat=-26.2041&lng=28.0473&category=restaurant`

### GET /merchants/:id
Get merchant details.

### GET /merchants/:id/menu
Get merchant menu.

### POST /merchants
Create merchant (requires merchant role).

### PUT /merchants/:id
Update merchant details.

---

## Orders

### POST /orders
Create a new order.

**Body**:
```json
{
  "merchant_id": "merchant123",
  "items": [
    {"item_id": "item1", "quantity": 2},
    {"item_id": "item2", "quantity": 1}
  ],
  "delivery_address": {
    "lat": -26.2041,
    "lng": 28.0473,
    "address": "123 Main St"
  }
}
```

### GET /orders
Get user's orders.

### GET /orders/:id
Get order details.

### PUT /orders/:id/status
Update order status (merchant/rider only).

**Body**:
```json
{
  "status": "preparing"
}
```

---

## Riders

### GET /riders
List available riders.

### GET /riders/me
Get rider profile.

### PUT /riders/me/status
Update rider status.

**Body**:
```json
{
  "status": "available"
}
```

### GET /riders/me/earnings
Get rider earnings summary.

---

## Webhooks

### POST /webhooks/stripe
Handle Stripe payment events.

### POST /webhooks/supabase
Handle Supabase auth events.

---

#iHhashi #api