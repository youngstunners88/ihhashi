# iHhashi Deployment Configuration - Summary

## Files Created/Modified

### GitHub Actions Workflows

| File | Purpose |
|------|---------|
| `.github/workflows/deploy.yml` | Production deployment to Railway and Netlify |
| `.github/workflows/ci.yml` | Continuous integration (tests, lint, build) |

**Key fixes:**
- Fixed invalid `secrets` context in `if` conditions
- Added MongoDB service for backend tests
- Added proper health checks after deployment
- Added deployment summary reporting

### Platform Configuration

| File | Purpose |
|------|---------|
| `backend/railway.toml` | Railway deployment configuration |
| `netlify.toml` | Netlify build and redirect configuration |

**Key fixes:**
- Added healthcheck timeout and restart policy for Railway
- Fixed SPA redirect rules for Netlify
- Added security headers
- Added WebSocket support

### Docker Configuration

| File | Purpose |
|------|---------|
| `backend/Dockerfile` | Multi-stage production build |
| `frontend/Dockerfile` | Production nginx build |
| `frontend/Dockerfile.dev` | Development server |
| `docker-compose.yml` | Local development stack |

**Key features:**
- Multi-stage builds for optimization
- Non-root user for security
- Health checks configured
- MongoDB and Redis services included

### Deployment Scripts

| File | Purpose |
|------|---------|
| `deployment/scripts/full-deploy.sh` | Deploy both backend and frontend |
| `deployment/scripts/deploy-railway.sh` | Deploy backend to Railway |
| `deployment/scripts/deploy-netlify.sh` | Deploy frontend to Netlify |
| `deployment/scripts/quick-test.sh` | Quick local test build |
| `deployment/scripts/setup-env.sh` | Environment setup helper |

### Environment Templates

| File | Purpose |
|------|---------|
| `backend/.env.example` | Backend environment variables |
| `frontend/.env.example` | Frontend environment variables |
| `.env.example` | Root environment template |

## Deployment Methods

### 1. Automatic (Git Push)

Push to `main` or `master` branch:
```bash
git push origin main
```

GitHub Actions will:
1. Run backend and frontend tests
2. Deploy backend to Railway
3. Deploy frontend to Netlify
4. Run health checks
5. Post deployment summary

### 2. Manual Scripts

Deploy everything:
```bash
./deployment/scripts/full-deploy.sh
```

Deploy backend only:
```bash
./deployment/scripts/deploy-railway.sh
```

Deploy frontend only:
```bash
./deployment/scripts/deploy-netlify.sh --prod
```

### 3. Docker (Local Development)

Start all services:
```bash
docker compose up -d
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- MongoDB: localhost:27017
- Redis: localhost:6379

## Required GitHub Secrets

Add these in GitHub Repo → Settings → Secrets → Actions:

| Secret | Description |
|--------|-------------|
| `RAILWAY_TOKEN` | Railway API token |
| `NETLIFY_AUTH_TOKEN` | Netlify personal access token |
| `NETLIFY_SITE_ID` | Netlify site ID |
| `VITE_API_URL` | Production backend URL |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase public API key |

## Required Environment Variables

### Railway (Backend)

```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/ihhashi
SECRET_KEY=your-32-char-minimum-secret-key
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://your-site.netlify.app
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
```

### Netlify (Frontend)

```env
VITE_API_URL=https://your-app.up.railway.app
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-key
```

## Health Endpoints

- Backend: `GET /health` → Returns database and Redis status
- Frontend: `GET /health` → Returns "healthy" (nginx)

## Troubleshooting

### 502 Bad Gateway on Railway
1. Check `/health` endpoint
2. Verify `PORT` env var is not hardcoded
3. Check Railway logs: `railway logs`

### CORS Errors
1. Update `CORS_ORIGINS` in Railway with Netlify URL
2. Include `https://` prefix
3. No trailing slash

### Build Failures
1. Check Node.js version (v20 recommended)
2. Clear cache: `rm -rf node_modules dist`
3. Reinstall: `npm ci --legacy-peer-deps`

## Verification

Verify all configurations:
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"
python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"

# Check shell scripts
bash -n deployment/scripts/*.sh

# Test local build
docker compose build
```

## Next Steps

1. Set up GitHub secrets
2. Configure Railway environment variables
3. Configure Netlify environment variables
4. Push to main branch to trigger deployment
5. Verify health endpoints
6. Test the deployed application
