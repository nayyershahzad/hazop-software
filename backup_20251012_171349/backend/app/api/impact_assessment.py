"""
API endpoints for Impact Assessment and Risk Matrix functionality.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models import ImpactAssessment
from app.models.user import User
from app.api.deps import get_current_user
from app.models.risk_assessment import IMPACT_DESCRIPTIONS, LIKELIHOOD_DESCRIPTIONS

router = APIRouter()


# Pydantic Models
class ImpactAssessmentCreate(BaseModel):
    """Request model for creating/updating impact assessment."""
    safety_impact: int = Field(ge=1, le=5, description="Safety impact rating (1-5)")
    financial_impact: int = Field(ge=1, le=5, description="Financial impact rating (1-5)")
    environmental_impact: int = Field(ge=1, le=5, description="Environmental impact rating (1-5)")
    reputation_impact: int = Field(ge=1, le=5, description="Reputation impact rating (1-5)")
    schedule_impact: int = Field(ge=1, le=5, description="Schedule impact rating (1-5)")
    performance_impact: int = Field(ge=1, le=5, description="Performance impact rating (1-5)")
    likelihood: int = Field(ge=1, le=5, description="Likelihood rating (1-5)")
    assessment_notes: Optional[str] = None


class ImpactAssessmentResponse(BaseModel):
    """Response model for impact assessment."""
    id: UUID
    deviation_id: UUID  # Kept for backward compatibility
    consequence_id: Optional[UUID]  # New: Link to specific consequence
    safety_impact: int
    financial_impact: int
    environmental_impact: int
    reputation_impact: int
    schedule_impact: int
    performance_impact: int
    likelihood: int
    max_impact: int
    risk_score: int
    risk_level: str
    risk_color: str
    assessed_by: Optional[UUID]
    assessed_at: datetime
    updated_at: datetime
    assessment_notes: Optional[str]

    class Config:
        from_attributes = True


class RiskMatrixConfigResponse(BaseModel):
    """Risk matrix configuration and descriptions."""
    matrix_size: int = 5
    risk_levels: dict = {
        "Low": {"range": "1-7", "color": "green"},
        "Medium": {"range": "8-16", "color": "yellow"},
        "High": {"range": "17-20", "color": "orange"},
        "Critical": {"range": "21-25", "color": "red"}
    }
    impact_descriptions: dict
    likelihood_descriptions: dict


# API Endpoints

@router.post("/deviations/{deviation_id}/impact-assessment", response_model=ImpactAssessmentResponse)
def create_or_update_impact_assessment(
    deviation_id: UUID,
    assessment: ImpactAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update impact assessment for a deviation.
    Automatically calculates risk metrics based on input.
    """
    # Calculate risk metrics
    risk_metrics = ImpactAssessment.calculate_risk_metrics(
        safety=assessment.safety_impact,
        financial=assessment.financial_impact,
        environmental=assessment.environmental_impact,
        reputation=assessment.reputation_impact,
        schedule=assessment.schedule_impact,
        performance=assessment.performance_impact,
        likelihood=assessment.likelihood
    )

    # Check if assessment already exists
    existing = db.query(ImpactAssessment).filter(
        ImpactAssessment.deviation_id == deviation_id
    ).first()

    if existing:
        # Update existing assessment
        existing.safety_impact = assessment.safety_impact
        existing.financial_impact = assessment.financial_impact
        existing.environmental_impact = assessment.environmental_impact
        existing.reputation_impact = assessment.reputation_impact
        existing.schedule_impact = assessment.schedule_impact
        existing.performance_impact = assessment.performance_impact
        existing.likelihood = assessment.likelihood
        existing.max_impact = risk_metrics["max_impact"]
        existing.risk_score = risk_metrics["risk_score"]
        existing.risk_level = risk_metrics["risk_level"]
        existing.risk_color = risk_metrics["risk_color"]
        existing.assessment_notes = assessment.assessment_notes
        existing.assessed_by = current_user.id
        existing.assessed_at = datetime.utcnow()

        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new assessment
        new_assessment = ImpactAssessment(
            deviation_id=deviation_id,
            safety_impact=assessment.safety_impact,
            financial_impact=assessment.financial_impact,
            environmental_impact=assessment.environmental_impact,
            reputation_impact=assessment.reputation_impact,
            schedule_impact=assessment.schedule_impact,
            performance_impact=assessment.performance_impact,
            likelihood=assessment.likelihood,
            max_impact=risk_metrics["max_impact"],
            risk_score=risk_metrics["risk_score"],
            risk_level=risk_metrics["risk_level"],
            risk_color=risk_metrics["risk_color"],
            assessment_notes=assessment.assessment_notes,
            assessed_by=current_user.id
        )

        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)
        return new_assessment


