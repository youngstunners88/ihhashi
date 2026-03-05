# iHhashi Auto-Deployment Setup

## ✅ What's Already Done

1. **Railway build fixed** - Updated `railway.toml` and `railway.json` to use `python3 -m pip`
2. **GitHub Actions workflow** - Created `.github/workflows/deploy.yml` for auto-deploy
3. **Code pushed** - All changes committed to `work` branch

## 🔧 What You Need To Do

### Step 1: Set GitHub Secrets (for Auto-Deploy)

Go to: https://github.com/youngstunners88/ihhashi/settings/secrets/actions

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `RAILWAY_TOKEN` | `91e3ad14-e35d-490d-9fa0-361ecc59822f` |
| `NETLIFY_AUTH_TOKEN` | `nfp_skw8CN2quLP7NcwTzmsY8QXUvP6eH3CFcd8b` |
| `NETLIFY_SITE_ID` | Get from https://app.netlify.com/ > Your Site > Settings |
| `VITE_API_URL` | Your Railway URL (e.g., `https://ihhashi-api.up.railway.app`) |
| `VITE_SUPABASE_URL` | From Supabase Dashboard |
| `VITE_SUPABASE_ANON_KEY` | From Supabase Dashboard |

### Step 2: Set Railway Environment Variables

Go to: https://railway.app/dashboard > Your Project > Variables

Add:
- `MONGODB_URL` = `mongodb+srv://teacherchris37_db_user:iHhashil!!!@cluster0.ai5z7wq.mongodb.net/ihhashi?retryWrites=true&w=majority`
- `DB_NAME` = `ihhashi`
- `SUPABASE_URL` = (from Supabase)
- `SUPABASE_ANON_KEY` = (from Supabase)
- `SUPABASE_SERVICE_ROLE_KEY` = (from Supabase)
- `SECRET_KEY` = Generate with: `openssl rand -base64 32`
- `CORS_ORIGINS` = Your Netlify frontend URL

### Step 3: Merge to Main

Once secrets are set, merge `work` branch to `main`:

```bash
git checkout main
git merge work
git push origin main
```

This will trigger the auto-deployment!

## 🚀 What Happens Next

When you push to `main` or `master`:
1. GitHub Actions runs tests
2. Backend deploys to Railway automatically
3. Frontend deploys to Netlify automatically

## 🆘 Quick Commands

Run this to set everything up automatically:

```bash
./deployment/scripts/setup-auto-deploy.sh
```

Or manually deploy now:

```bash
# Backend
cd backend && railway up

# Frontend
cd frontend && npm run build && netlify deploy --prod
```

## 📊 Monitor Deployment

- GitHub Actions: https://github.com/youngstunners88/ihhashi/actions
- Railway Dashboard: https://railway.app/dashboard
- Netlify Dashboard: https://app.netlify.com
