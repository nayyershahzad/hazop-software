"""
Risk Assessment and Impact Assessment models for HAZOP analysis.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class ImpactAssessment(Base):
    """
    Detailed impact assessment across multiple categories with risk matrix calculation.
    Based on industry-standard 5x5 risk matrix.
    Now linked to consequences instead of deviations.
    """
    __tablename__ = "impact_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deviation_id = Column(UUID(as_uuid=True), ForeignKey("deviations.id", ondelete="CASCADE"))  # Keep for backward compatibility
    consequence_id = Column(UUID(as_uuid=True), ForeignKey("consequences.id", ondelete="CASCADE"), unique=True, nullable=True)  # New: Link to specific consequence

    # Impact Ratings (1-5 scale for each category)
    # 1 = Minor/Negligible, 2 = Limited, 3 = Moderate, 4 = Significant, 5 = Major/Critical
    safety_impact = Column(Integer, nullable=False, default=1)            # Health & Safety impact
    financial_impact = Column(Integer, nullable=False, default=1)         # Financial/Economic impact
    environmental_impact = Column(Integer, nullable=False, default=1)     # Environmental impact
    reputation_impact = Column(Integer, nullable=False, default=1)        # Reputation/PR impact
    schedule_impact = Column(Integer, nullable=False, default=1)          # Schedule/Timeline impact
    performance_impact = Column(Integer, nullable=False, default=1)       # Operational Performance impact

    # Likelihood Rating (1-5 scale)
    # 1 = Very Unlikely, 2 = Unlikely, 3 = Possible, 4 = Highly Likely, 5 = Probable
    likelihood = Column(Integer, nullable=False, default=1)

    # Calculated Risk Metrics
    max_impact = Column(Integer, nullable=False, default=1)               # Maximum of all impact ratings
    risk_score = Column(Integer, nullable=False, default=1)               # likelihood × max_impact (1-25)
    risk_level = Column(String(20), nullable=False, default='Low')        # Low, Medium, High, Critical
    risk_color = Column(String(20), nullable=False, default='green')      # green, yellow, orange, red

    # Metadata
    assessed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assessed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Notes and justifications
    assessment_notes = Column(String(1000))                               # Optional notes/justification

    @staticmethod
    def calculate_risk_metrics(safety: int, financial: int, environmental: int,
                              reputation: int, schedule: int, performance: int,
                              likelihood: int) -> dict:
        """
        Calculate risk score, level, and color based on impact ratings and likelihood.

        Risk Matrix (5×5):
        - Low (Green): 1-7
        - Medium (Yellow): 8-16
        - High (Orange): 17-20
        - Critical (Red): 21-25
        """
        # Calculate maximum impact across all categories
        max_impact = max(safety, financial, environmental, reputation, schedule, performance)

        # Calculate risk score (likelihood × max_impact)
        risk_score = likelihood * max_impact

        # Determine risk level and color based on score
        if risk_score <= 7:
            risk_level = "Low"
            risk_color = "green"
        elif risk_score <= 16:
            risk_level = "Medium"
            risk_color = "yellow"
        elif risk_score <= 20:
            risk_level = "High"
            risk_color = "orange"
        else:  # 21-25
            risk_level = "Critical"
            risk_color = "red"

        return {
            "max_impact": max_impact,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_color": risk_color
        }


# Impact Level Descriptions (for reference in API/UI)
IMPACT_DESCRIPTIONS = {
    "safety": {
        1: "Minor: First aid treatment only",
        2: "Limited: Medical treatment required",
        3: "Moderate: Single or multiple lost time injuries",
        4: "Significant: Permanent disablement",
        5: "Major/Critical: Single or multiple fatalities"
    },
    "financial": {
        1: "Minor: <$10K",
        2: "Limited: $10K-$100K",
        3: "Moderate: $100K-$1M",
        4: "Significant: $1M-$10M",
        5: "Major: >$10M"
    },
    "environmental": {
        1: "Minor: Contained spill, no environmental impact",
        2: "Limited: Minor spill/incident affecting immediate area",
        3: "Moderate: Localized environmental impact",
        4: "Significant: Substantial environmental impact",
        5: "Major/Critical: Major environmental catastrophe"
    },
    "reputation": {
        1: "Minor: Local awareness, limited concern",
        2: "Limited: Regional awareness, some stakeholder concern",
        3: "Moderate: National awareness, significant stakeholder concern",
        4: "Significant: International awareness, major reputational damage",
        5: "Major/Critical: Severe long-term reputational damage"
    },
    "schedule": {
        1: "Minor: <1 day delay",
        2: "Limited: 1-7 days delay",
        3: "Moderate: 1-4 weeks delay",
        4: "Significant: 1-3 months delay",
        5: "Major: >3 months delay"
    },
    "performance": {
        1: "Minor: <5% degradation",
        2: "Limited: 5-15% degradation",
        3: "Moderate: 15-30% degradation",
        4: "Significant: 30-50% degradation",
        5: "Major: >50% degradation or shutdown"
    }
}

LIKELIHOOD_DESCRIPTIONS = {
    1: "Very Unlikely: Has not occurred in similar operations",
    2: "Unlikely: Has occurred in similar operations",
    3: "Possible: Has occurred in this operation",
    4: "Highly Likely: Occurs several times per year in this operation",
    5: "Probable: Occurs frequently in this operation"
}
