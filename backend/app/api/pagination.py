from typing import List, TypeVar, Generic, Optional, Dict, Any
from fastapi import Query
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginationParams:
    """
    Pagination parameters for list endpoints.
    """

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
        fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response")
    ):
        self.skip = skip
        self.limit = limit
        self.fields = fields.split(",") if fields else None


class PaginatedResponse(GenericModel, Generic[T]):
    """
    Standard paginated response format for list endpoints.
    """
    items: List[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_more: bool
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        items: List[T],
        total_count: int,
        params: PaginationParams,
        metadata: Optional[Dict[str, Any]] = None
    ):
        page = (params.skip // params.limit) + 1
        total_pages = (total_count + params.limit - 1) // params.limit if params.limit > 0 else 0

        return cls(
            items=items,
            total_count=total_count,
            page=page,
            page_size=params.limit,
            total_pages=total_pages,
            has_more=params.skip + len(items) < total_count,
            metadata=metadata
        )