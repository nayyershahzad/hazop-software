from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
import uuid
from app.database import Base

class GeminiCache(Base):
    """
    Database model for caching Gemini AI API responses.
    This caching system aims to reduce costs by approximately 70% by storing
    responses for similar queries (same deviation, context, and suggestion type).
    """
    __tablename__ = "gemini_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(64), unique=True, nullable=False, index=True)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"), nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # 'causes', 'consequences', 'safeguards', etc.
    context_hash = Column(String(32), nullable=False)
    response_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)

    # Additional tracking fields for optimization
    access_count = Column(Integer, default=1, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def is_expired(self):
        """Check if cache entry is expired"""
        return datetime.utcnow() > self.expires_at

    def update_access_stats(self):
        """Update access statistics for this cache entry"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()