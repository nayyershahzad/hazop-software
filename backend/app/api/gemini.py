from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from app.database import get_db
from app.models.hazop_entities import Cause, Consequence, Safeguard, Recommendation
from app.models.user import User
from app.api.deps import get_current_user
from app.models.study import HazopNode as Node, Deviation
from app.services.gemini_service import get_gemini_service

router = APIRouter(prefix="/api/gemini", tags=["gemini"])

# Request Models
class AIAssistanceContext(BaseModel):
    process_description: Optional[str] = None
    fluid_type: Optional[str] = None
    operating_conditions: Optional[str] = None
    previous_incidents: Optional[str] = None

class SuggestCausesRequest(BaseModel):
    deviation_id: UUID
    context: Optional[AIAssistanceContext] = None

class SuggestConsequencesRequest(BaseModel):
    deviation_id: UUID
    cause_id: Optional[UUID] = None
    context: Optional[AIAssistanceContext] = None

class SuggestSafeguardsRequest(BaseModel):
    deviation_id: UUID
    cause_id: Optional[UUID] = None
    consequence_id: Optional[UUID] = None
    context: Optional[AIAssistanceContext] = None

class SuggestRecommendationsRequest(BaseModel):
    deviation_id: UUID
    consequence_id: Optional[UUID] = None
    context: Optional[AIAssistanceContext] = None

class CompleteAnalysisRequest(BaseModel):
    deviation_id: UUID
    context: Optional[AIAssistanceContext] = None

# Response Models
class AISuggestion(BaseModel):
    text: str
    confidence: float
    reasoning: Optional[str] = None

    class Config:
        from_attributes = True

class AIConsequenceSuggestion(AISuggestion):
    severity: Optional[str] = None
    category: Optional[str] = None

class AISafeguardSuggestion(AISuggestion):
    type: Optional[str] = None
    effectiveness: Optional[str] = None

class AIRecommendationSuggestion(AISuggestion):
    priority: Optional[str] = None
    responsible_party: Optional[str] = None

class CompleteAnalysisResponse(BaseModel):
    causes: List[AISuggestion]
    consequences: List[AIConsequenceSuggestion]
    safeguards: List[AISafeguardSuggestion]

