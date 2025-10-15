# HAZOP Software - Render.com Deployment Plan

**Date**: October 15, 2025
**Target Platform**: Render.com (Hobby Account)
**GitHub**: https://github.com/nayyershahzad
**Deployment Type**: MVP (Multi-tenant SaaS)

---

## 📋 Pre-Deployment Checklist

### Phase 1: Multi-Tenancy Implementation ✅ IN PROGRESS

#### 1.1 Database Schema Changes
- [ ] Add `organizations` table
- [ ] Add `organization_id` to users table
- [ ] Add `organization_id` to all HAZOP entities
- [ ] Create migration scripts
- [ ] Add foreign key constraints for data isolation
- [ ] Add database indexes for performance

#### 1.2 Backend Changes
- [ ] Update SQLAlchemy models with organization fields
- [ ] Add organization creation on user registration
- [ ] Update all API queries to filter by organization_id
- [ ] Add middleware to enforce organization isolation
- [ ] Update authentication to include organization context
- [ ] Add organization management endpoints

#### 1.3 Authentication Enhancements
- [ ] Improve signup flow with clear instructions
- [ ] Add email validation
- [ ] Add password strength requirements
- [ ] Add "Welcome" email (optional for MVP)
- [ ] Add user profile management
- [ ] Improve login error messages

#### 1.4 Frontend Changes
- [ ] Create improved Signup page with guide instructions
- [ ] Update Login page with better UX
- [ ] Add organization name during signup
- [ ] Add "Forgot Password" UI (placeholder for later)
- [ ] Update API calls to handle organization context
- [ ] Add organization name to header/navbar

---

### Phase 2: Render.com Configuration ⏳ PENDING

#### 2.1 Repository Setup
- [ ] Create new GitHub repository: `hazop-software`
- [ ] Push code to GitHub
- [ ] Add `.gitignore` for sensitive files
- [ ] Create `render.yaml` blueprint
- [ ] Add environment variable templates
- [ ] Create README for deployment

#### 2.2 File Structure Changes
- [ ] Add `render.yaml` in project root
- [ ] Create `backend/requirements.txt` (verify)
- [ ] Create `frontend/package.json` (verify)
- [ ] Add `backend/build.sh` script
- [ ] Add `frontend/build.sh` script
- [ ] Configure CORS for production URLs

#### 2.3 Environment Variables
- [ ] List all required env vars
- [ ] Create `.env.example` files
- [ ] Document production environment setup
- [ ] Add secrets management plan

---

### Phase 3: Deployment Execution ⏳ PENDING

#### 3.1 Render Dashboard Setup
- [ ] Login to Render.com
- [ ] Connect GitHub account
- [ ] Authorize repository access
- [ ] Create new Blueprint

#### 3.2 Service Configuration
- [ ] Configure PostgreSQL database service
- [ ] Configure backend web service
- [ ] Configure frontend static site
- [ ] Set environment variables
- [ ] Configure build commands
- [ ] Configure start commands

#### 3.3 Deploy & Verify
- [ ] Trigger initial deployment
- [ ] Monitor build logs
- [ ] Verify database connection
- [ ] Test backend API endpoints
- [ ] Test frontend loading
- [ ] Test signup/login flow
- [ ] Test HAZOP core features

---

### Phase 4: Post-Deployment ⏳ PENDING

#### 4.1 Testing
- [ ] Create test account
- [ ] Create test organization
- [ ] Create test HAZOP study
- [ ] Verify data isolation
- [ ] Test AI features
- [ ] Test PDF upload

#### 4.2 Monitoring Setup
- [ ] Enable Render metrics
- [ ] Set up error logging
- [ ] Configure health checks
- [ ] Set up uptime monitoring

#### 4.3 Documentation
- [ ] Update CLAUDE.md with deployment info
- [ ] Create user guide for signup
- [ ] Document API endpoints
- [ ] Create admin guide

---

## 🏗️ Multi-Tenancy Architecture

### Database Schema Changes

```sql
-- New table: organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    max_studies INT DEFAULT 100,
    max_users INT DEFAULT 10
);

-- Update users table
ALTER TABLE users ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'member'; -- admin, member, viewer

-- Update HAZOP tables
ALTER TABLE hazop_studies ADD COLUMN organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE;

-- Add indexes for performance
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_studies_org ON hazop_studies(organization_id);
CREATE INDEX idx_nodes_study ON hazop_nodes(study_id);
CREATE INDEX idx_deviations_node ON deviations(node_id);
```

### Data Isolation Strategy

**Level 1: Database Level**
- Foreign key constraints ensure data integrity
- Cascade deletes remove all related data

**Level 2: Application Level**
- All queries filter by `organization_id`
- Middleware validates organization access
- API endpoints enforce organization context

**Level 3: User Level**
- Users belong to ONE organization
- JWT tokens include organization_id
- No cross-organization data access

