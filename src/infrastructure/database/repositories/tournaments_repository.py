import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.tournaments import (
    Tournament,
    TournamentFilters,
    TournamentSortField,
)
from src.domain.repositories.tournaments_repository import AbstractTournamentRepository
from src.domain.utils.enums import TournamentStatus
from src.infrastructure.database.models import TournamentModel
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

    def to_domain(self, model: TournamentModel) -> Tournament:
        return TournamentModel.to_domain(model)

    def from_domain(self, entity: Tournament) -> TournamentModel:
        return TournamentModel.from_domain(entity)

    # Specific CRUD operations

    async def get_by_name_and_guild(
        self, name: str, guild_id: int
    ) -> Tournament | None:
        query = select(TournamentModel).where(
            TournamentModel.name == name,
            TournamentModel.guild_id == guild_id,
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    # Custom operations

    async def open_tournament(self, tournament_id: uuid.UUID) -> Tournament:
        query = select(TournamentModel).where(TournamentModel.id == tournament_id)
        result = await self.session.execute(query)
        model = result.scalar_one()
        model.status = TournamentStatus.OPEN
        await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self.to_domain(model)

    async def start_tournament(self, tournament_id: uuid.UUID) -> Tournament:
        query = select(TournamentModel).where(TournamentModel.id == tournament_id)
        result = await self.session.execute(query)
        model = result.scalar_one()
        model.status = TournamentStatus.IN_PROGRESS
        await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(model)
        return self.to_domain(model)
