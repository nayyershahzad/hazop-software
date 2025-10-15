from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import auth, studies, hazop, pid, impact_assessment

app = FastAPI(
    title="HAZOP Management System",
    description="AI-powered HAZOP study management system",
    version="0.1.0-mvp"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
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
