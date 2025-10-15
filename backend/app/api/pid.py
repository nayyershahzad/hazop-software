from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import os
import shutil
from datetime import datetime
from app.database import get_db
from app.models.pid import PIDDocument, NodePIDLocation
from app.models.user import User
from app.api.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/pid", tags=["pid"])

# Schemas
class PIDDocumentResponse(BaseModel):
    id: UUID
    study_id: UUID
    node_id: UUID
    filename: str
    total_pages: Optional[int]
    uploaded_at: datetime

    class Config:
        from_attributes = True

class NodeLocationRequest(BaseModel):
    node_id: UUID
    pid_document_id: UUID
    page_number: int
    x_coordinate: float
    y_coordinate: float
    width: float = 10.0
    height: float = 5.0
    color: str = '#FFFF00'

class NodeLocationResponse(BaseModel):
    id: UUID
    node_id: UUID
    pid_document_id: UUID
    page_number: int
    x_coordinate: float
    y_coordinate: float
    width: float
    height: float
    color: str
    created_at: datetime

    class Config:
        from_attributes = True

# Upload P&ID for a specific node
@router.post("/upload/{node_id}", response_model=PIDDocumentResponse)
async def upload_pid(
    node_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a P&ID document (PDF) for a specific node"""
    # Get node to verify it exists and get study_id
    from app.models.study import HazopNode
    node = db.query(HazopNode).filter(HazopNode.id == node_id).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Create upload directory if it doesn't exist
    study_id = node.study_id
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(study_id))
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Get PDF page count (optional - requires PyPDF2)
    total_pages = None
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
    except:
        pass  # PyPDF2 not installed or error reading

    # Create database record
    pid_doc = PIDDocument(
        study_id=study_id,
        node_id=node_id,
        filename=file.filename,
        file_path=file_path,
        total_pages=total_pages,
        uploaded_by=current_user.id
    )
    db.add(pid_doc)
    db.commit()
    db.refresh(pid_doc)

    return pid_doc

# List P&IDs for a specific node
@router.get("/node/{node_id}", response_model=List[PIDDocumentResponse])
def list_pids_for_node(
    node_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all P&ID documents for a specific node"""
    pids = db.query(PIDDocument).filter(
        PIDDocument.node_id == node_id
    ).order_by(PIDDocument.uploaded_at.desc()).all()
    return pids

# Get P&ID file
@router.get("/file/{pid_id}")
def get_pid_file(
    pid_id: UUID,
    db: Session = Depends(get_db)
):
    """Download/view a P&ID file - temporarily without auth for debugging"""
    print(f"[DEBUG] Requested PID file: {pid_id}")
    pid_doc = db.query(PIDDocument).filter(PIDDocument.id == pid_id).first()
    if not pid_doc:
        print(f"[DEBUG] PID not found in database: {pid_id}")
        raise HTTPException(status_code=404, detail="P&ID document not found")

    print(f"[DEBUG] File path: {pid_doc.file_path}")
    if not os.path.exists(pid_doc.file_path):
        print(f"[DEBUG] File not found on disk: {pid_doc.file_path}")
        raise HTTPException(status_code=404, detail=f"File not found on disk: {pid_doc.file_path}")

    print(f"[DEBUG] Serving file: {pid_doc.file_path}")
    return FileResponse(
        pid_doc.file_path,
        media_type="application/pdf",
        filename=pid_doc.filename,
        headers={
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Content-Range, Content-Length"
        }
    )

# Delete P&ID
@router.delete("/{pid_id}")
def delete_pid(
    pid_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a P&ID document"""
    pid_doc = db.query(PIDDocument).filter(PIDDocument.id == pid_id).first()
    if not pid_doc:
        raise HTTPException(status_code=404, detail="P&ID document not found")

    # Delete file from disk
    if os.path.exists(pid_doc.file_path):
        os.remove(pid_doc.file_path)

    # Delete from database
    db.delete(pid_doc)
    db.commit()

    return {"message": "P&ID deleted successfully"}

# Mark node location on P&ID (allows multiple highlights per node)
@router.post("/location", response_model=NodeLocationResponse)
def create_node_location(
    req: NodeLocationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a node's location on a P&ID - creates a new highlight every time"""
    # Always create a new highlight (no more updating existing)
    location = NodePIDLocation(
        node_id=req.node_id,
        pid_document_id=req.pid_document_id,
        page_number=req.page_number,
        x_coordinate=req.x_coordinate,
        y_coordinate=req.y_coordinate,
        width=req.width,
        height=req.height,
        color=req.color,
        created_by=current_user.id
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

# Get node location
@router.get("/location/node/{node_id}", response_model=Optional[NodeLocationResponse])
def get_node_location(
    node_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a node's location on P&ID"""
    location = db.query(NodePIDLocation).filter(
        NodePIDLocation.node_id == node_id
    ).first()
    return location

# Get all locations for a P&ID
@router.get("/location/pid/{pid_id}", response_model=List[NodeLocationResponse])
def get_pid_locations(
    pid_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all node locations for a P&ID document"""
    locations = db.query(NodePIDLocation).filter(
        NodePIDLocation.pid_document_id == pid_id
    ).all()
    return locations

# Delete node location
@router.delete("/location/{location_id}")
def delete_node_location(
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a node location marker"""
    location = db.query(NodePIDLocation).filter(NodePIDLocation.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    db.delete(location)
    db.commit()
    return {"message": "Location deleted successfully"}
