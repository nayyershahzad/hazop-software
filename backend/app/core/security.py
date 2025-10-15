from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from typing import Optional
from uuid import UUID

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode a JWT token"""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

class TokenData:
    """Data extracted from JWT token"""
    def __init__(self, user_id: str, email: str, organization_id: str, org_role: str):
        self.user_id = user_id
        self.email = email
        self.organization_id = organization_id
        self.org_role = org_role

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = None
) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token.
    Returns TokenData with user and organization information.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_token(token)
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        organization_id: str = payload.get("organization_id")
        org_role: str = payload.get("org_role")

        if email is None or user_id is None or organization_id is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=user_id,
            email=email,
            organization_id=organization_id,
            org_role=org_role or "member"
        )
        return token_data

    except JWTError:
        raise credentials_exception
