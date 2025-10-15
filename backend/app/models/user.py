from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="analyst")  # System role: analyst, admin, etc.

    # Multi-tenancy fields
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    org_role = Column(String(50), default="member")  # Organization role: owner, admin, member, viewer

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")

    def __repr__(self):
        return f"<User {self.email} (Org: {self.organization_id})>"

    def to_dict(self):
        """Convert user to dictionary for API responses (exclude sensitive data)"""
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "org_role": self.org_role,
            "organization_id": str(self.organization_id),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
