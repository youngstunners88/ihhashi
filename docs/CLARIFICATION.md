# iHhashi Platform - Important Clarifications

## Commit History Correction

**Date:** 2026-03-02

### Issue
An earlier commit message incorrectly stated:
> "Initial commit: taxi safety app"

### Correction
**iHhashi is NOT a taxi safety app.** iHhashi is a comprehensive **delivery platform** designed for:
- Food delivery
- Package delivery
- Grocery delivery
- Any on-demand delivery services

### Platform Overview

iHhashi connects three key stakeholders:

1. **Customers** - Place orders through mobile/web apps
2. **Restaurants/Retailers** - Manage menu/inventory and fulfill orders
3. **Riders** - Pick up and deliver orders to customers

### Key Features

| Feature | Description |
|---------|-------------|
| Real-time Order Tracking | Live GPS tracking of deliveries |
| Payment Processing | Integrated Stripe/Paystack payments |
| WebSocket Notifications | Real-time order status updates |
| Rider Management | Location tracking, assignment algorithms |
| Restaurant Portal | Menu management, order acceptance |
| Customer App | iOS/Android apps for ordering |

### Architecture

```
iHhashi Delivery Platform
├── Backend API (FastAPI)
├── Mobile Apps (React Native)
├── Web Dashboard (React)
├── Real-time Services (WebSocket + Redis Pub/Sub)
├── Background Workers (Celery)
└── Infrastructure (Docker, Kubernetes, Terraform)
```

### Why The Confusion?

The initial commit message was a template error that referenced an unrelated project. All subsequent development and documentation correctly identifies iHhashi as a delivery platform.

### Version History

| Version | Description |
|---------|-------------|
| v0.1.0 | Initial delivery platform structure |
| v0.2.0 | WebSocket real-time updates |
| v0.3.0 | Payment integration (Stripe) |
| v0.4.0 | Security hardening phase |
| v0.4.1 | Security hardening phase 2 |
| v0.4.2 | Security hardening phase 3 |
| v0.5.0 | Production readiness (current) |

---

**Note:** This document serves as the official correction to any commit messages or documentation that may incorrectly describe iHhashi as a taxi safety application.
