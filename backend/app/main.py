from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from app.database import init_db, get_db
from app.api import auth, studies, hazop, pid, impact_assessment, gemini
from app.services.gemini_service import schedule_cache_cleanup
from app.middleware.compression import CompressionMiddleware
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="HAZOP Management System",
    description="AI-powered HAZOP study management system with multi-tenant support",
    version="2.0.0-mvp",
    # Use faster JSON library for better performance
    default_response_class=ORJSONResponse,
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

# Add performance middleware for better caching
app.add_middleware(CompressionMiddleware)

# Add FastAPI's built-in GZip middleware
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500)

# Include routers
app.include_router(auth.router)
app.include_router(studies.router)
app.include_router(hazop.router)
app.include_router(pid.router)
app.include_router(impact_assessment.router, prefix="/api", tags=["Impact Assessment"])
app.include_router(gemini.router)

@app.on_event("startup")
def startup_event():
    """Initialize database and services on startup"""
    # Initialize database
    init_db()

    # Schedule Gemini API cache cleanup
    try:
        schedule_cache_cleanup(get_db)
        logging.info("Gemini API cache cleanup scheduler started")
    except Exception as e:
        logging.error(f"Failed to start cache cleanup scheduler: {e}", exc_info=True)

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
