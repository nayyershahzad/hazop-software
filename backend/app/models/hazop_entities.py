from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Cause(Base):
    __tablename__ = "causes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"))
    cause_description = Column(Text, nullable=False)
    likelihood = Column(String(50))  # 'rare', 'unlikely', 'possible', 'likely', 'almost_certain'
    ai_suggested = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Consequence(Base):
    __tablename__ = "consequences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"))
    cause_id = Column(UUID(as_uuid=True), ForeignKey("causes.id", ondelete="CASCADE"), nullable=True)  # New: Link to specific cause
    consequence_description = Column(Text, nullable=False)
    severity = Column(String(50))  # 'negligible', 'minor', 'moderate', 'major', 'catastrophic'
    category = Column(String(100))  # 'safety', 'environmental', 'operational', 'financial'
    ai_suggested = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Safeguard(Base):
    __tablename__ = "safeguards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"))
    consequence_id = Column(UUID(as_uuid=True), ForeignKey("consequences.id", ondelete="CASCADE"), nullable=True)  # New: Link to specific consequence
    safeguard_description = Column(Text, nullable=False)
    safeguard_type = Column(String(100))  # 'prevention', 'detection', 'mitigation'
    effectiveness = Column(String(50))  # 'low', 'medium', 'high'
    ai_suggested = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"))
    initial_likelihood = Column(String(50))
    initial_severity = Column(String(50))
    initial_risk_level = Column(String(50))  # 'low', 'medium', 'high', 'critical'
    residual_likelihood = Column(String(50))
    residual_severity = Column(String(50))
    residual_risk_level = Column(String(50))
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assessed_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"))
    consequence_id = Column(UUID(as_uuid=True), ForeignKey("consequences.id", ondelete="CASCADE"), nullable=True)  # New: Link to specific consequence
    recommendation_description = Column(Text, nullable=False)
    priority = Column(String(50))  # 'low', 'medium', 'high', 'critical'
    responsible_party = Column(String(255))
    target_date = Column(Date)
    status = Column(String(50), default='open')  # 'open', 'in_progress', 'completed', 'closed'
    ai_suggested = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