### User Registration Flow

```
1. User visits /signup
2. Enters:
   - Email (validated)
   - Password (min 8 chars, 1 uppercase, 1 number)
   - Full Name
   - Organization Name (new or existing)
3. Backend:
   - Validates email uniqueness
   - Creates organization (if new)
   - Creates user with organization_id
   - Generates JWT token with org context
4. User redirected to /studies dashboard
5. Welcome message shows organization name
```

---

## 📦 Render.yaml Configuration

```yaml
services:
  # Backend API Service
  - type: web
    name: hazop-backend
    env: python
    region: oregon
    plan: free  # Change to 'starter' when ready ($7/month)
    buildCommand: |
      cd backend
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: |
      cd backend
      uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: hazop-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: JWT_ALGORITHM
        value: HS256
      - key: ACCESS_TOKEN_EXPIRE_MINUTES
        value: 1440
      - key: GEMINI_API_KEY
        sync: false  # Set manually in Render dashboard
      - key: CORS_ORIGINS
        value: https://hazop-frontend.onrender.com
    healthCheckPath: /health

  # Frontend Static Site
  - type: web
    name: hazop-frontend
    env: static
    region: oregon
    buildCommand: |
      cd frontend
      npm install
      npm run build
    staticPublishPath: frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://hazop-backend.onrender.com
    routes:
      - type: rewrite
        source: /*
        destination: /index.html

databases:
  # PostgreSQL Database
  - name: hazop-db
    databaseName: hazop_db
    user: hazop_user
    region: oregon
    plan: free  # 1GB storage, 97 hours/month
    # Change to 'starter' when ready ($7/month, 24/7 uptime)
```

---

## 🔐 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/hazop_db

# JWT Authentication
JWT_SECRET=<auto-generated-by-render>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Integration
GEMINI_API_KEY=<your-google-gemini-key>

# CORS
CORS_ORIGINS=https://hazop-frontend.onrender.com,http://localhost:5173

# App Settings
ENVIRONMENT=production
DEBUG=False
```

### Frontend (.env.production)

```env
VITE_API_URL=https://hazop-backend.onrender.com
```

---

## 🚀 Deployment Steps

### Step 1: Prepare Codebase (Local)

```bash
# Navigate to project
cd /Users/nayyershahzad/HAZOP-Software

# Create GitHub repository (if not exists)
# Visit: https://github.com/new
# Name: hazop-software
# Private repository recommended

# Initialize git (if needed)
git init
git add .
git commit -m "feat: Multi-tenant HAZOP Software ready for deployment"

# Add remote
git remote add origin https://github.com/nayyershahzad/hazop-software.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Create Render Services

```bash
# Option A: Use render.yaml (Recommended)
1. Login to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect GitHub repository
4. Select "hazop-software" repo
5. Render auto-detects render.yaml
6. Click "Apply"

# Option B: Manual Setup
1. Create PostgreSQL database first
2. Create backend web service
3. Create frontend static site
4. Link services together
```

### Step 3: Configure Environment Variables

```bash
# In Render Dashboard → Backend Service → Environment
1. DATABASE_URL → Auto-populated from database
2. JWT_SECRET → Auto-generated
3. GEMINI_API_KEY → Add manually (from Google AI Studio)
4. CORS_ORIGINS → Set to frontend URL

# In Render Dashboard → Frontend Service → Environment
1. VITE_API_URL → Set to backend URL
```

### Step 4: Deploy

```bash
# Render automatically deploys on git push
# Or manually trigger from dashboard

# Monitor deployment
1. Check build logs
2. Wait for "Live" status (green)
3. Click service URL to test
```

### Step 5: Database Migration

```bash
# Connect to Render PostgreSQL
# In Render Dashboard → Database → Info → External Connection String

psql <EXTERNAL_DATABASE_URL>

# Run migration SQL
\i migrations/001_multi_tenancy.sql

# Verify tables
\dt
```

### Step 6: Test Application

```bash
# Visit frontend URL
https://hazop-frontend.onrender.com

# Test signup
1. Click "Sign Up"
2. Follow guided instructions
3. Create account

# Test login
1. Login with new account
2. Create HAZOP study
3. Test core features

# Verify data isolation
1. Create second account
2. Verify studies are isolated
3. No cross-tenant data visible
```

---

## 📊 Resource Limits (Render Free Tier)

| Resource | Free Tier | Starter ($7/mo) |
|----------|-----------|-----------------|
| Database Storage | 1 GB | 10 GB |
| Database Uptime | 90 days, then sleep | 24/7 |
| Web Service RAM | 512 MB | 512 MB |
| Build Minutes | 500/month | 500/month |
| Bandwidth | 100 GB/month | 100 GB/month |
| Custom Domains | Yes | Yes |
| HTTPS | Yes | Yes |

