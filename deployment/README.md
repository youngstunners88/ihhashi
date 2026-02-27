# Deployment Directory

This directory contains all deployment configurations for iHhashi.

## Files

| File | Description |
|------|-------------|
| `vercel.json` | Vercel deployment configuration for frontend |
| `render.yaml` | Render Blueprint for backend + database |
| `docker-compose.prod.yml` | Production Docker Compose setup |
| `DEPLOYMENT_CHECKLIST.md` | Step-by-step deployment guide |
| `mongo-init.js` | MongoDB initialization script |

## Directories

| Directory | Description |
|-----------|-------------|
| `nginx/` | Nginx configuration files for reverse proxy |

## Quick Deploy

### Render + Vercel (Recommended)

```bash
# Backend: Push to GitHub and create Render Blueprint
# Frontend: Deploy to Vercel
cd frontend && vercel --prod
```

### Self-Hosted (Docker)

```bash
# Set up environment
cp ../backend/.env.example .env
nano .env  # Edit with production values

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## Architecture

```
                    ┌─────────────────┐
                    │   Cloudflare    │
                    │   (CDN/DDoS)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Nginx       │
                    │  (SSL/Reverse)  │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │  Frontend   │   │   Backend   │   │  WebSocket  │
    │   (React)   │   │  (FastAPI)  │   │   (Live)    │
    └─────────────┘   └──────┬──────┘   └─────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
    │   MongoDB   │   │    Redis    │   │  GlitchTip  │
    │  (Database) │   │   (Cache)   │   │  (Errors)   │
    └─────────────┘   └─────────────┘   └─────────────┘
```

## Environment Variables

See:
- `../backend/.env.example` - Backend environment variables
- `../frontend/.env.example` - Frontend environment variables

## SSL Certificates

Certificates are managed by Let's Encrypt via Certbot:

```bash
# Initial certificate request
docker-compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot --webroot-path /var/www/certbot \
  -d ihhashi.co.za -d www.ihhashi.co.za -d api.ihhashi.co.za

# Auto-renewal is configured in the certbot container
```

## Monitoring

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs`
- **Errors**: GlitchTip dashboard
- **Analytics**: PostHog dashboard
