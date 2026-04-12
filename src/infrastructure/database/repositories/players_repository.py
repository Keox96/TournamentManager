"""
Database infrastructure module.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.players import Player, PlayerFilters, PlayerSortField
from src.domain.repositories.players_repository import AbstractPlayerRepository
from src.infrastructure.database.models import PlayerModel, TeamPlayerModel
from src.infrastructure.database.repositories.base_repository import SqlBaseRepository


class SqlPlayerRepository(
    SqlBaseRepository[Player, PlayerModel, PlayerFilters, PlayerSortField],
    AbstractPlayerRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model_class(self) -> type[PlayerModel]:
        return PlayerModel

    @property
    def sort_field_map(self) -> dict[PlayerSortField, Any]:
        return {
            PlayerSortField.CREATED_AT: PlayerModel.created_at,
            PlayerSortField.USERNAME: PlayerModel.username,
            PlayerSortField.DISPLAY_NAME: PlayerModel.display_name,
        }

    @property
    def search_fields(self) -> list[Any]:
        return [
            PlayerModel.username,
            PlayerModel.display_name,
            PlayerModel.email,
        ]

    @property
    def load_options(self) -> list[Any]:
        return [
            selectinload(PlayerModel.team_memberships).selectinload(
                TeamPlayerModel.team
            )
        ]

    def to_domain(self, model: PlayerModel) -> Player:
        return PlayerModel.to_domain(model)

    def from_domain(self, entity: Player) -> PlayerModel:
        return PlayerModel.from_domain(entity)

    # CRUD operations
    async def get_by_username(self, username: str) -> Player | None:
        query = (
            select(PlayerModel)
            .where(PlayerModel.username == username)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None

    async def get_by_email(self, email: str) -> Player | None:
        query = (
            select(PlayerModel)
            .where(PlayerModel.email == email)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        return self.to_domain(model) if model else None