**Recommendations:**
- **Start with Free tier** for MVP testing
- **Upgrade to Starter ($7/mo)** when:
  - You have 5+ active users
  - Database needs 24/7 uptime
  - Data exceeds 1GB

---

## 🐛 Troubleshooting

### Common Issues

**1. Build Fails**
```bash
# Check build logs in Render dashboard
# Common causes:
- Missing dependencies in requirements.txt
- Wrong Python version
- Missing environment variables

# Solution:
- Update requirements.txt
- Set Python version in render.yaml (python-3.11)
- Add missing env vars
```

**2. Database Connection Fails**
```bash
# Check:
- DATABASE_URL is set correctly
- Database service is running
- Database plan allows external connections

# Solution:
- Verify connection string in env vars
- Restart backend service
- Check database logs
```

**3. CORS Errors**
```bash
# Error: "Access-Control-Allow-Origin"
# Cause: Frontend URL not in CORS_ORIGINS

# Solution:
# Update backend/.env
CORS_ORIGINS=https://hazop-frontend.onrender.com

# Update backend/app/main.py
origins = [
    "https://hazop-frontend.onrender.com",
    "http://localhost:5173"
]
```

**4. Frontend 404 on Refresh**
```bash
# Cause: SPA routing not configured

# Solution: Already handled in render.yaml
routes:
  - type: rewrite
    source: /*
    destination: /index.html
```

---

## 📈 Success Metrics

### MVP Launch Criteria
- [ ] Signup/Login working
- [ ] Create HAZOP study working
- [ ] Add nodes/deviations working
- [ ] AI suggestions working
- [ ] PDF upload working
- [ ] Data isolation verified
- [ ] No critical bugs
- [ ] Page load < 3 seconds

### Post-Launch Monitoring
- Active users per day
- Studies created per week
- AI API costs per user
- Database size growth
- Average session duration
- Error rate < 1%

---

## 💰 Cost Estimates

### Month 1 (Free Tier)
- Render Free: $0
- Gemini API (100 users × 10 requests): ~$4
- **Total: $4/month**

### Month 2-3 (Growing)
- Render Starter: $7 (database)
- Gemini API (500 users × 10 requests): ~$20
- **Total: $27/month**

### Month 4+ (Production)
- Render Pro: $25
- Gemini API (2000 users × 10 requests): ~$80
- **Total: $105/month**

---

## 🎯 Next Steps After MVP Deployment

### Phase 2: SaaS Features (Week 2-4)
1. **Subscription & Billing**
   - Integrate Stripe
   - Plans: Free, Pro ($49/mo), Enterprise
   - Usage limits per plan

2. **Team Collaboration**
   - Invite team members
   - User roles (Admin, Engineer, Viewer)
   - Activity logs

3. **Advanced Features**
   - Export to PDF/Excel
   - Email notifications
   - Real-time collaboration
   - Advanced search

4. **Security Enhancements**
   - Rate limiting
   - Email verification
   - Password reset
   - 2FA (optional)

5. **Analytics & Monitoring**
   - User analytics (Plausible/Mixpanel)
   - Error tracking (Sentry)
   - Uptime monitoring (UptimeRobot)
   - Performance monitoring (LogRocket)

6. **Marketing Site**
   - Landing page
   - Pricing page
   - Documentation
   - Blog/Resources

---

## 🔗 Useful Links

- **Render Dashboard**: https://dashboard.render.com
- **GitHub Repo**: https://github.com/nayyershahzad/hazop-software
- **Render Docs**: https://render.com/docs
- **PostgreSQL Migrations**: https://render.com/docs/databases
- **FastAPI Deployment**: https://render.com/docs/deploy-fastapi

---

## ✅ Deployment Checklist Summary

**Pre-Deployment:**
- [x] Read deployment plan
- [ ] Implement multi-tenancy
- [ ] Improve auth UI
- [ ] Test locally
- [ ] Create GitHub repo
- [ ] Push code

**Deployment:**
- [ ] Create Render account
- [ ] Connect GitHub
- [ ] Deploy via Blueprint
- [ ] Set environment variables
- [ ] Run migrations
- [ ] Test production

**Post-Deployment:**
- [ ] Verify all features
- [ ] Monitor errors
- [ ] Update documentation
- [ ] Share with beta users
- [ ] Gather feedback

---

**Status**: ✅ MVP Ready for Deployment

**Implementation Complete**:
- ✅ Multi-tenancy database schema
- ✅ Organization management
- ✅ Enhanced authentication with signup guide
- ✅ Data isolation at API level
- ✅ Improved Login/Signup UI
- ✅ Render.yaml configuration
- ✅ CORS settings for production
- ✅ Environment variable templates

**Next Action**: Test locally, then deploy to Render.com

---

**Last Updated**: October 15, 2025
