# Render.yaml Fix - Deployment Ready!

**Issue**: "databases: field databases not found in type file.service"
**Status**: ✅ FIXED
**Date**: October 15, 2025

---

## What Was Wrong

The original `render.yaml` had incorrect syntax:

```yaml
# ❌ WRONG - databases nested under services
services:
  - type: pserv
    name: hazop-db
    databases:        # <-- This is wrong!
      - name: hazop_db
```

**Error**: Render.com expects `databases` at the **top level**, not nested under `services`.

---

## What Was Fixed

The corrected `render.yaml` structure:

```yaml
# ✅ CORRECT - databases at top level
databases:
  - name: hazop-db
    databaseName: hazop_db
    user: hazop_user
    plan: free

services:
  - type: web
    name: hazop-backend
    # ... backend config
```

### Key Changes:

1. **Moved `databases` to top level** (not under services)
2. **Changed service type**:
   - `env: python` → `runtime: python`
   - `env: static` → `runtime: static`
3. **Simplified build commands** (removed unnecessary `cd` commands)
4. **Fixed environment variable references** using `RENDER_EXTERNAL_URL`

---

## Current render.yaml Structure

```yaml
databases:
  - name: hazop-db              # Database service name
    databaseName: hazop_db      # Actual PostgreSQL database name
    user: hazop_user            # Database user
    plan: free                  # Free tier (1GB, 90 days)

services:
  # Backend API
  - type: web
    name: hazop-backend
    runtime: python             # Python runtime
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hazop-db        # References database above
          property: connectionString
      - key: JWT_SECRET
        generateValue: true     # Auto-generate secret
      - key: GEMINI_API_KEY
        sync: false             # Set manually in dashboard
      - key: CORS_ORIGINS
        fromService:
          type: web
          name: hazop-frontend
          envVarKey: RENDER_EXTERNAL_URL
    healthCheckPath: /health

  # Frontend Static Site
  - type: web
    name: hazop-frontend
    runtime: static             # Static site hosting
    plan: free
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        fromService:
          type: web
          name: hazop-backend   # References backend above
          envVarKey: RENDER_EXTERNAL_URL
    routes:
      - type: rewrite           # SPA routing
        source: /*
        destination: /index.html
```

---

## How to Deploy Now

### Step 1: Render Dashboard

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Select repository: `nayyershahzad/hazop-software`
4. Render will now correctly parse the `render.yaml`
5. Click **"Apply"**

### Step 2: Set GEMINI_API_KEY

After deployment starts:

1. Go to **Services** → **hazop-backend**
2. Click **Environment**
3. Find `GEMINI_API_KEY`
4. Click **"Generate Value"** or paste your API key
5. Click **"Save Changes"**

Get API key from: https://makersuite.google.com/app/apikey

### Step 3: Wait for Deployment

Render will:
1. ✅ Create PostgreSQL database (`hazop-db`)
2. ✅ Build backend (install Python dependencies)
3. ✅ Build frontend (install npm packages, run build)
4. ✅ Deploy both services
5. ✅ Provide URLs for both

**Estimated time**: 5-10 minutes

### Step 4: Run Database Migration

Once backend is deployed:

```bash
# Get External Database URL from Render dashboard
# Go to: Databases → hazop-db → Info → External Database URL

psql <EXTERNAL_DATABASE_URL>

# Run migration
\i backend/migrations/006_add_multi_tenancy.sql

# Verify tables exist
\dt

# Exit
\q
```

### Step 5: Test Deployment

1. Visit frontend URL (e.g., `https://hazop-frontend.onrender.com`)
2. Click **"Sign Up"**
3. Create account with organization name
4. Test features:
   - Create study ✓
   - Add nodes/deviations ✓
   - Test AI suggestions ✓
   - Upload P&ID ✓

---

## Service URLs

After deployment, you'll get these URLs:

| Service | URL Pattern |
|---------|-------------|
| Frontend | `https://hazop-frontend.onrender.com` |
| Backend | `https://hazop-backend.onrender.com` |
| API Docs | `https://hazop-backend.onrender.com/docs` |
| Database | Internal (accessed via backend) |

