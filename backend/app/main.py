from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import auth, studies, hazop, pid, impact_assessment, gemini
import os

app = FastAPI(
    title="HAZOP Management System",
    description="AI-powered HAZOP study management system with multi-tenant support",
    version="2.0.0-mvp"
)

# CORS middleware with environment-aware origins
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
origins = [origin.strip() for origin in CORS_ORIGINS.split(",")]

# Add wildcard for development (will be restricted in production)
if os.getenv("ENVIRONMENT") == "development":
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(studies.router)
app.include_router(hazop.router)
app.include_router(pid.router)
app.include_router(impact_assessment.router, prefix="/api", tags=["Impact Assessment"])
app.include_router(gemini.router)

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()

@app.get("/")
def root():
    return {
        "message": "HAZOP Management System API",
        "version": "0.1.0-mvp",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
