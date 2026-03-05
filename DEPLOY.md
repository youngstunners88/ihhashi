# iHhashi Deployment - Quick Start

## ⚠️ Prerequisites

1. **Node.js** (v20+ installed, v22+ recommended for Capacitor)
2. **Railway CLI**: `npm install -g @railway/cli`
3. **Netlify CLI**: `npm install -g netlify-cli`
4. **MongoDB Database**: MongoDB Atlas free tier works fine

---

## 🚀 Quick Deploy (3 Steps)

### Step 1: Deploy Backend to Railway

```bash
cd /home/teacherchris37/backend

# Login and link project
railway login
railway link  # Select or create project

# Set required environment variables in Railway Dashboard:
# - MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/ihhashi
# - SECRET_KEY=$(openssl rand -base64 32)
# - SUPABASE_URL=https://your-project.supabase.co
# - SUPABASE_ANON_KEY=your-anon-key
# - CORS_ORIGINS=https://your-app.netlify.app

# Deploy
railway up

# Get your backend URL
railway domain
# Example output: ihhashi-api.up.railway.app
```

### Step 2: Create Frontend Environment File

```bash
cd /home/teacherchris37/frontend

# Create .env.local with your actual Railway URL
cat > .env.local << EOF
VITE_API_URL=https://YOUR-RAILWAY-URL.up.railway.app
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
EOF
```

**Replace `YOUR-RAILWAY-URL` with the actual domain from Step 1.**

### Step 3: Deploy Frontend to Netlify

```bash
cd /home/teacherchris37/frontend

# Install dependencies
npm ci --legacy-peer-deps

# Build
npm run build

# Login and link
netlify login
netlify link  # Select or create site

# Deploy
netlify deploy --prod --dir=dist

# Get your Netlify URL from the output
# Example: https://ihhashi-123.netlify.app
```

---

## 🔧 Post-Deployment

### 1. Update CORS Origins (Critical!)

Go to Railway Dashboard and update `CORS_ORIGINS` with your Netlify URL:

```
CORS_ORIGINS=https://ihhashi-123.netlify.app
```

Then redeploy:
```bash
cd backend && railway up
```

### 2. Test Everything

```bash
# Test backend
curl https://YOUR-RAILWAY-URL.up.railway.app/health

# Visit frontend in browser
# Check browser console for errors
```

---

## 📋 Required Environment Variables

### Backend (Railway Dashboard)

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/ihhashi` |
| `SECRET_KEY` | JWT signing key | Generate: `openssl rand -base64 32` |
| `SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon key | From Supabase dashboard |
| `CORS_ORIGINS` | Allowed frontend URLs | `https://app.netlify.app` |

### Frontend (Netlify Dashboard or .env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Railway backend URL | `https://api.up.railway.app` |
| `VITE_SUPABASE_URL` | Supabase URL | Same as backend |
| `VITE_SUPABASE_ANON_KEY` | Supabase key | Same as backend |

---

## 🛠️ Alternative: Use Deployment Scripts

If the manual steps above are too complex, try the helper scripts:

```bash
# Quick test (verifies everything builds correctly)
./deployment/scripts/quick-test.sh

# Full deployment with interactive prompts
./deployment/scripts/deploy-all.sh

# Or separately:
./deployment/scripts/deploy-railway.sh
./deployment/scripts/deploy-netlify.sh
```

---

## 🐛 Troubleshooting

### "Cannot find module"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### "CORS error" in browser
Update `CORS_ORIGINS` in Railway with your exact Netlify URL including `https://`

### "MongoDB connection failed"
1. Whitelist `0.0.0.0/0` in MongoDB Atlas Network Access
2. Verify your connection string has the correct password

### "Build fails on Railway"
Check logs: `railway logs --follow`

### "Netlify deploy fails"
Make sure you ran `npm run build` first and the `dist/` folder exists.

---

## 📚 Full Documentation

See `deployment/README.md` for more detailed instructions.
