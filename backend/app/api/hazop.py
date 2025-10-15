from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from app.database import get_db
from app.models.hazop_entities import Cause, Consequence, Safeguard, RiskAssessment, Recommendation
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/hazop", tags=["hazop"])

# ============ Causes ============
class CreateCauseRequest(BaseModel):
    deviation_id: UUID
    cause_description: str
    likelihood: Optional[str] = None

class CauseResponse(BaseModel):
    id: UUID
    deviation_id: UUID
    cause_description: str
    likelihood: Optional[str]
    ai_suggested: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/causes", response_model=CauseResponse)
def create_cause(
    req: CreateCauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cause = Cause(
        deviation_id=req.deviation_id,
        cause_description=req.cause_description,
        likelihood=req.likelihood,
        created_by=current_user.id
    )
    db.add(cause)
    db.commit()
    db.refresh(cause)
    return cause

@router.get("/deviations/{deviation_id}/causes", response_model=List[CauseResponse])
def list_causes(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    causes = db.query(Cause).filter(Cause.deviation_id == deviation_id).all()
    return causes

@router.put("/causes/{cause_id}", response_model=CauseResponse)
def update_cause(
    cause_id: UUID,
    req: CreateCauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cause = db.query(Cause).filter(Cause.id == cause_id).first()
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")

    cause.cause_description = req.cause_description
    cause.likelihood = req.likelihood
    db.commit()
    db.refresh(cause)
    return cause

@router.delete("/causes/{cause_id}")
def delete_cause(
    cause_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cause = db.query(Cause).filter(Cause.id == cause_id).first()
    if not cause:
        raise HTTPException(status_code=404, detail="Cause not found")
    db.delete(cause)
    db.commit()
    return {"message": "Cause deleted"}

# ============ Consequences ============
class CreateConsequenceRequest(BaseModel):
    deviation_id: UUID
    cause_id: Optional[UUID] = None  # New: Link to specific cause
    consequence_description: str
    severity: Optional[str] = None
    category: Optional[str] = None

class ConsequenceResponse(BaseModel):
    id: UUID
    deviation_id: UUID
    cause_id: Optional[UUID]  # New: Link to specific cause
    consequence_description: str
    severity: Optional[str]
    category: Optional[str]
    ai_suggested: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/consequences", response_model=ConsequenceResponse)
def create_consequence(
    req: CreateConsequenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    consequence = Consequence(
        deviation_id=req.deviation_id,
        cause_id=req.cause_id,  # New: Link to specific cause
        consequence_description=req.consequence_description,
        severity=req.severity,
        category=req.category,
        created_by=current_user.id
    )
    db.add(consequence)
    db.commit()
    db.refresh(consequence)
    return consequence

@router.get("/deviations/{deviation_id}/consequences", response_model=List[ConsequenceResponse])
def list_consequences(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    consequences = db.query(Consequence).filter(Consequence.deviation_id == deviation_id).all()
    return consequences

@router.get("/causes/{cause_id}/consequences", response_model=List[ConsequenceResponse])
def list_consequences_for_cause(
    cause_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all consequences for a specific cause"""
    consequences = db.query(Consequence).filter(Consequence.cause_id == cause_id).all()
    return consequences

@router.put("/consequences/{consequence_id}", response_model=ConsequenceResponse)
def update_consequence(
    consequence_id: UUID,
    req: CreateConsequenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    consequence = db.query(Consequence).filter(Consequence.id == consequence_id).first()
    if not consequence:
        raise HTTPException(status_code=404, detail="Consequence not found")

    consequence.consequence_description = req.consequence_description
    consequence.severity = req.severity
    consequence.category = req.category
    consequence.cause_id = req.cause_id
    db.commit()
    db.refresh(consequence)
    return consequence

@router.delete("/consequences/{consequence_id}")
def delete_consequence(
    consequence_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    consequence = db.query(Consequence).filter(Consequence.id == consequence_id).first()
    if not consequence:
        raise HTTPException(status_code=404, detail="Consequence not found")

    # Manually delete any associated impact assessments first
    from app.models import ImpactAssessment
    impact_assessment = db.query(ImpactAssessment).filter(
        ImpactAssessment.consequence_id == consequence_id
    ).first()

    if impact_assessment:
        db.delete(impact_assessment)

    # Now delete the consequence
    db.delete(consequence)
    db.commit()
    return {"message": "Consequence deleted"}

# ============ Safeguards ============
class CreateSafeguardRequest(BaseModel):
    deviation_id: UUID
    consequence_id: Optional[UUID] = None  # New: Link to specific consequence
    safeguard_description: str
    safeguard_type: Optional[str] = None
    effectiveness: Optional[str] = None

class SafeguardResponse(BaseModel):
    id: UUID
    deviation_id: UUID
    consequence_id: Optional[UUID]  # New: Link to specific consequence
    safeguard_description: str
    safeguard_type: Optional[str]
    effectiveness: Optional[str]
    ai_suggested: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/safeguards", response_model=SafeguardResponse)
def create_safeguard(
    req: CreateSafeguardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    safeguard = Safeguard(
        deviation_id=req.deviation_id,
        consequence_id=req.consequence_id,  # New: Link to specific consequence
        safeguard_description=req.safeguard_description,
        safeguard_type=req.safeguard_type,
        effectiveness=req.effectiveness,
        created_by=current_user.id
    )
    db.add(safeguard)
    db.commit()
    db.refresh(safeguard)
    return safeguard

@router.get("/deviations/{deviation_id}/safeguards", response_model=List[SafeguardResponse])
def list_safeguards(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    safeguards = db.query(Safeguard).filter(Safeguard.deviation_id == deviation_id).all()
    return safeguards

@router.get("/consequences/{consequence_id}/safeguards", response_model=List[SafeguardResponse])
def list_safeguards_for_consequence(
    consequence_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all safeguards for a specific consequence"""
    safeguards = db.query(Safeguard).filter(Safeguard.consequence_id == consequence_id).all()
    return safeguards

@router.put("/safeguards/{safeguard_id}", response_model=SafeguardResponse)
def update_safeguard(
    safeguard_id: UUID,
    req: CreateSafeguardRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    safeguard = db.query(Safeguard).filter(Safeguard.id == safeguard_id).first()
    if not safeguard:
        raise HTTPException(status_code=404, detail="Safeguard not found")

    safeguard.safeguard_description = req.safeguard_description
    safeguard.safeguard_type = req.safeguard_type
    safeguard.effectiveness = req.effectiveness
    safeguard.consequence_id = req.consequence_id
    db.commit()
    db.refresh(safeguard)
    return safeguard

@router.delete("/safeguards/{safeguard_id}")
def delete_safeguard(
    safeguard_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    safeguard = db.query(Safeguard).filter(Safeguard.id == safeguard_id).first()
    if not safeguard:
        raise HTTPException(status_code=404, detail="Safeguard not found")
    db.delete(safeguard)
    db.commit()
    return {"message": "Safeguard deleted"}

# ============ Recommendations ============
class CreateRecommendationRequest(BaseModel):
    deviation_id: UUID
    consequence_id: Optional[UUID] = None  # New: Link to specific consequence
    recommendation_description: str
    priority: Optional[str] = None
    responsible_party: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = 'open'
    due_date: Optional[date] = None

class RecommendationResponse(BaseModel):
    id: UUID
    deviation_id: UUID
    consequence_id: Optional[UUID]  # New: Link to specific consequence
    recommendation_description: str
    priority: Optional[str]
    responsible_party: Optional[str]
    target_date: Optional[date]
    status: str
    ai_suggested: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/recommendations", response_model=RecommendationResponse)
def create_recommendation(
    req: CreateRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = Recommendation(
        deviation_id=req.deviation_id,
        consequence_id=req.consequence_id,  # New: Link to specific consequence
        recommendation_description=req.recommendation_description,
        priority=req.priority,
        responsible_party=req.responsible_party,
        target_date=req.target_date,
        created_by=current_user.id
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation

@router.get("/deviations/{deviation_id}/recommendations", response_model=List[RecommendationResponse])
def list_recommendations(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendations = db.query(Recommendation).filter(Recommendation.deviation_id == deviation_id).all()
    return recommendations

@router.get("/consequences/{consequence_id}/recommendations", response_model=List[RecommendationResponse])
def list_recommendations_for_consequence(
    consequence_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recommendations for a specific consequence"""
    recommendations = db.query(Recommendation).filter(Recommendation.consequence_id == consequence_id).all()
    return recommendations

@router.put("/recommendations/{recommendation_id}", response_model=RecommendationResponse)
def update_recommendation(
    recommendation_id: UUID,
    req: CreateRecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    recommendation.recommendation_description = req.recommendation_description
    recommendation.priority = req.priority
    recommendation.status = req.status
    # Handle both due_date (from frontend) and target_date (from model)
    recommendation.due_date = req.due_date or req.target_date
    recommendation.consequence_id = req.consequence_id
    db.commit()
    db.refresh(recommendation)
    return recommendation

@router.delete("/recommendations/{recommendation_id}")
def delete_recommendation(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    db.delete(recommendation)
    db.commit()
    return {"message": "Recommendation deleted"}

@router.patch("/recommendations/{recommendation_id}/status")
def update_recommendation_status(
    recommendation_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    recommendation.status = status
    db.commit()
    return {"message": "Status updated"}
