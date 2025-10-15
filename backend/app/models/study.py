from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class HazopStudy(Base):
    __tablename__ = "hazop_studies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    facility_name = Column(String(255))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String(50), default="draft")

    # Multi-tenancy field
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nodes = relationship("HazopNode", back_populates="study", cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="studies")

class HazopNode(Base):
    __tablename__ = "hazop_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(UUID(as_uuid=True), ForeignKey("hazop_studies.id", ondelete="CASCADE"))
    node_number = Column(String(50), nullable=False)
    node_name = Column(String(255), nullable=False)
    description = Column(Text)
    design_intent = Column(Text)
    sort_order = Column(Integer)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    study = relationship("HazopStudy", back_populates="nodes")
    deviations = relationship("Deviation", back_populates="node", cascade="all, delete-orphan")

class Deviation(Base):
    __tablename__ = "deviations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("hazop_nodes.id", ondelete="CASCADE"))
    parameter = Column(String(255), nullable=False)
    guide_word = Column(String(50), nullable=False)
    deviation_description = Column(Text, nullable=False)
    sort_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    node = relationship("HazopNode", back_populates="deviations")
