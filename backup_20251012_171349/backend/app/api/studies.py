from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import uuid as uuid_module
from app.database import get_db
from app.models.study import HazopStudy, HazopNode, Deviation
from app.models.hazop_entities import Cause, Consequence, Safeguard, Recommendation
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/studies", tags=["studies"])

# Schemas
class CreateStudyRequest(BaseModel):
    title: str
    description: Optional[str] = None
    facility_name: Optional[str] = None

class StudyResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    facility_name: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class CreateNodeRequest(BaseModel):
    node_number: str
    node_name: str
    description: Optional[str] = None
    design_intent: Optional[str] = None

class NodeResponse(BaseModel):
    id: UUID
    study_id: UUID
    node_number: str
    node_name: str
    description: Optional[str]
    design_intent: Optional[str]
    status: str

    class Config:
        from_attributes = True

class CreateDeviationRequest(BaseModel):
    parameter: str
    guide_word: str
    deviation_description: str

class DeviationResponse(BaseModel):
    id: UUID
    node_id: UUID
    parameter: str
    guide_word: str
    deviation_description: str

    class Config:
        from_attributes = True

# Study endpoints
@router.post("/", response_model=StudyResponse)
def create_study(
    req: CreateStudyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new HAZOP study"""
    study = HazopStudy(
        title=req.title,
        description=req.description,
        facility_name=req.facility_name,
        created_by=current_user.id
    )
    db.add(study)
    db.commit()
    db.refresh(study)
    return study

@router.get("/", response_model=List[StudyResponse])
def list_studies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all HAZOP studies"""
    studies = db.query(HazopStudy).all()
    return studies

@router.get("/{study_id}", response_model=StudyResponse)
def get_study(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific study"""
    study = db.query(HazopStudy).filter(HazopStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")
    return study

# Node endpoints
@router.post("/{study_id}/nodes", response_model=NodeResponse)
def create_node(
    study_id: UUID,
    req: CreateNodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a node to a study"""
    study = db.query(HazopStudy).filter(HazopStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    node = HazopNode(
        study_id=study_id,
        node_number=req.node_number,
        node_name=req.node_name,
        description=req.description,
        design_intent=req.design_intent
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node

@router.get("/{study_id}/nodes", response_model=List[NodeResponse])
def list_nodes(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all nodes in a study"""
    nodes = db.query(HazopNode).filter(HazopNode.study_id == study_id).all()
    return nodes

# Deviation endpoints
@router.post("/nodes/{node_id}/deviations", response_model=DeviationResponse)
def create_deviation(
    node_id: UUID,
    req: CreateDeviationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a deviation to a node"""
    node = db.query(HazopNode).filter(HazopNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    deviation = Deviation(
        node_id=node_id,
        parameter=req.parameter,
        guide_word=req.guide_word,
        deviation_description=req.deviation_description
    )
    db.add(deviation)
    db.commit()
    db.refresh(deviation)
    return deviation

@router.get("/nodes/{node_id}/deviations", response_model=List[DeviationResponse])
def list_deviations(
    node_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all deviations for a node"""
    deviations = db.query(Deviation).filter(Deviation.node_id == node_id).all()
    return deviations

@router.delete("/{study_id}")
def delete_study(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a study and all its related data"""
    study = db.query(HazopStudy).filter(HazopStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    db.delete(study)
    db.commit()
    return {"message": "Study deleted successfully"}

@router.put("/nodes/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: UUID,
    req: CreateNodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a node's information"""
    node = db.query(HazopNode).filter(HazopNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Update node fields
    node.node_number = req.node_number
    node.node_name = req.node_name
    node.description = req.description
    node.design_intent = req.design_intent

    db.commit()
    db.refresh(node)
    return node

@router.delete("/nodes/{node_id}")
def delete_node(
    node_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a node and all its deviations"""
    node = db.query(HazopNode).filter(HazopNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    db.delete(node)
    db.commit()
    return {"message": "Node deleted successfully"}

@router.delete("/deviations/{deviation_id}")
def delete_deviation(
    deviation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a deviation and all its HAZOP analysis data"""
    deviation = db.query(Deviation).filter(Deviation.id == deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    db.delete(deviation)
    db.commit()
    return {"message": "Deviation deleted successfully"}

# Duplicate/Copy endpoints
class DuplicateNodeRequest(BaseModel):
    new_node_number: str
    new_node_name: str
    include_deviations: bool = True
    include_causes: bool = True
    include_consequences: bool = True
    include_safeguards: bool = True
    include_recommendations: bool = True

@router.post("/nodes/{node_id}/duplicate", response_model=NodeResponse)
def duplicate_node(
    node_id: UUID,
    req: DuplicateNodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate a node with all its data"""
    # Get source node
    source_node = db.query(HazopNode).filter(HazopNode.id == node_id).first()
    if not source_node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Create new node
    new_node = HazopNode(
        study_id=source_node.study_id,
        node_number=req.new_node_number,
        node_name=req.new_node_name,
        description=source_node.description,
        design_intent=source_node.design_intent,
        status="pending"
    )
    db.add(new_node)
    db.flush()

    # Copy deviations if requested
    if req.include_deviations:
        source_deviations = db.query(Deviation).filter(
            Deviation.node_id == node_id
        ).all()

        for src_dev in source_deviations:
            new_dev = Deviation(
                node_id=new_node.id,
                parameter=src_dev.parameter,
                guide_word=src_dev.guide_word,
                deviation_description=src_dev.deviation_description
            )
            db.add(new_dev)
            db.flush()

            # Copy causes
            if req.include_causes:
                src_causes = db.query(Cause).filter(
                    Cause.deviation_id == src_dev.id
                ).all()
                for src_cause in src_causes:
                    new_cause = Cause(
                        deviation_id=new_dev.id,
                        cause_description=src_cause.cause_description,
                        likelihood=src_cause.likelihood,
                        created_by=current_user.id
                    )
                    db.add(new_cause)

            # Copy consequences
            if req.include_consequences:
                src_consequences = db.query(Consequence).filter(
                    Consequence.deviation_id == src_dev.id
                ).all()
                for src_cons in src_consequences:
                    new_cons = Consequence(
                        deviation_id=new_dev.id,
                        consequence_description=src_cons.consequence_description,
                        severity=src_cons.severity,
                        category=src_cons.category,
                        created_by=current_user.id
                    )
                    db.add(new_cons)

            # Copy safeguards
            if req.include_safeguards:
                src_safeguards = db.query(Safeguard).filter(
                    Safeguard.deviation_id == src_dev.id
                ).all()
                for src_safe in src_safeguards:
                    new_safe = Safeguard(
                        deviation_id=new_dev.id,
                        safeguard_description=src_safe.safeguard_description,
                        safeguard_type=src_safe.safeguard_type,
                        effectiveness=src_safe.effectiveness,
                        created_by=current_user.id
                    )
                    db.add(new_safe)

            # Copy recommendations
            if req.include_recommendations:
                src_recs = db.query(Recommendation).filter(
                    Recommendation.deviation_id == src_dev.id
                ).all()
                for src_rec in src_recs:
                    new_rec = Recommendation(
                        deviation_id=new_dev.id,
                        recommendation_description=src_rec.recommendation_description,
                        priority=src_rec.priority,
                        responsible_party=src_rec.responsible_party,
                        target_date=src_rec.target_date,
                        status="open",
                        created_by=current_user.id
                    )
                    db.add(new_rec)

    db.commit()
    db.refresh(new_node)
    return new_node

class SimilarDeviationResponse(BaseModel):
    deviation_id: UUID
    node_id: UUID
    node_number: str
    node_name: str
    study_id: UUID
    study_name: str
    parameter: str
    guide_word: str
    deviation_description: str
    causes_count: int
    consequences_count: int
    safeguards_count: int
    recommendations_count: int

    class Config:
        from_attributes = True

@router.get("/deviations/similar", response_model=List[SimilarDeviationResponse])
def find_similar_deviations(
    parameter: str,
    guide_word: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find similar deviations from other nodes/studies"""
    # Find deviations with same parameter and guide word
    deviations = db.query(
        Deviation,
        HazopNode,
        HazopStudy
    ).join(
        HazopNode, Deviation.node_id == HazopNode.id
    ).join(
        HazopStudy, HazopNode.study_id == HazopStudy.id
    ).filter(
        Deviation.parameter == parameter,
        Deviation.guide_word == guide_word
    ).all()

    results = []
    for dev, node, study in deviations:
        # Count related items
        causes_count = db.query(Cause).filter(Cause.deviation_id == dev.id).count()
        consequences_count = db.query(Consequence).filter(Consequence.deviation_id == dev.id).count()
        safeguards_count = db.query(Safeguard).filter(Safeguard.deviation_id == dev.id).count()
        recommendations_count = db.query(Recommendation).filter(Recommendation.deviation_id == dev.id).count()

        # Only include if it has some data
        if causes_count > 0 or consequences_count > 0 or safeguards_count > 0:
            results.append({
                "deviation_id": dev.id,
                "node_id": node.id,
                "node_number": node.node_number,
                "node_name": node.node_name,
                "study_id": study.id,
                "study_name": study.title,
                "parameter": dev.parameter,
                "guide_word": dev.guide_word,
                "deviation_description": dev.deviation_description,
                "causes_count": causes_count,
                "consequences_count": consequences_count,
                "safeguards_count": safeguards_count,
                "recommendations_count": recommendations_count
            })

    return results

class CopyFromPreviousRequest(BaseModel):
    source_deviation_id: UUID
    copy_causes: bool = True
    copy_consequences: bool = True
    copy_safeguards: bool = True
    copy_recommendations: bool = False

@router.post("/deviations/{deviation_id}/copy-from-previous")
def copy_from_previous_deviation(
    deviation_id: UUID,
    req: CopyFromPreviousRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Copy data from a previous similar deviation"""
    # Get target deviation
    target_deviation = db.query(Deviation).filter(
        Deviation.id == deviation_id
    ).first()
    if not target_deviation:
        raise HTTPException(status_code=404, detail="Target deviation not found")

    # Get source deviation
    source_deviation = db.query(Deviation).filter(
        Deviation.id == req.source_deviation_id
    ).first()
    if not source_deviation:
        raise HTTPException(status_code=404, detail="Source deviation not found")

    copied_counts = {
        "causes": 0,
        "consequences": 0,
        "safeguards": 0,
        "recommendations": 0
    }

    # Copy causes
    if req.copy_causes:
        src_causes = db.query(Cause).filter(
            Cause.deviation_id == source_deviation.id
        ).all()
        for src_cause in src_causes:
            new_cause = Cause(
                deviation_id=target_deviation.id,
                cause_description=src_cause.cause_description,
                likelihood=src_cause.likelihood,
                created_by=current_user.id
            )
            db.add(new_cause)
            copied_counts["causes"] += 1

    # Copy consequences
    if req.copy_consequences:
        src_consequences = db.query(Consequence).filter(
            Consequence.deviation_id == source_deviation.id
        ).all()
        for src_cons in src_consequences:
            new_cons = Consequence(
                deviation_id=target_deviation.id,
                consequence_description=src_cons.consequence_description,
                severity=src_cons.severity,
                category=src_cons.category,
                created_by=current_user.id
            )
            db.add(new_cons)
            copied_counts["consequences"] += 1

    # Copy safeguards
    if req.copy_safeguards:
        src_safeguards = db.query(Safeguard).filter(
            Safeguard.deviation_id == source_deviation.id
        ).all()
        for src_safe in src_safeguards:
            new_safe = Safeguard(
                deviation_id=target_deviation.id,
                safeguard_description=src_safe.safeguard_description,
                safeguard_type=src_safe.safeguard_type,
                effectiveness=src_safe.effectiveness,
                created_by=current_user.id
            )
            db.add(new_safe)
            copied_counts["safeguards"] += 1

    # Copy recommendations
    if req.copy_recommendations:
        src_recs = db.query(Recommendation).filter(
            Recommendation.deviation_id == source_deviation.id
        ).all()
        for src_rec in src_recs:
            new_rec = Recommendation(
                deviation_id=target_deviation.id,
                recommendation_description=src_rec.recommendation_description,
                priority=src_rec.priority,
                responsible_party=src_rec.responsible_party,
                target_date=src_rec.target_date,
                status="open",
                created_by=current_user.id
            )
            db.add(new_rec)
            copied_counts["recommendations"] += 1

    db.commit()

    return {
        "message": "Data copied successfully",
        "copied": copied_counts
    }
