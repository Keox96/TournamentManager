"""
Domain repository interfaces and query helper classes.
"""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any
from uuid import UUID

from src.domain.repositories.filters import PaginationParams, SearchParams, SortParams
from src.domain.repositories.paginations import PaginatedResult


class AbstractRepository[TEntity, TFilters, TSortField: StrEnum](ABC):
    """Repository interface for abstract persistence operations."""

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> TEntity | None:
        """Retrieve an entity by its unique identifier.

        Args:
            entity_id: The entity identifier.

        Returns:
            The entity or None if it does not exist.
        """
        ...

    @abstractmethod
    async def save(self, entity: TEntity) -> TEntity:
        """Persist the given entity.

        Args:
            entity: The entity to save.

        Returns:
            The saved entity.
        """
        ...

    @abstractmethod
    async def update(self, entity: TEntity, updated_data: dict[str, Any]) -> TEntity:
        """Update the given entity.

        Args:
            entity: The entity to update.
            updated_data: The data to update the entity with.

        Returns:
            The updated entity.
        """
        ...

    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """Delete an entity by its unique identifier.

        Args:
            entity_id: The entity identifier.
        """
        ...

    @abstractmethod
    async def list(
        self,
        filters: TFilters,
        pagination: PaginationParams,
        sort: SortParams[TSortField],
        search: SearchParams,
    ) -> PaginatedResult[TEntity]:
        """List entities using filters, sorting, pagination, and search criteria.

        Args:
            filters: The filtering parameters.
            pagination: The pagination parameters.
            sort: The sorting parameters.
            search: The search parameters.

        Returns:
            A paginated result containing matching entities.
        """
        ...
