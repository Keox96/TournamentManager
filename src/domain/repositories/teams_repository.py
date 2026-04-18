"""
Domain repository interfaces and query helper classes.
"""

import uuid
from abc import abstractmethod

from src.domain.entities.teams import Team, TeamFilters, TeamPlayer, TeamSortField
from src.domain.repositories.base_repository import AbstractRepository


class AbstractTeamRepository(AbstractRepository[Team, TeamFilters, TeamSortField]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Team | None: ...

    @abstractmethod
    async def get_by_tag(self, tag: str) -> Team | None: ...

    @abstractmethod
    async def save_team_membership(self, team_membership: TeamPlayer) -> Team: ...

    @abstractmethod
    async def delete_team_membership(
        self, team_id: uuid.UUID, player_id: uuid.UUID
    ) -> None: ...
