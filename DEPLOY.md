# iHhashi Deployment - Quick Start

## 🚀 Deploy in 3 Steps

### Step 1: Install CLIs
```bash
npm install -g @railway/cli netlify-cli
```

### Step 2: Setup Environment
```bash
./deployment/scripts/setup-env.sh
```
This will show you what environment variables you need.

### Step 3: Deploy
```bash
# Deploy everything
./deployment/scripts/deploy-all.sh

# Or separately:
./deployment/scripts/deploy-railway.sh   # Backend
./deployment/scripts/deploy-netlify.sh   # Frontend
```

---

## 📋 Required Environment Variables

### Backend (Railway Dashboard)
```
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/ihhashi
SECRET_KEY=(generate: openssl rand -base64 32)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key
CORS_ORIGINS=https://your-app.netlify.app
```

### Frontend (Netlify Dashboard or .env.local)
```
VITE_API_URL=https://your-app.up.railway.app
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## 🔧 Troubleshooting

### "Deployment failed"
1. Check Railway logs: `railway logs --follow`
2. Verify environment variables are set
3. Test MongoDB connection

### "CORS error"
1. Update `CORS_ORIGINS` in Railway with your Netlify URL
2. Make sure URL has `https://`

### "MongoDB connection failed"
1. Whitelist `0.0.0.0/0` in MongoDB Atlas Network Access
2. Verify connection string format

---

## 📚 Full Documentation
See `deployment/README.md` for detailed instructions.
