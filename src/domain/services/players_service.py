"""
Domain service layer containing business logic.
"""

import uuid

from src.domain.entities.players import Player, PlayerFilters, PlayerSortField
from src.domain.exceptions.players_exceptions import (
    PlayerEmailAlreadyExistsError,
    PlayerNotFoundError,
    PlayerUsernameAlreadyExistsError,
)
from src.domain.repositories.filters import PaginationParams, SearchParams, SortParams
from src.domain.repositories.paginations import PaginatedResult
from src.domain.repositories.players_repository import AbstractPlayerRepository


class PlayerService:
    def __init__(self, repository: AbstractPlayerRepository) -> None:
        self.repository = repository

    # CRUD operations
    async def list_players(
        self,
        filters: PlayerFilters,
        pagination: PaginationParams,
        sort: SortParams[PlayerSortField],
        search: SearchParams,
    ) -> PaginatedResult[Player]:
        return await self.repository.list(filters, pagination, sort, search)

    async def get_player_by_id(self, player_id: uuid.UUID) -> Player:
        player = await self.repository.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(details={"id": str(player_id)})
        return player

    async def create_player(self, player: Player) -> Player:
        existing = await self.repository.get_by_username(player.username)
        if existing is not None:
            raise PlayerUsernameAlreadyExistsError(
                details={"username": player.username}
            )
        return await self.repository.save(player)

    async def update_player(self, player_id: uuid.UUID, player: Player) -> Player:
        existing = await self.repository.get_by_id(player_id)
        # Check if player exists
        if existing is None:
            raise PlayerNotFoundError(details={"id": str(player_id)})
        # Check if username is changing and if new username already exists
        if (
            player.username != existing.username
            and await self.repository.get_by_username(player.username) is not None
        ):
            raise PlayerUsernameAlreadyExistsError(
                details={"username": player.username}
            )
        # Check if email is changing and if new email already exists
        if (
            player.email != existing.email
            and player.email is not None
            and await self.repository.get_by_email(player.email) is not None
        ):
            raise PlayerEmailAlreadyExistsError(details={"email": player.email})
        # Update data
        updated_data = {
            "username": player.username,
            "display_name": player.display_name,
            "email": player.email,
            "icon_url": player.icon_url,
        }
        return await self.repository.update(existing, updated_data)

    async def delete_player(self, player_id: uuid.UUID) -> None:
        existing = await self.repository.get_by_id(player_id)
        if existing is None:
            raise PlayerNotFoundError(details={"id": str(player_id)})
        await self.repository.delete(player_id)

    # Custom operations
