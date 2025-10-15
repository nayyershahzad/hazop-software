from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Organization(Base):
    """
    Organization model for multi-tenancy support.
    Each organization represents a separate tenant with isolated data.
    """
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    # Subscription limits (for future SaaS features)
    max_studies = Column(Integer, default=100)
    max_users = Column(Integer, default=10)
    max_nodes_per_study = Column(Integer, default=1000)

    # Contact information
    contact_email = Column(String(255))
    contact_phone = Column(String(50))

    # Billing information (for future use)
    subscription_plan = Column(String(50), default='free')  # 'free', 'pro', 'enterprise'
    subscription_status = Column(String(50), default='active')  # 'active', 'suspended', 'cancelled'
    trial_ends_at = Column(DateTime, nullable=True)

    # Relationships
    users = relationship("User", back_populates="organization")
    studies = relationship("HazopStudy", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"

    def to_dict(self):
        """Convert organization to dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "is_active": self.is_active,
            "subscription_plan": self.subscription_plan,
            "subscription_status": self.subscription_status,
            "max_studies": self.max_studies,
            "max_users": self.max_users,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate a URL-friendly slug from organization name"""
        import re
        slug = name.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:100]  # Limit to 100 characters
