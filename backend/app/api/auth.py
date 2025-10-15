from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import hash_password, verify_password, create_access_token
import re

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization_name: str
    role: str = "analyst"

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password too long (max 72 characters)')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name"""
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        if len(v) > 255:
            raise ValueError('Full name too long (max 255 characters)')
        return v.strip()

    @validator('organization_name')
    def validate_organization_name(cls, v):
        """Validate organization name"""
        if len(v.strip()) < 2:
            raise ValueError('Organization name must be at least 2 characters')
        if len(v) > 255:
            raise ValueError('Organization name too long (max 255 characters)')
        return v.strip()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    organization: dict

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user and create their organization.

    This endpoint creates both an organization and the first user (owner) for that organization.
    All subsequent users can be invited by the organization owner.
    """
    # Check if user already exists
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please login instead."
        )

    # Generate organization slug
    base_slug = Organization.generate_slug(req.organization_name)
    slug = base_slug
    counter = 1

    # Ensure unique slug
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create organization
    organization = Organization(
        name=req.organization_name,
        slug=slug,
        subscription_plan='free',
        subscription_status='active'
    )
    db.add(organization)
    db.flush()  # Get the organization ID without committing

    # Create user as organization owner
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
        organization_id=organization.id,
        org_role='owner'  # First user is always the owner
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(organization)

    # Create token with organization context
    token = create_access_token({
        "sub": user.email,
        "user_id": str(user.id),
        "organization_id": str(organization.id),
        "org_role": user.org_role
    })

    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_role": user.org_role,
            "organization_id": str(organization.id)
        },
        "organization": organization.to_dict()
    }

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user with email and password.

    Returns access token with user and organization information.
    """
    user = db.query(User).filter(User.email == req.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again."
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials and try again."
        )

    # Get user's organization
    organization = db.query(Organization).filter(Organization.id == user.organization_id).first()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User organization not found. Please contact support."
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your organization account has been suspended. Please contact support."
        )

    # Create token with organization context
    token = create_access_token({
        "sub": user.email,
        "user_id": str(user.id),
        "organization_id": str(organization.id),
        "org_role": user.org_role
    })

    return {
        "access_token": token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "org_role": user.org_role,
            "organization_id": str(organization.id)
        },
        "organization": organization.to_dict()
    }