@router.get("/deviations/{deviation_id}/impact-assessment", response_model=ImpactAssessmentResponse)
def get_impact_assessment(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get impact assessment for a specific deviation (legacy endpoint)."""
    assessment = db.query(ImpactAssessment).filter(
        ImpactAssessment.deviation_id == deviation_id
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Impact assessment not found")

    return assessment


@router.post("/consequences/{consequence_id}/impact-assessment", response_model=ImpactAssessmentResponse)
def create_or_update_impact_assessment_for_consequence(
    consequence_id: UUID,
    assessment: ImpactAssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update impact assessment for a consequence.
    Automatically calculates risk metrics based on input.
    """
    from app.models.hazop_entities import Consequence

    # Verify consequence exists
    consequence = db.query(Consequence).filter(Consequence.id == consequence_id).first()
    if not consequence:
        raise HTTPException(status_code=404, detail="Consequence not found")

    # Calculate risk metrics
    risk_metrics = ImpactAssessment.calculate_risk_metrics(
        safety=assessment.safety_impact,
        financial=assessment.financial_impact,
        environmental=assessment.environmental_impact,
        reputation=assessment.reputation_impact,
        schedule=assessment.schedule_impact,
        performance=assessment.performance_impact,
        likelihood=assessment.likelihood
    )

    # Check if assessment already exists for this consequence
    existing = db.query(ImpactAssessment).filter(
        ImpactAssessment.consequence_id == consequence_id
    ).first()

    if existing:
        # Update existing assessment
        existing.safety_impact = assessment.safety_impact
        existing.financial_impact = assessment.financial_impact
        existing.environmental_impact = assessment.environmental_impact
        existing.reputation_impact = assessment.reputation_impact
        existing.schedule_impact = assessment.schedule_impact
        existing.performance_impact = assessment.performance_impact
        existing.likelihood = assessment.likelihood
        existing.max_impact = risk_metrics["max_impact"]
        existing.risk_score = risk_metrics["risk_score"]
        existing.risk_level = risk_metrics["risk_level"]
        existing.risk_color = risk_metrics["risk_color"]
        existing.assessment_notes = assessment.assessment_notes
        existing.assessed_by = current_user.id
        existing.assessed_at = datetime.utcnow()

        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new assessment
        new_assessment = ImpactAssessment(
            deviation_id=consequence.deviation_id,  # Keep for backward compatibility
            consequence_id=consequence_id,
            safety_impact=assessment.safety_impact,
            financial_impact=assessment.financial_impact,
            environmental_impact=assessment.environmental_impact,
            reputation_impact=assessment.reputation_impact,
            schedule_impact=assessment.schedule_impact,
            performance_impact=assessment.performance_impact,
            likelihood=assessment.likelihood,
            max_impact=risk_metrics["max_impact"],
            risk_score=risk_metrics["risk_score"],
            risk_level=risk_metrics["risk_level"],
            risk_color=risk_metrics["risk_color"],
            assessment_notes=assessment.assessment_notes,
            assessed_by=current_user.id
        )

        db.add(new_assessment)
        db.commit()
        db.refresh(new_assessment)
        return new_assessment


@router.get("/consequences/{consequence_id}/impact-assessment", response_model=ImpactAssessmentResponse)
def get_impact_assessment_for_consequence(
    consequence_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get impact assessment for a specific consequence."""
    assessment = db.query(ImpactAssessment).filter(
        ImpactAssessment.consequence_id == consequence_id
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Impact assessment not found")

    return assessment


@router.delete("/deviations/{deviation_id}/impact-assessment")
def delete_impact_assessment(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete impact assessment for a deviation."""
    assessment = db.query(ImpactAssessment).filter(
        ImpactAssessment.deviation_id == deviation_id
    ).first()

    if not assessment:
        raise HTTPException(status_code=404, detail="Impact assessment not found")

    db.delete(assessment)
    db.commit()

    return {"message": "Impact assessment deleted successfully"}


@router.get("/risk-matrix/config", response_model=RiskMatrixConfigResponse)
def get_risk_matrix_config():
    """
    Get risk matrix configuration including:
    - Matrix size and risk level definitions
    - Impact descriptions for all categories
    - Likelihood descriptions
    """
    return RiskMatrixConfigResponse(
        impact_descriptions=IMPACT_DESCRIPTIONS,
        likelihood_descriptions=LIKELIHOOD_DESCRIPTIONS
    )


@router.get("/studies/{study_id}/risk-summary")
def get_study_risk_summary(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get risk summary for an entire study.
    Returns counts by risk level and high-risk items.
    """
    from app.models import Deviation, HazopNode

    # Get all deviations for this study with their impact assessments
    deviations_with_risk = db.query(Deviation, ImpactAssessment).join(
        HazopNode, Deviation.node_id == HazopNode.id
    ).outerjoin(
        ImpactAssessment, Deviation.id == ImpactAssessment.deviation_id
    ).filter(
        HazopNode.study_id == study_id
    ).all()

    # Count by risk level
    risk_counts = {
        "Low": 0,
        "Medium": 0,
        "High": 0,
        "Critical": 0,
        "Not Assessed": 0
    }

    high_risk_items = []

    for deviation, assessment in deviations_with_risk:
        if assessment:
            risk_counts[assessment.risk_level] += 1

            # Add to high-risk list if High or Critical
            if assessment.risk_level in ["High", "Critical"]:
                high_risk_items.append({
                    "deviation_id": str(deviation.id),
                    "deviation_description": deviation.deviation_description,
                    "node_number": deviation.node.node_number if deviation.node else None,
                    "risk_level": assessment.risk_level,
                    "risk_score": assessment.risk_score,
                    "risk_color": assessment.risk_color
                })
        else:
            risk_counts["Not Assessed"] += 1

    # Sort high-risk items by score (descending)
    high_risk_items.sort(key=lambda x: x["risk_score"], reverse=True)

    return {
        "study_id": str(study_id),
        "total_deviations": len(deviations_with_risk),
        "risk_counts": risk_counts,
        "high_risk_items": high_risk_items[:10],  # Top 10 highest risks
        "assessment_completion": (
            ((len(deviations_with_risk) - risk_counts["Not Assessed"]) / len(deviations_with_risk) * 100)
            if len(deviations_with_risk) > 0 else 0
        )
    }
