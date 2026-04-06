"""
Database infrastructure module.
"""

from abc import abstractmethod
from dataclasses import fields as dataclass_fields
from enum import StrEnum
from typing import Any

from sqlalchemy import Select, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions.generic_exceptions import InvalidSortFormatError
from src.domain.repositories.base_repository import AbstractRepository
from src.domain.repositories.filters import (
    PaginationParams,
    SearchParams,
    SortOrder,
    SortParams,
)
from src.domain.repositories.paginations import PaginatedResult


class SqlBaseRepository[TEntity, TModel, TFilters, TSortField: StrEnum](
    AbstractRepository[TEntity, TFilters, TSortField]
):
    """
    Repository interface for sql base persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize a new init instance.

        Args:
        session: The session parameter.
        """
        self.session = session

    @property
    @abstractmethod
    def model_class(self) -> type[TModel]:
        """
        Return whether the model class condition is met.

        Returns:
        The result of the operation.
        """
        ...

    @property
    @abstractmethod
    def sort_field_map(self) -> dict[TSortField, Any]:
        """
        Return whether the sort field map condition is met.

        Returns:
        The result of the operation.
        """
        ...

    @property
    def search_fields(self) -> list[Any]:
        """
        Colonnes sur lesquelles appliquer la recherche full-text.
        Chaque repository spécifique surcharge cette propriété.

        Example:
            return [TournamentModel.name, TournamentModel.game]
        """
        return []

    @abstractmethod
    def to_domain(self, model: TModel) -> TEntity:
        """
        Convert the object to domain.

        Args:
        model: The model parameter.

        Returns:
        The result of the operation.
        """
        ...

    @abstractmethod
    def from_domain(self, entity: TEntity) -> TModel:
        """
        Create an object from domain.

        Args:
        entity: The entity parameter.

        Returns:
        The result of the operation.
        """
        ...

    def _build_conditions(self, filters: TFilters) -> list[Any]:
        """
        Build the build conditions.

        Args:
        filters: The filters parameter.

        Returns:
        The result of the operation.
        """
        conditions: list[Any] = []

        for f in dataclass_fields(filters):  # type: ignore[arg-type]
            value = getattr(filters, f.name)
            if value is None:
                continue

            column_name = (
                f.name.removesuffix("_from")
                .removesuffix("_to")
                .removesuffix("_min")
                .removesuffix("_max")
                .removesuffix("_like")
            )
            column = getattr(self.model_class, column_name, None)
            if column is None:
                continue

            match f.name:
                case name if name.endswith("_from") or name.endswith("_min"):
                    conditions.append(column >= value)
                case name if name.endswith("_to") or name.endswith("_max"):
                    conditions.append(column <= value)
                case name if name.endswith("_like"):
                    conditions.append(column.ilike(f"%{value}%"))
                case _:
                    raw = value.value if hasattr(value, "value") else value
                    conditions.append(column == raw)

        return conditions

    def _build_search_condition(self, search: SearchParams) -> Any | None:
        """
        Construit un OR sur tous les champs définis dans search_fields.
        Retourne None si pas de query ou pas de champs définis.
        """
        if not search.query or not self.search_fields:
            return None

        term = f"%{search.query}%"
        return or_(*[col.ilike(term) for col in self.search_fields])

    def _build_order_clauses(self, sort: SortParams[TSortField]) -> list[Any]:
        """
        Build the build order clauses.

        Args:
        sort: The sort parameter.

        Returns:
        The result of the operation.
        """
        if not sort.sorts:
            return [asc(self.model_class.created_at)]  # type: ignore[attr-defined]

        if self.sort_field_map is None:
            raise NotImplementedError("sort_field_map must be defined to use sorting")

        for s in sort.sorts:
            if s.field not in self.sort_field_map:
                valid_fields = list(self.sort_field_map.keys())
                raise InvalidSortFormatError(
                    message=f"Invalid sort field '{s.field}'. Valid fields: {valid_fields}.",
                    details={"invalid_field": s.field},
                )

        return [
            asc(self.sort_field_map[s.field])
            if s.order == SortOrder.ASC
            else desc(self.sort_field_map[s.field])
            for s in sort.sorts
        ]

    def _get_list_query(
        self,
        filters: TFilters,
        sort: SortParams[TSortField],
        search: SearchParams,
    ) -> Select[Any]:
        """
        Execute get list query.

        Args:
        filters: The filters parameter.
        sort: The sort parameter.
        search: The search parameter.

        Returns:
        The result of the operation.
        """
        conditions = self._build_conditions(filters)
        order_clauses = self._build_order_clauses(sort)

        search_condition = self._build_search_condition(search)
        if search_condition is not None:
            conditions.append(search_condition)

        return select(self.model_class).where(*conditions).order_by(*order_clauses)

    async def get_by_id(self, entity_id: Any) -> TEntity | None:
        """Retrieve an entity by its unique identifier.

        Args:
            entity_id: The entity identifier.

        Returns:
            The entity instance or None if not found.
        """
        query = select(self.model_class).where(self.model_class.id == entity_id)  # type: ignore[attr-defined]
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def save(self, entity: TEntity) -> TEntity:
        """
        Persist the given entity.

        Args:
            entity: The entity parameter.

        Returns:
            The result of the operation.
        """
        model = self.from_domain(entity)
        merged = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged)
        return self.to_domain(merged)

    async def update(self, entity: TEntity, updated_data: dict[str, Any]) -> TEntity:
        """
        Update the given entity.

        Args:
            entity: The entity parameter.
            updated_data: The data to update the entity with.

        Returns:
            The result of the operation.
        """
        for key, value in updated_data.items():
            setattr(entity, key, value)
        return await self.save(entity)

    async def delete(self, entity_id: Any) -> None:
        """
        Execute delete.

        Args:
            entity_id: The entity_id parameter.
        """
        query = select(self.model_class).where(self.model_class.id == entity_id)  # type: ignore[attr-defined]
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model:
            await self.session.delete(model)

    async def list(
        self,
        filters: TFilters,
        pagination: PaginationParams,
        sort: SortParams[TSortField],
        search: SearchParams,
    ) -> PaginatedResult[TEntity]:
        """
        Execute list.

        Args:
            filters: The filters parameter.
            pagination: The pagination parameter.
            sort: The sort parameter.
            search: The search parameter.

        Returns:
            The result of the operation.
        """
        query = self._get_list_query(filters, sort, search)

        # ── COUNT ─────────────────────────────────────────────────────────
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # ── PAGINATION ────────────────────────────────────────────────────
        paginated_query = query.offset((pagination.page - 1) * pagination.size).limit(
            pagination.size
        )
        result = await self.session.execute(paginated_query)
        models = result.scalars().all()

        return PaginatedResult(
            items=[self.to_domain(m) for m in models],
            total=total,
        )
