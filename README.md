# HAZOP Analysis System - SaaS Platform

Professional HAZOP (Hazard and Operability) study management system with AI-powered suggestions and multi-tenant architecture.

## Features

- **Multi-Tenant Architecture**: Complete data isolation between organizations
- **AI-Powered Analysis**: Google Gemini AI integration for intelligent suggestions  
- **Comprehensive HAZOP Workflow**: Studies, Nodes, Deviations, Causes, Consequences, Safeguards, Recommendations
- **Risk Assessment**: Built-in risk matrix and impact assessment
- **P&ID Integration**: Upload and annotate P&ID diagrams
- **Modern UI**: React + TypeScript frontend with Tailwind CSS
- **Secure Authentication**: JWT-based auth with password validation
- **RESTful API**: FastAPI backend with automatic OpenAPI docs

## Tech Stack

**Backend:**
- FastAPI (Python)
- PostgreSQL  
- SQLAlchemy ORM
- JWT Authentication
- Google Generative AI (Gemini)

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Zustand (State Management)
- Axios

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
psql -U postgres -c "CREATE DATABASE hazop_db;"
psql -U hazop_user -d hazop_db -f migrations/006_add_multi_tenancy.sql

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173

## Deployment to Render.com

See [RENDER_DEPLOY.md](RENDER_DEPLOY.md) for detailed deployment instructions.

### Quick Deploy

```bash
git init
git add .
git commit -m "Initial commit: HAZOP SaaS MVP"
git branch -M main
git remote add origin https://github.com/nayyershahzad/hazop-software.git
git push -u origin main
```

Then deploy via Render Dashboard using the `render.yaml` blueprint.

## API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-backend.onrender.com/docs`
- **ReDoc**: `https://your-backend.onrender.com/redoc`

## Multi-Tenancy & Data Isolation

All data is isolated by `organization_id`:

- Users belong to ONE organization
- Studies are scoped to organizations
- API endpoints automatically filter by organization
- JWT tokens include organization context

## User Roles

- **Owner**: Full access (first user who creates the organization)
- **Admin**: Manage users and studies
- **Member**: Create and edit studies
- **Viewer**: Read-only access

## Security

- Password requirements: Min 8 chars, 1 uppercase, 1 lowercase, 1 number
- JWT token expiration: 24 hours
- HTTPS enforced in production
- Organization-level data isolation
- SQL injection protection via SQLAlchemy ORM

## License

Proprietary - All Rights Reserved

## Support

For issues or questions, contact: support@hazopsystem.com

---

**Version**: 2.0.0-mvp
**Last Updated**: October 15, 2025
