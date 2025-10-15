from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class PIDDocument(Base):
    __tablename__ = "pid_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(UUID(as_uuid=True), ForeignKey("hazop_studies.id", ondelete="CASCADE"))
    node_id = Column(UUID(as_uuid=True), ForeignKey("hazop_nodes.id", ondelete="CASCADE"))  # Node-specific P&ID
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    total_pages = Column(Integer)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    node_locations = relationship("NodePIDLocation", back_populates="pid_document", cascade="all, delete-orphan")

class NodePIDLocation(Base):
    __tablename__ = "node_pid_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(UUID(as_uuid=True), ForeignKey("hazop_nodes.id", ondelete="CASCADE"))
    pid_document_id = Column(UUID(as_uuid=True), ForeignKey("pid_documents.id", ondelete="CASCADE"))
    page_number = Column(Integer, nullable=False)
    x_coordinate = Column(Float, nullable=False)  # Percentage (0-100)
    y_coordinate = Column(Float, nullable=False)  # Percentage (0-100)
    width = Column(Float, default=10.0)  # Width as percentage
    height = Column(Float, default=5.0)  # Height as percentage
    color = Column(String(20), default='#FFFF00')  # Hex color code (default: yellow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    pid_document = relationship("PIDDocument", back_populates="node_locations")
