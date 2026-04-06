"""
Domain repository interfaces and query helper classes.
"""

from abc import abstractmethod

from src.domain.entities.players import Player, PlayerFilters, PlayerSortField
from src.domain.repositories.base_repository import AbstractRepository


class AbstractPlayerRepository(
    AbstractRepository[Player, PlayerFilters, PlayerSortField]
):
    @abstractmethod
    async def get_by_username(self, username: str) -> Player | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Player | None: ...
