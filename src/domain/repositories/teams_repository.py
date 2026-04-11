"""
Domain repository interfaces and query helper classes.
"""

from abc import abstractmethod

from src.domain.entities.teams import Team, TeamFilters, TeamSortField
from src.domain.repositories.base_repository import AbstractRepository


class AbstractTeamRepository(AbstractRepository[Team, TeamFilters, TeamSortField]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Team | None: ...

    @abstractmethod
    async def get_by_tag(self, tag: str) -> Team | None: ...
