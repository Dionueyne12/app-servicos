from fastapi import Query
from pydantic import BaseModel


class PageParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        per_page: int = Query(default=20, ge=1, le=100),
    ) -> None:
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page


class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int


def build_pagination_meta(total: int, params: PageParams) -> PaginationMeta:
    total_pages = (total + params.per_page - 1) // params.per_page if total else 0
    return PaginationMeta(
        page=params.page,
        per_page=params.per_page,
        total=total,
        total_pages=total_pages,
    )
