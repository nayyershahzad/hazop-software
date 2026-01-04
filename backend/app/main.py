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
origins = []

# Production origins for Fly.io/Vercel deployment
PRODUCTION_ORIGINS = [
    "https://hazop-frontend.vercel.app",
    "https://hazopcloud.com",
    "https://www.hazopcloud.com",
    "https://app.hazopcloud.com",
]

if CORS_ORIGINS == "*":
    # For development or when explicitly configured to allow all origins
    origins = ["*"]
    logging.warning("CORS is configured to allow all origins (*). This is not recommended for production.")
else:
    # Parse comma-separated list of allowed origins
    origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]

    # Add production origins
    for origin in PRODUCTION_ORIGINS:
        if origin not in origins:
            origins.append(origin)

    # Add common development origins if environment is not production
    if os.getenv("ENVIRONMENT") != "production":
        dev_origins = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"]
        for origin in dev_origins:
            if origin not in origins:
                origins.append(origin)

    # Check for Render.com environment and add the frontend URL
    if os.getenv("RENDER") == "true" and os.getenv("RENDER_EXTERNAL_FRONTEND_URL"):
        render_frontend = os.getenv("RENDER_EXTERNAL_FRONTEND_URL", "").strip()
        if render_frontend and render_frontend not in origins:
            origins.append(render_frontend)
            logging.info(f"Added Render frontend URL to CORS: {render_frontend}")

    # Check for FRONTEND_URL environment variable (Fly.io)
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url and frontend_url not in origins:
        origins.append(frontend_url)
        logging.info(f"Added FRONTEND_URL to CORS: {frontend_url}")

logging.info(f"CORS origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    max_age=86400  # Cache preflight requests for 1 day
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
    return {"status": "healthy", "service": "hazop-backend", "version": "2.0.0"}
