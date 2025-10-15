# HAZOP Management System - MVP

Modern web-based HAZOP (Hazard and Operability Study) management system with AI integration.

## 🚀 Features (MVP)

- ✅ User authentication (register/login with JWT)
- ✅ Create and manage HAZOP studies
- ✅ Add nodes to studies
- ✅ Create deviations with parameters and guide words
- ✅ Clean, modern UI with Tailwind CSS
- ✅ REST API with FastAPI
- ✅ PostgreSQL database
- ✅ Docker support for easy deployment

## 📋 Prerequisites

- Docker and Docker Compose (recommended)
- OR manually:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - Redis 7+

## 🐳 Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   cd HAZOP-Software
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env and set JWT_SECRET to a random string
   ```

3. **Start all services**
   ```bash
   docker-compose up
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 💻 Manual Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit environment file
cp .env.example .env

# Start the server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

Make sure PostgreSQL is running with a database named `hazop_db`.

## 📖 Usage

1. **Register a new account** at http://localhost:5173/login
2. **Create a HAZOP study** from the Studies page
3. **Add nodes** to your study
4. **Add deviations** to each node with parameters and guide words

## 🏗️ Architecture

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **PostgreSQL** - Relational database
- **JWT** - Authentication
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **React Router** - Navigation

## 📁 Project Structure

```
HAZOP-Software/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Security & config
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── store/          # Zustand stores
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Studies
- `GET /api/studies` - List all studies
- `POST /api/studies` - Create study
- `GET /api/studies/{id}` - Get study details

### Nodes
- `GET /api/studies/{id}/nodes` - List nodes
- `POST /api/studies/{id}/nodes` - Create node

### Deviations
- `GET /api/studies/nodes/{id}/deviations` - List deviations
- `POST /api/studies/nodes/{id}/deviations` - Create deviation

## 🚀 Next Steps (Full Phase)

After testing the MVP, we'll add:
- P&ID PDF upload and viewing
- Causes, Consequences, Safeguards
- Risk assessment
- AI-powered suggestions (Google Gemini)
- Superior copy/paste functionality
- Intelligent auto-complete
- Real-time collaboration
- Export to Word/Excel
- MCP server integration

## 📝 Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens (change in production!)
- `GEMINI_API_KEY` - Optional for AI features

## 🐛 Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env

**Frontend can't connect to backend:**
- Ensure backend is running on port 8000
- Check VITE_API_URL in frontend/.env

**Docker issues:**
- Try `docker-compose down -v` to reset
- Ensure ports 5173, 8000, 5432 are free

## 📄 License

MIT License - See LICENSE file for details
