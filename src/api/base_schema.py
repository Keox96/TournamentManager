"""
FastAPI API module.
"""

from enum import StrEnum
from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from src.domain.exceptions.generic_exceptions import InvalidSortFormatError
from src.domain.repositories.filters import (
    PaginationParams,
    SearchParams,
    SortOrder,
    SortParam,
    SortParams,
)


class BaseSortRequest[TSortField: StrEnum]:
    """
    Schema representing a base sort request payload.
    """

    sort_field_class: type[TSortField]
    default_sort_field: TSortField

    def __init__(
        self,
        sort: Annotated[
            list[str] | None,
            Query(description="Format: field:order — ex: name:asc,created_at:desc"),
        ] = None,
    ):
        """
        Initialize a new init instance.

        Args:
        sort: The sort parameter.
        """
        self._sort = sort or [f"{self.default_sort_field}:desc"]

    def to_domain(self) -> SortParams[TSortField]:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        sorts = []
        for item in self._sort:
            match item.split(":"):
                case [field_str, order_str]:
                    try:
                        sorts.append(
                            SortParam(
                                field=self.sort_field_class(field_str),
                                order=SortOrder(order_str),
                            )
                        )
                    except ValueError as err:
                        raise InvalidSortFormatError(
                            message=f"Invalid sort '{item}'. ",
                            details={
                                "invalid_field": field_str,
                                "invalid_order": order_str,
                            },
                        ) from err
                case [field_str]:
                    try:
                        sorts.append(SortParam(field=self.sort_field_class(field_str)))
                    except ValueError as err:
                        raise InvalidSortFormatError(
                            message=f"Invalid sort field '{field_str}'. ",
                            details={"invalid_field": field_str},
                        ) from err
                case _:
                    raise InvalidSortFormatError(
                        message=f"Invalid sort format '{item}'. Expected format: 'field:order'.",
                    )
        return SortParams(sorts=sorts)


class PaginationRequest:
    """Query params de pagination — remplace Params de fastapi-pagination."""

    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 20,
    ):
        """
        Initialize a new init instance.

        Args:
        page: The page parameter.
        size: The size parameter.
        """
        self.page = page
        self.size = size

    def to_domain(self) -> PaginationParams:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return PaginationParams(page=self.page, size=self.size)


class PaginatedResponse[T](BaseModel):
    """
    Schema representing a paginated response payload.
    """

    items: list[T]
    total: int
    page: int
    size: int
    total_pages: int


class SearchRequest:
    """
    Schema representing a search request payload.
    """

    def __init__(
        self,
        search: Annotated[
            str | None,
            Query(
                max_length=100,
                description="Recherche full-text sur les champs disponibles",
            ),
        ] = None,
    ):
        """
        Initialize a new init instance.

        Args:
        search: The search parameter.
        """
        self._search = search

    def to_domain(self) -> SearchParams:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return SearchParams(query=self._search)


PaginationQuery = Annotated[PaginationRequest, Depends()]
SearchQuery = Annotated[SearchRequest, Depends()]