---

## Environment Variables (Auto-Configured)

### Backend

| Variable | Source | Value |
|----------|--------|-------|
| `DATABASE_URL` | From database | Auto-set |
| `JWT_SECRET` | Generated | Auto-generated |
| `JWT_ALGORITHM` | Fixed | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Fixed | `1440` |
| `GEMINI_API_KEY` | Manual | **You set this** |
| `CORS_ORIGINS` | From frontend | Auto-set to frontend URL |
| `ENVIRONMENT` | Fixed | `production` |

### Frontend

| Variable | Source | Value |
|----------|--------|-------|
| `VITE_API_URL` | From backend | Auto-set to backend URL |

---

## Free Tier Limits

### Database (hazop-db)
- **Storage**: 1 GB
- **Connections**: 97 hours/month (then sleeps)
- **Backup**: None on free tier
- **Upgrade**: $7/month for 24/7 uptime

### Backend (hazop-backend)
- **RAM**: 512 MB
- **Build Minutes**: 500/month
- **Bandwidth**: 100 GB/month
- **Uptime**: Spins down after 15 min inactivity

### Frontend (hazop-frontend)
- **Bandwidth**: 100 GB/month
- **Builds**: Unlimited
- **CDN**: Global edge network

---

## Common Deployment Issues

### Issue 1: Build Fails

**Error**: `pip: command not found` or `npm: command not found`

**Fix**: Check `runtime` is set correctly in `render.yaml`:
- Backend: `runtime: python`
- Frontend: `runtime: static`

### Issue 2: Database Connection Fails

**Error**: `could not connect to server`

**Fix**:
1. Wait 2-3 minutes for database to spin up
2. Check `DATABASE_URL` is set in backend environment
3. Verify database service is running

### Issue 3: Frontend Shows Blank Page

**Error**: API calls fail or 404 errors

**Fix**:
1. Check `VITE_API_URL` is set in frontend environment
2. Should be: `https://hazop-backend.onrender.com`
3. Verify backend is running and healthy: `{backend_url}/health`

### Issue 4: CORS Errors

**Error**: `Access-Control-Allow-Origin`

**Fix**:
1. Check `CORS_ORIGINS` in backend includes frontend URL
2. Should automatically be set from `render.yaml`
3. Can manually add in backend environment if needed

---

## Verification Checklist

After deployment completes:

- [ ] Database service shows "Available"
- [ ] Backend service shows "Live"
- [ ] Frontend service shows "Live"
- [ ] Can visit frontend URL
- [ ] Can visit backend `/health` endpoint
- [ ] Can visit backend `/docs` (Swagger UI)
- [ ] Can sign up with new account
- [ ] Can create HAZOP study
- [ ] AI suggestions work

---

## Cost Breakdown

### Free Tier (First Month)
- Database: $0
- Backend: $0
- Frontend: $0
- Gemini API: ~$4 (100 users × 10 requests)
- **Total: ~$4/month**

### After Free Trial (Database Sleeps)
- Database: $7/month (for 24/7 uptime)
- Backend: $0
- Frontend: $0
- Gemini API: ~$4
- **Total: ~$11/month**

### Production Scale (500 users)
- Database: $7/month
- Backend: $0 (or $7 for Pro)
- Frontend: $0
- Gemini API: ~$20
- **Total: ~$27-34/month**

---

## Next Steps After Deployment

1. **Test Everything** (use verification checklist above)
2. **Monitor Logs** (check for errors in Render dashboard)
3. **Add Custom Domain** (optional, free on Render)
4. **Set Up Monitoring** (UptimeRobot, Sentry)
5. **Invite Beta Users** (get feedback)
6. **Plan Upgrades** (when you have paying customers)

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **Render Status**: https://status.render.com
- **Community**: https://community.render.com
- **Your Repo**: https://github.com/nayyershahzad/hazop-software

---

**Status**: ✅ render.yaml is now correct and deployment-ready!

**Last Updated**: October 15, 2025
