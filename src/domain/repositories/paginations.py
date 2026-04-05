"""
Domain repository interfaces and query helper classes.
"""

from dataclasses import dataclass


@dataclass
class PaginatedResult[T]:
    """
    Model representing a paginated result.
    """

    items: list[T]
    total: int
