"""
Database infrastructure module.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.teams import Team, TeamFilters, TeamSortField
from src.domain.repositories.teams_repository import AbstractTeamRepository
from src.infrastructure.database.models import TeamModel
from src.infrastructure.database.repositories.base_repository import SqlBaseRepository


class SqlTeamRepository(
    SqlBaseRepository[Team, TeamModel, TeamFilters, TeamSortField],
    AbstractTeamRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model_class(self) -> type[TeamModel]:
        return TeamModel

    @property
    def sort_field_map(self) -> dict[TeamSortField, Any]:
        return {
            TeamSortField.CREATED_AT: TeamModel.created_at,
            TeamSortField.NAME: TeamModel.name,
            TeamSortField.TAG: TeamModel.tag,
        }

    @property
    def search_fields(self) -> list[Any]:
        return [
            TeamModel.name,
            TeamModel.tag,
            TeamModel.description,
        ]

    def to_domain(self, model: TeamModel) -> Team:
        return TeamModel.to_domain(model)

    def from_domain(self, entity: Team) -> TeamModel:
        return TeamModel.from_domain(entity)

    # CRUD operations
    async def get_by_name(self, name: str) -> Team | None:
        query = select(TeamModel).where(TeamModel.name == name)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def get_by_tag(self, tag: str) -> Team | None:
        query = select(TeamModel).where(TeamModel.tag == tag)
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None