# Helper function to get a node from a deviation
async def get_node_from_deviation(deviation_id: UUID, db: Session):
    deviation = db.query(Deviation).filter(Deviation.id == deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    node = db.query(Node).filter(Node.id == deviation.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return node, deviation

# Endpoint to suggest causes based on node and deviation
@router.post("/suggest-causes", response_model=List[AISuggestion])
async def suggest_causes(
    req: SuggestCausesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI suggestions for causes of a deviation"""
    node, deviation = await get_node_from_deviation(req.deviation_id, db)

    # Get the Gemini service singleton
    gemini_service = get_gemini_service()

    # Generate suggestions from Gemini with cache support
    suggestions = await gemini_service.suggest_causes(
        node=node,
        deviation=deviation,
        context=req.context.dict() if req.context else None,
        db=db  # Pass DB session for caching
    )

    return suggestions

# Endpoint to suggest consequences for a deviation or cause
@router.post("/suggest-consequences", response_model=List[AIConsequenceSuggestion])
async def suggest_consequences(
    req: SuggestConsequencesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI suggestions for consequences of a deviation or cause"""
    node, deviation = await get_node_from_deviation(req.deviation_id, db)

    # Get cause text if provided
    cause_text = None
    if req.cause_id:
        cause = db.query(Cause).filter(Cause.id == req.cause_id).first()
        if not cause:
            raise HTTPException(status_code=404, detail="Cause not found")
        cause_text = cause.cause_description

    # Get the Gemini service singleton
    gemini_service = get_gemini_service()

    # Generate suggestions from Gemini with cache support
    suggestions = await gemini_service.suggest_consequences(
        node=node,
        deviation=deviation,
        cause_text=cause_text,
        context=req.context.dict() if req.context else None,
        db=db  # Pass DB session for caching
    )

    return suggestions

# Endpoint to suggest safeguards for a deviation, cause, or consequence
@router.post("/suggest-safeguards", response_model=List[AISafeguardSuggestion])
async def suggest_safeguards(
    req: SuggestSafeguardsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI suggestions for safeguards to mitigate risks"""
    node, deviation = await get_node_from_deviation(req.deviation_id, db)

    # Get cause text if provided
    cause_text = None
    if req.cause_id:
        cause = db.query(Cause).filter(Cause.id == req.cause_id).first()
        if not cause:
            raise HTTPException(status_code=404, detail="Cause not found")
        cause_text = cause.cause_description

    # Get consequence text if provided
    consequence_text = None
    if req.consequence_id:
        consequence = db.query(Consequence).filter(Consequence.id == req.consequence_id).first()
        if not consequence:
            raise HTTPException(status_code=404, detail="Consequence not found")
        consequence_text = consequence.consequence_description

    # Get the Gemini service singleton
    gemini_service = get_gemini_service()

    # Generate suggestions from Gemini with cache support
    suggestions = await gemini_service.suggest_safeguards(
        node=node,
        deviation=deviation,
        cause_text=cause_text,
        consequence_text=consequence_text,
        context=req.context.dict() if req.context else None,
        db=db  # Pass DB session for caching
    )

    return suggestions

# Endpoint to get a complete analysis (causes, consequences, and safeguards)
@router.post("/complete-analysis", response_model=CompleteAnalysisResponse)
async def complete_analysis(
    req: CompleteAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a complete HAZOP analysis with causes, consequences, and safeguards"""
    node, deviation = await get_node_from_deviation(req.deviation_id, db)

    # Get the Gemini service singleton
    gemini_service = get_gemini_service()

    # Generate complete analysis from Gemini with cache support
    analysis = await gemini_service.suggest_complete_analysis(
        node=node,
        deviation_text=deviation.deviation_description,
        context=req.context.dict() if req.context else None,
        db=db  # Pass DB session for caching
    )

    return analysis

# Request models for applying suggestions
class ApplyCauseSuggestionsRequest(BaseModel):
    deviation_id: UUID
    suggestions: List[AISuggestion]

class ApplyConsequenceSuggestionsRequest(BaseModel):
    deviation_id: UUID
    cause_id: Optional[UUID] = None
    suggestions: List[AIConsequenceSuggestion]

class ApplySafeguardSuggestionsRequest(BaseModel):
    deviation_id: UUID
    consequence_id: Optional[UUID] = None
    suggestions: List[AISafeguardSuggestion]

# Endpoint to apply AI suggestions directly to the database
@router.post("/apply-suggestions/causes")
async def apply_cause_suggestions(
    req: ApplyCauseSuggestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save AI-suggested causes to the database"""
    # Check if deviation exists
    deviation = db.query(Deviation).filter(Deviation.id == req.deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    created_causes = []
    for suggestion in req.suggestions:
        # Map confidence to likelihood
        likelihood = None
        if suggestion.confidence >= 90:
            likelihood = "almost_certain"
        elif suggestion.confidence >= 70:
            likelihood = "likely"
        elif suggestion.confidence >= 50:
            likelihood = "possible"
        elif suggestion.confidence >= 30:
            likelihood = "unlikely"
        else:
            likelihood = "rare"

        # Create cause with AI suggestion flag
        cause = Cause(
            deviation_id=req.deviation_id,
            cause_description=suggestion.text,
            likelihood=likelihood,
            ai_suggested=True,
            ai_confidence=suggestion.confidence,
            created_by=current_user.id
        )
        db.add(cause)
        created_causes.append(cause)

    db.commit()
    return {"message": f"Added {len(created_causes)} AI-suggested causes", "count": len(created_causes)}

# Endpoint to apply consequence suggestions
@router.post("/apply-suggestions/consequences")
async def apply_consequence_suggestions(
    req: ApplyConsequenceSuggestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save AI-suggested consequences to the database"""
    # Check if deviation exists
    deviation = db.query(Deviation).filter(Deviation.id == req.deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    # Check if cause exists (if provided)
    if req.cause_id:
        cause = db.query(Cause).filter(Cause.id == req.cause_id).first()
        if not cause:
            raise HTTPException(status_code=404, detail="Cause not found")

    created_consequences = []
    for suggestion in req.suggestions:
        # Create consequence with AI suggestion flag
        consequence = Consequence(
            deviation_id=req.deviation_id,
            cause_id=req.cause_id,
            consequence_description=suggestion.text,
            severity=suggestion.severity,
            category=suggestion.category,
            ai_suggested=True,
            ai_confidence=suggestion.confidence,
            created_by=current_user.id
        )
        db.add(consequence)
        created_consequences.append(consequence)

    db.commit()
    return {"message": f"Added {len(created_consequences)} AI-suggested consequences", "count": len(created_consequences)}

# Endpoint to apply safeguard suggestions (for existing safeguards)
@router.post("/apply-suggestions/safeguards")
async def apply_safeguard_suggestions(
    req: ApplySafeguardSuggestionsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save AI-suggested safeguards to the database"""
    # Check if deviation exists
    deviation = db.query(Deviation).filter(Deviation.id == req.deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    # Check if consequence exists (if provided)
    if req.consequence_id:
        consequence = db.query(Consequence).filter(Consequence.id == req.consequence_id).first()
        if not consequence:
            raise HTTPException(status_code=404, detail="Consequence not found")

    created_safeguards = []
    for suggestion in req.suggestions:
        # Create safeguard with AI suggestion flag
        safeguard = Safeguard(
            deviation_id=req.deviation_id,
            consequence_id=req.consequence_id,
            safeguard_description=suggestion.text,
            safeguard_type=suggestion.type,
            effectiveness=suggestion.effectiveness,
            ai_suggested=True,
            ai_confidence=suggestion.confidence,
            created_by=current_user.id
        )
        db.add(safeguard)
        created_safeguards.append(safeguard)

    db.commit()
    return {"message": f"Added {len(created_safeguards)} AI-suggested safeguards", "count": len(created_safeguards)}

# Endpoint to apply recommendation suggestions (for AI-suggested actions)
@router.post("/apply-suggestions/recommendations")
async def apply_recommendation_suggestions(
    req: ApplySafeguardSuggestionsRequest,  # Same structure as safeguards
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save AI-suggested recommendations to the database"""
    # Check if deviation exists
    deviation = db.query(Deviation).filter(Deviation.id == req.deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    # Check if consequence exists (if provided)
    if req.consequence_id:
        consequence = db.query(Consequence).filter(Consequence.id == req.consequence_id).first()
        if not consequence:
            raise HTTPException(status_code=404, detail="Consequence not found")

    created_recommendations = []
    for suggestion in req.suggestions:
        # Map AI suggestion type to priority
        priority = "medium"  # Default
        if suggestion.confidence >= 90:
            priority = "high"
        elif suggestion.confidence >= 70:
            priority = "medium"
        else:
            priority = "low"

        # Create recommendation with AI suggestion flag
        recommendation = Recommendation(
            deviation_id=req.deviation_id,
            consequence_id=req.consequence_id,
            recommendation_description=suggestion.text,
            priority=priority,
            status='open',
            ai_suggested=True,
            ai_confidence=suggestion.confidence,
            created_by=current_user.id
        )
        db.add(recommendation)
        created_recommendations.append(recommendation)

    db.commit()
    return {"message": f"Added {len(created_recommendations)} AI-suggested recommendations", "count": len(created_recommendations)}

# Contextual Knowledge Injection endpoints

class ContextualKnowledgeRequest(BaseModel):
    node_id: UUID
    deviation_id: Optional[UUID] = None
    topic: Optional[str] = None  # Optional specific topic to search for
    context: Optional[AIAssistanceContext] = None

class RegulationReference(BaseModel):
    title: str
    description: str
    source: str
    relevance: str
    link: Optional[str] = None

class IncidentReport(BaseModel):
    title: str
    description: str
    date: str
    facility: str
    relevance: str

class TechnicalReference(BaseModel):
    title: str
    description: str
    source: str
    relevance: str

class ContextualKnowledgeResponse(BaseModel):
    regulations: List[RegulationReference]
    incident_reports: List[IncidentReport]
    technical_references: List[TechnicalReference]
    industry_benchmarks: List[Dict]

# Workshop intelligence and preparation endpoints

class WorkshopPreparationRequest(BaseModel):
    study_id: UUID
    node_ids: Optional[List[UUID]] = None  # Optional specific nodes to analyze

class WorkshopPreparationResponse(BaseModel):
    high_risk_areas: List[Dict]
    suggested_questions: List[Dict]
    similar_nodes: List[Dict]
    reference_materials: List[Dict]

@router.post("/contextual-knowledge", response_model=ContextualKnowledgeResponse)
async def get_contextual_knowledge(
    req: ContextualKnowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve contextual knowledge like regulations, standards,
    incident reports, and technical data relevant to a node or deviation
    """
    # Get node
    node = db.query(Node).filter(Node.id == req.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get deviation if provided
    deviation = None
    if req.deviation_id:
        deviation = db.query(Deviation).filter(Deviation.id == req.deviation_id).first()
        if not deviation:
            raise HTTPException(status_code=404, detail="Deviation not found")

    # TODO: In a real implementation, this would query Gemini API with the node details
    # and return relevant regulations, incidents, etc.

    # Example data - this would normally come from Gemini
    regulations = []
    incident_reports = []
    technical_references = []
    industry_benchmarks = []

    # Process type information based on node name/description
    is_pressure_vessel = "vessel" in node.node_name.lower() or "tank" in node.node_name.lower()
    is_piping = "pipe" in node.node_name.lower() or "line" in node.node_name.lower()
    is_pump = "pump" in node.node_name.lower()
    is_heat_exchanger = "exchanger" in node.node_name.lower() or "heater" in node.node_name.lower()
    is_reactor = "reactor" in node.node_name.lower()

    # Example process parameters from deviation if available
    if deviation:
        parameter = deviation.parameter.lower()  # e.g., flow, pressure, temperature
        guide_word = deviation.guide_word.lower()  # e.g., no, more, less

        # Add relevant regulations based on parameter and equipment
        if parameter == "pressure":
            regulations.append({
                "title": "ASME Boiler and Pressure Vessel Code",
                "description": "Standards for pressure vessels and piping systems",
                "source": "American Society of Mechanical Engineers",
                "relevance": "Mandatory requirements for pressure vessel design and testing",
                "link": "https://www.asme.org/codes-standards/find-codes-standards/bpvc-complete-code-boiler-pressure-vessel-code-complete-set"
            })

            if guide_word in ["more", "high"]:
                incident_reports.append({
                    "title": "Pressure Vessel Failure at Chemical Plant",
                    "description": "Overpressure caused vessel rupture due to blocked outlet",
                    "date": "2018-07-15",
                    "facility": "Generic Chemical Plant, Texas",
                    "relevance": "Similar overpressure scenario - demonstrates importance of pressure relief systems"
                })

        if parameter == "temperature":
            regulations.append({
                "title": "API 521: Pressure-relieving and Depressuring Systems",
                "description": "Guidelines for thermal relief and fire exposure",
                "source": "American Petroleum Institute",
                "relevance": "Guidance on thermal relief requirements and fire scenarios",
                "link": "https://www.api.org/products-and-services/standards/important-standards-announcements/standard-521"
            })

            technical_references.append({
                "title": "Material Temperature Limits",
                "description": "Maximum temperature limits for common materials in process equipment",
                "source": "Engineering Handbook",
                "relevance": "Provides maximum allowable temperatures for common process materials"
            })

    # Add equipment-specific references
    if is_pressure_vessel:
        regulations.append({
            "title": "ASME Section VIII Division 1",
            "description": "Rules for Construction of Pressure Vessels",
            "source": "American Society of Mechanical Engineers",
            "relevance": "Mandatory requirements for design, fabrication, inspection, and testing",
            "link": "https://www.asme.org/codes-standards/find-codes-standards/bpvc-viii-1-bpvc-section-viii-rules-construction-pressure-vessels-division-1"
        })

        industry_benchmarks.append({
            "title": "Pressure Vessel Inspection Frequency",
            "description": "Industry benchmarks for vessel inspection intervals",
            "value": "External: 5 years, Internal: 10 years",
            "source": "API 510"
        })

    if is_piping:
        regulations.append({
            "title": "ASME B31.3 Process Piping",
            "description": "Requirements for piping in chemical, petroleum, and related industries",
            "source": "American Society of Mechanical Engineers",
            "relevance": "Mandatory code for design, materials, fabrication, inspection and testing",
            "link": "https://www.asme.org/codes-standards/find-codes-standards/b31-3-process-piping"
        })

        technical_references.append({
            "title": "Recommended Flow Velocities",
            "description": "Maximum recommended flow velocities for different piping services",
            "source": "Process Design Handbook",
            "relevance": "Helps prevent erosion and excessive pressure drop"
        })

    if is_heat_exchanger:
        technical_references.append({
            "title": "TEMA Standards",
            "description": "Standards for shell and tube heat exchangers",
            "source": "Tubular Exchanger Manufacturers Association",
            "relevance": "Design standards for mechanical design of shell and tube heat exchangers"
        })

    if is_pump:
        technical_references.append({
            "title": "API 610: Centrifugal Pumps",
            "description": "Standard for centrifugal pumps for petroleum, petrochemical and gas industries",
            "source": "American Petroleum Institute",
            "relevance": "Design, operation and maintenance standards for centrifugal pumps"
        })

        incident_reports.append({
            "title": "Pump Seal Failure and Fire",
            "description": "Mechanical seal failure led to release of flammable material and fire",
            "date": "2019-03-22",
            "facility": "Generic Refinery, California",
            "relevance": "Highlights importance of proper seal selection and monitoring"
        })

    if is_reactor:
        regulations.append({
            "title": "OSHA 1910.119: Process Safety Management",
            "description": "Requirements for preventing or minimizing catastrophic releases of toxic, reactive, flammable, or explosive chemicals",
            "source": "Occupational Safety and Health Administration",
            "relevance": "Mandatory requirements for reactive processes including hazard analysis",
            "link": "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119"
        })

        incident_reports.append({
            "title": "Runaway Reaction Incident",
            "description": "Loss of cooling led to temperature excursion and pressure relief",
            "date": "2017-09-03",
            "facility": "Generic Specialty Chemicals, Germany",
            "relevance": "Demonstrates importance of understanding reaction kinetics and proper cooling systems"
        })

    # Return the contextual knowledge
    return {
        "regulations": regulations,
        "incident_reports": incident_reports,
        "technical_references": technical_references,
        "industry_benchmarks": industry_benchmarks
    }

@router.post("/workshop-preparation", response_model=WorkshopPreparationResponse)
async def prepare_workshop_intelligence(
    req: WorkshopPreparationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate workshop preparation materials and intelligence
    to help facilitators prepare for HAZOP sessions
    """
    # Implementation will require additional Gemini service methods
    # This is a placeholder that returns empty lists for now

    return {
        "high_risk_areas": [],
        "suggested_questions": [],
        "similar_nodes": [],
        "reference_materials": []
    }

# Cache statistics endpoint
@router.get("/cache-stats")
async def get_cache_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get statistics about the Gemini API cache.
    Only available to users with admin or owner roles.
    """
    # Check if user has required permission
    if current_user.org_role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access cache statistics"
        )

    # Create cache service
    from app.services.gemini_cache import GeminiCacheService
    cache_service = GeminiCacheService(db)

    # Get statistics
    stats = cache_service.get_stats()

    # Calculate estimated cost savings
    # Assuming average cost per Gemini API call: $0.0004
    estimated_cost_per_call = 0.0004
    total_hits = stats.get("total_hits", 0)
    total_entries = stats.get("total_entries", 0)
    cache_hits = total_hits - total_entries if total_hits > total_entries else 0

    estimated_savings = round(cache_hits * estimated_cost_per_call, 2)
    hit_rate = round((cache_hits / total_hits * 100) if total_hits > 0 else 0, 2)

    return {
        **stats,
        "estimated_cost_savings_usd": estimated_savings,
        "cache_hit_rate_percent": hit_rate,
        "cache_status": "active" if stats.get("enabled", False) else "disabled",
    }

# Smart Risk Recalculation Endpoints

class RiskRecalculationRequest(BaseModel):
    consequence_id: UUID
    context: Optional[AIAssistanceContext] = None

class RiskSuggestion(BaseModel):
    current_likelihood: int
    suggested_likelihood: int
    current_severity: int
    suggested_severity: int
    reasoning: str
    historical_comparison: Optional[str] = None
    industry_norm: Optional[str] = None

# Safeguard Effectiveness Evaluation Endpoints

class SafeguardEvaluationRequest(BaseModel):
    safeguard_id: UUID
    context: Optional[AIAssistanceContext] = None

class SafeguardEffectiveness(BaseModel):
    confidence_score: float
    effectiveness_score: float
    reasoning: str
    improvement_suggestions: Optional[str] = None
    before_risk_level: Optional[str] = None
    after_risk_level: Optional[str] = None

@router.post("/suggest-risk-assessment", response_model=RiskSuggestion)
async def suggest_risk_assessment(
    req: RiskRecalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI suggestions for risk assessment likelihood and severity
    based on historical data and industry norms
    """
    # Get consequence
    consequence = db.query(Consequence).filter(Consequence.id == req.consequence_id).first()
    if not consequence:
        raise HTTPException(status_code=404, detail="Consequence not found")

    # Get deviation
    deviation = db.query(Deviation).filter(Deviation.id == consequence.deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    # Get node
    node = db.query(Node).filter(Node.id == deviation.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get existing impact assessment if available
    from app.models.risk_assessment import ImpactAssessment
    impact_assessment = db.query(ImpactAssessment).filter(
        ImpactAssessment.consequence_id == req.consequence_id
    ).first()

    # Default values if no assessment exists
    current_likelihood = 1
    current_severity = 1

    if impact_assessment:
        current_likelihood = impact_assessment.likelihood
        current_severity = impact_assessment.max_impact

    # TODO: Implement actual Gemini call for smart risk suggestions
    # For now, generate placeholder suggestions
    suggested_likelihood = min(current_likelihood + 1, 5)  # Suggest slightly higher
    suggested_severity = min(current_severity + 1, 5)      # Suggest slightly higher

    reasoning = f"Based on the description '{consequence.consequence_description}', the suggested likelihood and severity have been adjusted to reflect potential risks more accurately."
    historical_comparison = "Historical data for similar scenarios suggests this event may be more frequent than initially estimated."
    industry_norm = "Industry standards for similar processes typically rate this type of consequence with higher severity."

    return {
        "current_likelihood": current_likelihood,
        "suggested_likelihood": suggested_likelihood,
        "current_severity": current_severity,
        "suggested_severity": suggested_severity,
        "reasoning": reasoning,
        "historical_comparison": historical_comparison,
        "industry_norm": industry_norm
    }

@router.post("/evaluate-safeguard-effectiveness", response_model=SafeguardEffectiveness)
async def evaluate_safeguard_effectiveness(
    req: SafeguardEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate the effectiveness of a safeguard and provide improvement suggestions
    """
    # Get safeguard
    safeguard = db.query(Safeguard).filter(Safeguard.id == req.safeguard_id).first()
    if not safeguard:
        raise HTTPException(status_code=404, detail="Safeguard not found")

    # Get consequence if linked
    consequence = None
    if safeguard.consequence_id:
        consequence = db.query(Consequence).filter(Consequence.id == safeguard.consequence_id).first()

    # Get deviation
    deviation = db.query(Deviation).filter(Deviation.id == safeguard.deviation_id).first()
    if not deviation:
        raise HTTPException(status_code=404, detail="Deviation not found")

    # Get node
    node = db.query(Node).filter(Node.id == deviation.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get impact assessments associated with this safeguard's consequence or deviation
    from app.models.risk_assessment import ImpactAssessment
    impact_assessment = None

    if safeguard.consequence_id:
        impact_assessment = db.query(ImpactAssessment).filter(
            ImpactAssessment.consequence_id == safeguard.consequence_id
        ).first()

    if not impact_assessment and deviation:
        # Fall back to deviation-level assessment if no consequence-specific one exists
        impact_assessment = db.query(ImpactAssessment).filter(
            ImpactAssessment.deviation_id == deviation.id
        ).first()

    # Calculate effectiveness based on safeguard type and quality of description
    # This is a placeholder - in a real implementation, Gemini would analyze the safeguard

    effectiveness_score = 0.65  # Default effectiveness score
    confidence_score = 0.75     # Default confidence score

    # Adjust based on existing safeguard data if available
    if safeguard.effectiveness:
        if safeguard.effectiveness.lower() == "high":
            effectiveness_score = 0.85
        elif safeguard.effectiveness.lower() == "medium":
            effectiveness_score = 0.65
        elif safeguard.effectiveness.lower() == "low":
            effectiveness_score = 0.35

    # Adjust confidence score based on description length and type
    description_length = len(safeguard.safeguard_description)
    if description_length > 200:
        confidence_score += 0.1
    elif description_length < 50:
        confidence_score -= 0.1

    if safeguard.safeguard_type:
        if safeguard.safeguard_type.lower() == "prevention":
            confidence_score += 0.05
        elif safeguard.safeguard_type.lower() == "detection":
            # Detection is less effective than prevention
            confidence_score -= 0.05

    # Ensure scores are within 0-1 range
    effectiveness_score = max(0.0, min(1.0, effectiveness_score))
    confidence_score = max(0.0, min(1.0, confidence_score))

    # Risk levels before and after
    before_risk_level = "High"
    after_risk_level = "Medium"

    if impact_assessment:
        # Use actual risk level if available
        before_risk_level = impact_assessment.risk_level

        # Simulate reduced risk level
        risk_levels = ["Low", "Medium", "High", "Critical"]
        current_index = risk_levels.index(before_risk_level)
        if effectiveness_score > 0.7 and current_index > 0:
            after_risk_level = risk_levels[current_index - 1]
        else:
            after_risk_level = before_risk_level

    # Generate reasoning
    reasoning = f"The safeguard '{safeguard.safeguard_description}' provides {int(effectiveness_score * 100)}% effectiveness for the {deviation.parameter}/{deviation.guide_word} deviation."

    # Improvement suggestions based on effectiveness
    improvement_suggestions = None
    if effectiveness_score < 0.5:
        improvement_suggestions = "Consider adding specific inspection procedures, testing frequency, or quantitative performance standards to improve this safeguard."
    elif effectiveness_score < 0.8:
        improvement_suggestions = "This safeguard could be enhanced with redundancy or by adding monitoring capabilities to detect potential failures."

    return {
        "confidence_score": confidence_score,
        "effectiveness_score": effectiveness_score,
        "reasoning": reasoning,
        "improvement_suggestions": improvement_suggestions,
        "before_risk_level": before_risk_level,
        "after_risk_level": after_risk_level
    }