from typing import Generic, List, TypeVar
from pydantic import BaseModel, conint


class PageParams(BaseModel):
    page: conint(ge=1) = 1
    size: conint(ge=1, le=100) = 10


T = TypeVar("T")


class PagedResponseSchema(BaseModel, Generic[T]):
    totalPages: int
    totalElements: int
    page: int
    size: int
    results: List[T]
