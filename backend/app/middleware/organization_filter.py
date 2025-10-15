"""
Organization-level data isolation middleware.

This middleware automatically adds organization_id filters to database queries,
ensuring users can only access data from their own organization.

Note: For MVP deployment, we're updating critical endpoints manually.
Future versions can use SQLAlchemy events for automatic filtering.
"""

from sqlalchemy import event
from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.models.user import User
from app.models.study import HazopStudy

def add_organization_filters(query, model, organization_id):
    """
    Add organization_id filter to query if model has organization_id column.

    Args:
        query: SQLAlchemy query object
        model: SQLAlchemy model class
        organization_id: UUID of the organization

    Returns:
        Modified query with organization filter
    """
    if hasattr(model, 'organization_id'):
        return query.filter(model.organization_id == organization_id)
    return query

def get_organization_from_context():
    """
    Get organization ID from request context.
    This would typically use contextvars or thread-local storage.

    For MVP, we're handling this at the endpoint level instead.
    """
    # TODO: Implement with contextvars for production
    pass

class OrganizationFilterMixin:
    """
    Mixin class to add organization filtering methods to SQLAlchemy models.

    Usage:
        class HazopStudy(Base, OrganizationFilterMixin):
            ...

        # Then in queries:
        studies = HazopStudy.filter_by_org(session, org_id).all()
    """

    @classmethod
    def filter_by_org(cls, session: Session, organization_id):
        """Filter query by organization ID"""
        if hasattr(cls, 'organization_id'):
            return session.query(cls).filter(cls.organization_id == organization_id)
        return session.query(cls)

    @classmethod
    def get_by_id_and_org(cls, session: Session, item_id, organization_id):
        """Get single item by ID and organization (for data isolation)"""
        if hasattr(cls, 'organization_id'):
            return session.query(cls).filter(
                cls.id == item_id,
                cls.organization_id == organization_id
            ).first()
        return session.query(cls).filter(cls.id == item_id).first()


# Helper functions for common query patterns

def verify_study_access(session: Session, study_id, organization_id) -> bool:
    """
    Verify that a study belongs to the given organization.
    Returns True if access is allowed, False otherwise.
    """
    study = session.query(HazopStudy).filter(
        HazopStudy.id == study_id,
        HazopStudy.organization_id == organization_id
    ).first()
    return study is not None


def verify_user_in_organization(session: Session, user_id, organization_id) -> bool:
    """
    Verify that a user belongs to the given organization.
    Returns True if user is in organization, False otherwise.
    """
    user = session.query(User).filter(
        User.id == user_id,
        User.organization_id == organization_id
    ).first()
    return user is not None
