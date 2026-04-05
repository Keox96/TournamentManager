import uuid
from abc import abstractmethod

from src.domain.entities.tournaments import (
    Tournament,
    TournamentFilters,
    TournamentSortField,
)
from src.domain.repositories.base_repository import AbstractRepository


class AbstractTournamentRepository(
    AbstractRepository[Tournament, TournamentFilters, TournamentSortField]
):
    @abstractmethod
    async def get_by_name_and_guild(
        self, name: str, guild_id: int
    ) -> Tournament | None: ...

    @abstractmethod
    async def open_tournament(self, tournament_id: uuid.UUID) -> Tournament: ...

    @abstractmethod
    async def start_tournament(self, tournament_id: uuid.UUID) -> Tournament: ...
