from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

# Configure database logger
db_logger = logging.getLogger("database")

# Import os for environment variables
import os

# Get connection pool settings from environment variables or use defaults
POOL_SIZE = int(os.environ.get("POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.environ.get("MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.environ.get("POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.environ.get("POOL_RECYCLE", "1800"))

# Add connection pooling parameters for better performance
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=POOL_SIZE,               # Maintain connection pool
    max_overflow=MAX_OVERFLOW,         # Allow overflow under heavy load
    pool_timeout=POOL_TIMEOUT,         # Wait time for connection
    pool_recycle=POOL_RECYCLE,         # Recycle connections
    pool_pre_ping=True,                # Verify connections before use
    connect_args={"connect_timeout": 10}  # Connection timeout
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    # Import all models so they are registered with Base.metadata
    from app.models import (
        Organization, User, HazopStudy, HazopNode, Deviation,
        Cause, Consequence, Safeguard, RiskAssessment, Recommendation,
        PIDDocument, NodePIDLocation, ImpactAssessment
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db_logger.info(f"Database initialized with connection pooling (pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, pool_timeout={POOL_TIMEOUT}, pool_recycle={POOL_RECYCLE})")
