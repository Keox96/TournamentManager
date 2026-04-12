"""
Database infrastructure module.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.teams import Team, TeamFilters, TeamPlayer, TeamSortField
from src.domain.repositories.teams_repository import AbstractTeamRepository
from src.infrastructure.database.models import TeamModel, TeamPlayerModel
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

    @property
    def load_options(self) -> list[Any]:
        return [selectinload(TeamModel.members).selectinload(TeamPlayerModel.player)]

    def to_domain(self, model: TeamModel) -> Team:
        return TeamModel.to_domain(model)

    def from_domain(self, entity: Team) -> TeamModel:
        return TeamModel.from_domain(entity)

    # CRUD operations
    async def get_by_name(self, name: str) -> Team | None:
        query = (
            select(TeamModel).where(TeamModel.name == name).options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def get_by_tag(self, tag: str) -> Team | None:
        query = (
            select(TeamModel).where(TeamModel.tag == tag).options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def save_membership(self, membership: TeamPlayer) -> Team:
        model = TeamPlayerModel.from_domain(membership)
        merged = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged)

        query = (
            select(TeamModel)
            .where(TeamModel.id == model.team_id)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        team_model = result.scalar_one()
        return self.to_domain(team_model)

    async def delete_membership(self, team_id: uuid.UUID, player_id: uuid.UUID) -> None:
        model = await self.session.get(TeamPlayerModel, (player_id, team_id))
        if model:
            await self.session.delete(model)
