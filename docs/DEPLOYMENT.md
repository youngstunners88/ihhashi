# iHhashi Delivery Platform - Deployment Guide

Complete deployment guide for the iHhashi delivery platform.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Variables](#environment-variables)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Application Deployment](#application-deployment)
5. [Health Checks](#health-checks)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Local development |
| kubectl | 1.28+ | Kubernetes management |
| Terraform | 1.6+ | Infrastructure provisioning |
| AWS CLI | 2.13+ | AWS resource management |
| Node.js | 20.x | Frontend/Mobile builds |
| Python | 3.11+ | Backend runtime |

### Required Accounts

- [ ] AWS Account with appropriate permissions
- [ ] GitHub account with Container Registry access
- [ ] MongoDB Atlas account (or self-hosted MongoDB)
- [ ] Redis Cloud account (or self-hosted Redis)
- [ ] Stripe account (payments)
- [ ] Paystack account (Africa payments)
- [ ] SendGrid account (emails)
- [ ] Twilio account (SMS)
- [ ] Firebase project (push notifications)
- [ ] Google Cloud (Maps API)

---

## Environment Variables

### Backend Environment Variables

Create a `.env` file in `backend/` directory:

```bash
# Application
APP_NAME="iHhashi Delivery"
APP_VERSION="1.0.0"
ENVIRONMENT="production"
DEBUG=false
SECRET_KEY="your-super-secret-key-min-32-chars"
INSTANCE_ID="backend-1"

# MongoDB
MONGODB_URL="mongodb+srv://user:pass@cluster.mongodb.net/ihhashi"
MONGODB_DB_NAME="ihhashi"
MONGODB_MAX_POOL_SIZE=100
MONGODB_MIN_POOL_SIZE=10
MONGODB_MAX_IDLE_TIME_MS=60000
MONGODB_WAIT_QUEUE_TIMEOUT_MS=5000
MONGODB_CONNECT_TIMEOUT_MS=10000
MONGODB_SOCKET_TIMEOUT_MS=30000
MONGODB_SERVER_SELECTION_TIMEOUT_MS=30000

# Redis
REDIS_URL="redis://username:password@redis-host:6379/0"
REDIS_PASSWORD=""

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Payment - Stripe
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Payment - Paystack
PAYSTACK_SECRET_KEY="sk_live_..."
PAYSTACK_PUBLIC_KEY="pk_live_..."

# Communication - SendGrid
SENDGRID_API_KEY="SG."
FROM_EMAIL="noreply@yourapp.com"

# Communication - Twilio
TWILIO_ACCOUNT_SID="AC..."
TWILIO_AUTH_TOKEN="..."
TWILIO_PHONE_NUMBER="+1234567890"

# Firebase
FIREBASE_PROJECT_ID="your-project"
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
FIREBASE_CLIENT_EMAIL="firebase-adminsdk@..."
FIREBASE_CREDENTIALS_PATH="/secrets/firebase-credentials.json"

# External APIs
GOOGLE_MAPS_API_KEY="AIza..."

# Monitoring
SENTRY_DSN="https://...@sentry.io/..."
LOG_LEVEL="INFO"
```

### Frontend Environment Variables

Create `.env.production` in `frontend/`:

```bash
VITE_API_URL=https://api.yourapp.com
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_PAYSTACK_PUBLIC_KEY=pk_live_...
VITE_GOOGLE_MAPS_API_KEY=AIza...
VITE_FIREBASE_API_KEY=...
```

### Mobile Environment Variables

Create `.env.production` in `mobile/`:

```bash
EXPO_PUBLIC_API_URL=https://api.yourapp.com
EXPO_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_...
EXPO_PUBLIC_PAYSTACK_PUBLIC_KEY=pk_live_...
EXPO_PUBLIC_GOOGLE_MAPS_API_KEY=AIza...
```

---

## Infrastructure Setup

### Step 1: AWS Infrastructure with Terraform

```bash
cd deployment/terraform

# Initialize Terraform
terraform init

# Create workspace for environment
terraform workspace new production

# Plan changes
terraform plan -var="environment=production" \
  -var="db_username=admin" \
  -var="db_password=$(openssl rand -base64 32)"

# Apply changes
terraform apply -auto-approve
```

**Outputs:**
- EKS cluster endpoint
- DocumentDB endpoint
- Redis endpoint
- S3 bucket name
- CloudFront domain

### Step 2: Configure kubectl

```bash
# Update kubeconfig
aws eks update-kubeconfig --region us-east-1 --name ihhashi-cluster

# Verify connection
kubectl get nodes
```

### Step 3: Deploy Kubernetes Resources

```bash
cd deployment/k8s

# Apply namespace
kubectl apply -f namespace.yaml

# Apply configmaps and secrets
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml

# Deploy Redis
kubectl apply -f redis-deployment.yaml

# Deploy backend with HPA
kubectl apply -f backend-deployment.yaml

# Deploy Celery workers
kubectl apply -f celery-deployment.yaml

# Apply ingress
kubectl apply -f ingress.yaml
```

### Step 4: Verify Deployments

```bash
# Check pods
kubectl get pods -n delivery-app

# Check services
kubectl get svc -n delivery-app

# Check HPA
kubectl get hpa -n delivery-app

# View logs
kubectl logs -n delivery-app -l app=backend --tail=100
```

---

## Application Deployment

### Backend Deployment

```bash
cd backend

# Build Docker image
docker build -t ghcr.io/yourusername/ihhashi-backend:v1.0.0 .

# Push to registry
docker push ghcr.io/yourusername/ihhashi-backend:v1.0.0

# Update deployment
kubectl set image deployment/backend backend=ghcr.io/yourusername/ihhashi-backend:v1.0.0 -n delivery-app

# Wait for rollout
kubectl rollout status deployment/backend -n delivery-app
```

### Frontend Deployment

```bash
cd frontend

# Install dependencies
npm ci

# Build production
npm run build

# Deploy to S3/CloudFront
aws s3 sync dist/ s3://your-bucket-name/
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

### Mobile App Deployment

```bash
cd mobile

# Install dependencies
npm ci

# Build for production
npx expo build:android --release-channel production
npx expo build:ios --release-channel production

# Or using EAS
 eas build --platform all --profile production
```

---

## Health Checks

### Endpoint Verification

```bash
# Health check
 curl https://api.yourapp.com/health

# Expected response:
# {
#   "status": "healthy",
#   "database": {"status": "healthy", "version": "7.0"},
#   "redis": {"status": "connected"},
#   "instance_id": "backend-1"
# }

# Readiness check
curl https://api.yourapp.com/ready
# Expected: {"ready": true}

# Reconciliation status
curl https://api.yourapp.com/admin/reconciliation/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Database Connectivity

```bash
# Connect to MongoDB
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/ihhashi" --eval "db.adminCommand('ping')"

# Check Redis
redis-cli -h your-redis-host -a your-password ping
```

### WebSocket Verification

```bash
# Test WebSocket connection with authentication
wscat -c "wss://api.yourapp.com/api/v1/ws/user/123?token=YOUR_JWT_TOKEN"

# Send ping
> {"action": "ping"}
# Expected: {"type": "pong"}
```

---

## Post-Deployment Verification

### Critical Checks

- [ ] All pods running (`kubectl get pods -n delivery-app`)
- [ ] Services accessible (`kubectl get svc -n delivery-app`)
- [ ] Ingress working (`curl https://api.yourapp.com/health`)
- [ ] SSL certificate valid
- [ ] Database migrations applied
- [ ] Redis connection established
- [ ] Payment webhooks configured
- [ ] Email service working
- [ ] SMS service working
- [ ] Push notifications working
- [ ] Maps API responding

### Smoke Tests

```bash
# 1. User registration
curl -X POST https://api.yourapp.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!", "full_name": "Test User"}'

# 2. Create order
curl -X POST https://api.yourapp.com/api/v1/orders \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"restaurant_id": "...", "items": [...]}'

# 3. Process payment
curl -X POST https://api.yourapp.com/api/v1/payments \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": "...", "payment_method": "card"}'
```

---

## Troubleshooting

### Common Issues

#### Pods stuck in Pending
```bash
# Check events
kubectl describe pod <pod-name> -n delivery-app

# Check resource quotas
kubectl describe resourcequota -n delivery-app

# Check node capacity
kubectl top nodes
```

#### Database Connection Failures
```bash
# Check network policy
kubectl get networkpolicies -n delivery-app

# Test connectivity from pod
kubectl exec -it <backend-pod> -n delivery-app -- python -c "from app.database import connect_db; import asyncio; asyncio.run(connect_db())"
```

#### WebSocket Connection Issues
```bash
# Check ingress annotations
kubectl get ingress -n delivery-app -o yaml | grep websocket

# Verify Nginx configuration
kubectl exec -it <nginx-pod> -- nginx -T | grep websocket
```

#### High Memory Usage
```bash
# Check pod metrics
kubectl top pods -n delivery-app

# Review HPA status
kubectl describe hpa backend-hpa -n delivery-app

# Check for memory leaks in logs
kubectl logs -n delivery-app -l app=backend | grep -i memory
```

### Log Collection

```bash
# Export logs
kubectl logs -n delivery-app -l app=backend --all-containers > backend-logs.txt

# Stream logs
kubectl logs -f -n delivery-app -l app=backend --all-containers

# Previous container logs
kubectl logs -n delivery-app <pod-name> --previous
```

### Rollback Procedure

```bash
# Rollback deployment
kubectl rollout undo deployment/backend -n delivery-app

# Check rollout history
kubectl rollout history deployment/backend -n delivery-app

# Rollback to specific revision
kubectl rollout undo deployment/backend -n delivery-app --to-revision=3
```

---

## Support Contacts

| Issue Type | Contact |
|------------|---------|
| Infrastructure | devops@yourapp.com |
| Backend API | backend@yourapp.com |
| Mobile Apps | mobile@yourapp.com |
| Payments | payments@yourapp.com |
| Emergency | +1-XXX-XXX-XXXX |

---

## Security Checklist

- [ ] Secrets stored in AWS Secrets Manager or Kubernetes Secrets
- [ ] Database passwords rotated regularly
- [ ] API keys have restricted permissions
- [ ] Webhook signatures verified
- [ ] TLS 1.3 enabled
- [ ] Security headers configured
- [ ] Rate limiting active
- [ ] DDoS protection enabled
- [ ] Audit logging enabled
- [ ] Backup encryption enabled

---

**Last Updated:** 2026-03-02  
**Version:** 1.0.0  
**Maintainer:** Platform Team
