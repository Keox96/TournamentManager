"""
Domain repository interfaces and query helper classes.
"""

from dataclasses import dataclass, field
from enum import StrEnum


class SortOrder(StrEnum):
    """
    Model representing a sort order.
    """

    ASC = "asc"
    DESC = "desc"


@dataclass
class SortParam[TSortField: StrEnum]:
    """
    Model representing a sort param.
    """

    field: TSortField
    order: SortOrder = SortOrder.DESC


@dataclass
class SortParams[TSortField: StrEnum]:
    """
    Container for sort parameters.
    """

    sorts: list[SortParam[TSortField]] | None = field(default_factory=list)


@dataclass
class PaginationParams:
    """
    Container for pagination parameters.
    """

    page: int = 1
    size: int = 20


@dataclass
class SearchParams:
    """
    Container for search parameters.
    """

    query: str | None = None
