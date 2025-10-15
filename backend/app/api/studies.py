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
    """Create a new HAZOP study (organization-isolated)"""
    study = HazopStudy(
        title=req.title,
        description=req.description,
        facility_name=req.facility_name,
        created_by=current_user.id,
        organization_id=current_user.organization_id  # Auto-set from current user
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
    """List all HAZOP studies (organization-isolated)"""
    studies = db.query(HazopStudy).filter(
        HazopStudy.organization_id == current_user.organization_id
    ).all()
    return studies

@router.get("/{study_id}", response_model=StudyResponse)
def get_study(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific study (organization-isolated)"""
    study = db.query(HazopStudy).filter(
        HazopStudy.id == study_id,
        HazopStudy.organization_id == current_user.organization_id  # Data isolation
    ).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found or access denied")
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

# Dashboard endpoint
from app.models.risk_assessment import ImpactAssessment

@router.get("/{study_id}/dashboard")
def get_study_dashboard(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard data for a study"""
    study = db.query(HazopStudy).filter(HazopStudy.id == study_id).first()
    if not study:
        raise HTTPException(status_code=404, detail="Study not found")

    # Get all nodes for this study
    nodes = db.query(HazopNode).filter(HazopNode.study_id == study_id).all()
    
    # Count metrics
    total_nodes = len(nodes)
    total_deviations = db.query(Deviation).join(HazopNode).filter(
        HazopNode.study_id == study_id
    ).count()
    
    total_causes = db.query(Cause).join(Deviation).join(HazopNode).filter(
        HazopNode.study_id == study_id
    ).count()
    
    total_consequences = db.query(Consequence).join(Deviation).join(HazopNode).filter(
        HazopNode.study_id == study_id
    ).count()
    
    total_safeguards = db.query(Safeguard).join(Consequence).join(Deviation).join(HazopNode).filter(
        HazopNode.study_id == study_id
    ).count()
    
    total_recommendations = db.query(Recommendation).join(Consequence).join(Deviation).join(HazopNode).filter(
        HazopNode.study_id == study_id
    ).count()
    
    # Risk distribution
    risk_assessments = db.query(ImpactAssessment).join(Consequence).join(Deviation).join(HazopNode).filter(
        HazopNode.study_id == study_id
    ).all()
    
    risk_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for assessment in risk_assessments:
        if assessment.risk_level:
            risk_level = assessment.risk_level.lower()
            if risk_level in risk_distribution:
                risk_distribution[risk_level] += 1
    
    # Deviations by node
    deviations_by_node = []
    for node in nodes:
        dev_count = db.query(Deviation).filter(Deviation.node_id == node.id).count()
        deviations_by_node.append({
            "node_id": str(node.id),
            "node_name": node.node_name,
            "count": dev_count
        })
    
    # Sort by count descending
    deviations_by_node.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "study": {
            "id": str(study.id),
            "title": study.title,
            "facility_name": study.facility_name
        },
        "metrics": {
            "total_nodes": total_nodes,
            "total_deviations": total_deviations,
            "total_causes": total_causes,
            "total_consequences": total_consequences,
            "total_safeguards": total_safeguards,
            "total_recommendations": total_recommendations,
            "risk_distribution": risk_distribution,
            "deviations_by_node": deviations_by_node,
            "completion_percentage": 0  # Can be calculated based on filled fields
        }
    }


# Excel export endpoint
from fastapi.responses import StreamingResponse
import io

@router.get("/{study_id}/export/excel")
def export_study_to_excel(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export study to Excel"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        study = db.query(HazopStudy).filter(HazopStudy.id == study_id).first()
        if not study:
            raise HTTPException(status_code=404, detail="Study not found")
        
        wb = Workbook()
        ws = wb.active
        ws.title = "HAZOP Analysis"
        
        # Header styling
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F4788", end_color="1F4788", fill_type="solid")
        
        # Headers
        headers = ["Node", "Parameter", "Guide Word", "Deviation", "Cause", "Likelihood", 
                   "Consequence", "Severity", "Safeguard", "Recommendation", "Risk Level"]
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Get all nodes
        nodes = db.query(HazopNode).filter(HazopNode.study_id == study_id).all()
        
        row_num = 2
        for node in nodes:
            deviations = db.query(Deviation).filter(Deviation.node_id == node.id).all()
            
            for deviation in deviations:
                causes = db.query(Cause).filter(Cause.deviation_id == deviation.id).all()
                
                if not causes:
                    # Deviation without causes
                    ws.cell(row=row_num, column=1).value = f"{node.node_number} - {node.node_name}"
                    ws.cell(row=row_num, column=2).value = deviation.parameter
                    ws.cell(row=row_num, column=3).value = deviation.guide_word
                    ws.cell(row=row_num, column=4).value = deviation.deviation_description
                    row_num += 1
                
                for cause in causes:
                    consequences = db.query(Consequence).filter(Consequence.cause_id == cause.id).all()
                    
                    if not consequences:
                        # Cause without consequences
                        ws.cell(row=row_num, column=1).value = f"{node.node_number} - {node.node_name}"
                        ws.cell(row=row_num, column=2).value = deviation.parameter
                        ws.cell(row=row_num, column=3).value = deviation.guide_word
                        ws.cell(row=row_num, column=4).value = deviation.deviation_description
                        ws.cell(row=row_num, column=5).value = cause.cause_description
                        ws.cell(row=row_num, column=6).value = cause.likelihood
                        row_num += 1
                    
                    for consequence in consequences:
                        safeguards = db.query(Safeguard).filter(Safeguard.consequence_id == consequence.id).all()
                        recommendations = db.query(Recommendation).filter(Recommendation.consequence_id == consequence.id).all()
                        impact = db.query(ImpactAssessment).filter(ImpactAssessment.consequence_id == consequence.id).first()
                        
                        # Write main row
                        ws.cell(row=row_num, column=1).value = f"{node.node_number} - {node.node_name}"
                        ws.cell(row=row_num, column=2).value = deviation.parameter
                        ws.cell(row=row_num, column=3).value = deviation.guide_word
                        ws.cell(row=row_num, column=4).value = deviation.deviation_description
                        ws.cell(row=row_num, column=5).value = cause.cause_description
                        ws.cell(row=row_num, column=6).value = cause.likelihood
                        ws.cell(row=row_num, column=7).value = consequence.consequence_description
                        ws.cell(row=row_num, column=8).value = consequence.severity
                        
                        # Safeguards (combine multiple)
                        if safeguards:
                            safeguard_text = "; ".join([s.safeguard_description for s in safeguards])
                            ws.cell(row=row_num, column=9).value = safeguard_text
                        
                        # Recommendations (combine multiple)
                        if recommendations:
                            rec_text = "; ".join([r.recommendation_description for r in recommendations])
                            ws.cell(row=row_num, column=10).value = rec_text
                        
                        # Risk level
                        if impact:
                            ws.cell(row=row_num, column=11).value = impact.risk_level
                            
                            # Color code by risk level
                            risk_colors = {
                                "Critical": "EF4444",
                                "High": "F59E0B",
                                "Medium": "FBBF24",
                                "Low": "10B981"
                            }
                            if impact.risk_level in risk_colors:
                                risk_cell = ws.cell(row=row_num, column=11)
                                risk_cell.fill = PatternFill(start_color=risk_colors[impact.risk_level], 
                                                            end_color=risk_colors[impact.risk_level], 
                                                            fill_type="solid")
                        
                        row_num += 1
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save to bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Generate filename
        filename = f"{study.title.replace(' ', '_')}_HAZOP_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"Export error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
