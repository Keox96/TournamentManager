import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.tournaments import (
    Tournament,
    TournamentFilters,
    TournamentSortField,
    TournamentTeam,
)
from src.domain.repositories.tournaments_repository import AbstractTournamentRepository
from src.domain.utils.enums import TournamentStatus
from src.infrastructure.database.models import (
    TeamModel,
    TeamPlayerModel,
    TournamentModel,
    TournamentTeamModel,
)
from src.infrastructure.database.repositories.base_repository import SqlBaseRepository


class SqlTournamentRepository(
    SqlBaseRepository[
        Tournament, TournamentModel, TournamentFilters, TournamentSortField
    ],
    AbstractTournamentRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model_class(self) -> type[TournamentModel]:
        return TournamentModel

    @property
    def sort_field_map(self) -> dict[TournamentSortField, Any]:
        return {
            TournamentSortField.CREATED_AT: TournamentModel.created_at,
            TournamentSortField.START_DATE: TournamentModel.start_date,
            TournamentSortField.NAME: TournamentModel.name,
            TournamentSortField.STATUS: TournamentModel.status,
        }

    @property
    def search_fields(self) -> list[Any]:
        return [
            TournamentModel.name,
            TournamentModel.game,
            TournamentModel.description,
        ]

    @property
    def load_options(self) -> list[Any]:
        return [
            selectinload(TournamentModel.registered_teams)
            .selectinload(TournamentTeamModel.team)
            .selectinload(TeamModel.members)
            .selectinload(TeamPlayerModel.player),
        ]

    def to_domain(self, model: TournamentModel) -> Tournament:
        return TournamentModel.to_domain(model)

    def from_domain(self, entity: Tournament) -> TournamentModel:
        return TournamentModel.from_domain(entity)

    # Specific CRUD operations

    async def get_by_name_and_guild(
        self, name: str, guild_id: int
    ) -> Tournament | None:
        query = (
            select(TournamentModel)
            .where(
                TournamentModel.name == name,
                TournamentModel.guild_id == guild_id,
            )
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    # Custom operations

    async def open_tournament(self, tournament_id: uuid.UUID) -> Tournament:
        query = (
            select(TournamentModel)
            .where(TournamentModel.id == tournament_id)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one()
        model.status = TournamentStatus.OPEN
        await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self.to_domain(model)

    async def start_tournament(self, tournament_id: uuid.UUID) -> Tournament:
        query = (
            select(TournamentModel)
            .where(TournamentModel.id == tournament_id)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one()
        model.status = TournamentStatus.IN_PROGRESS
        await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self.to_domain(model)

    async def save_tournament_membership(
        self, tournament_membership: TournamentTeam
    ) -> Tournament:
        model = TournamentTeamModel.from_domain(tournament_membership)
        merged = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged)

        query = (
            select(TournamentModel)
            .where(TournamentModel.id == model.team_id)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        team_model = result.scalar_one()
        return self.to_domain(team_model)

    async def delete_tournament_membership(self, tournament_id: uuid.UUID, team_id: uuid.UUID) -> None:
        model = await self.session.get(TournamentTeamModel, (tournament_id, team_id))
        if model:
            await self.session.delete(model)
