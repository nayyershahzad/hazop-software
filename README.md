# HAZOPCloud - AI-Powered HAZOP Analysis Software

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18+-61DAFB.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)

> Streamline HAZOP studies with AI-powered cause-consequence analysis, P&ID integration, and collaborative risk assessment.

**Website**: [hazopcloud.com](https://hazopcloud.com)
**Documentation**: [docs.hazopcloud.com](https://docs.hazopcloud.com)
**Blog**: [LinkedIn Article](https://www.linkedin.com/pulse/ai-powered-hazop-software-nayyer-shahzad-kesvf/)

## Features

- **AI-Powered Suggestions** - Gemini AI suggests causes, consequences, and safeguards
- **Risk Matrix** - Built-in 5x5 risk assessment with customizable scales
- **P&ID Integration** - Upload and annotate process diagrams
- **Multi-Tenant** - Organization-based data isolation with role-based access
- **Export** - Generate professional HAZOP reports in PDF/Excel

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Python 3.11, SQLAlchemy |
| Frontend | React 18, TypeScript, Tailwind CSS |
| Database | PostgreSQL 14+ |
| AI | Google Gemini API |
| Auth | JWT |

## Quick Start

See [QUICK_START.md](QUICK_START.md) for local development setup.

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

## Deployment

### Fly.io (Backend)
See `fly.toml` and `Dockerfile.fly` for backend deployment configuration.

### Vercel (Frontend)
See `frontend/vercel.json` for frontend deployment configuration.

### GitHub Pages (Landing Page)
See `landing-page/` directory for the marketing landing page.

## API Documentation

Once deployed, visit:
- **Swagger UI**: `https://hazop-backend.fly.dev/docs`
- **ReDoc**: `https://hazop-backend.fly.dev/redoc`

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

## Contact

Built by **Nayyer Shahzad** - Process Safety Engineer & AI/ML Specialist

- LinkedIn: [@nayyershahzad](https://www.linkedin.com/in/nayyershahzad/)
- Email: nayyer.shahzad@outlook.com

## License

Proprietary - All Rights Reserved

---

**Version**: 2.0.0
**Last Updated**: January 2025
