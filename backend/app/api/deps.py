from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import decode_token
from uuid import UUID

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    Returns full User object with organization relationship loaded.

    This is the main dependency for protecting endpoints and enforcing
    organization-level data isolation.
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        organization_id: str = payload.get("organization_id")

        if email is None or user_id is None or organization_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Query user and verify they belong to the organization in the token
    user = db.query(User).filter(
        User.id == user_id,
        User.email == email,
        User.organization_id == organization_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or organization mismatch"
        )

    # Verify organization is active
    organization = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not organization or not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization account is suspended"
        )

    return user

def get_organization_id(current_user: User = Depends(get_current_user)) -> UUID:
    """
    Helper dependency to extract organization_id from current user.
    Useful for filtering queries by organization.
    """
    return current_user.organization_id

def require_org_role(required_roles: list[str]):
    """
    Dependency factory for role-based access control within an organization.

    Example usage:
        @router.delete("/studies/{id}")
        def delete_study(
            study_id: UUID,
            current_user: User = Depends(require_org_role(["owner", "admin"]))
        ):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.org_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker
