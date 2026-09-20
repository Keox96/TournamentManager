"""
Domain repository interfaces and query helper classes.
"""

import uuid
from abc import abstractmethod

from src.domain.entities.matchs import (
    Match,
    MatchFilters,
    MatchPlayer,
    MatchSortField,
    MatchTeam,
)
from src.domain.repositories.base_repository import AbstractRepository
from src.domain.utils.enums import MatchStatus


class AbstractMatchRepository(
    AbstractRepository[Match, MatchFilters, MatchSortField]
):
    @abstractmethod
    async def create_match(self, match: Match) -> Match: ...

    @abstractmethod
    async def get_by_tournament(self, tournament_id: uuid.UUID) -> list[Match]: ...

    @abstractmethod
    async def get_by_tournament_and_round(
        self, tournament_id: uuid.UUID, round_number: int
    ) -> list[Match]: ...

    @abstractmethod
    async def update_match_status(
        self, match_id: uuid.UUID, status: MatchStatus
    ) -> Match | None: ...

    @abstractmethod
    async def update_match_score(
        self, match_id: uuid.UUID, team_id: uuid.UUID, score: int
    ) -> MatchTeam | None: ...

    @abstractmethod
    async def save_match_result(
        self,
        match_id: uuid.UUID,
        team_scores: dict[uuid.UUID, int],
        player_scores: dict[uuid.UUID, MatchPlayer],
    ) -> Match | None: ...

    @abstractmethod
    async def save_match_team(self, participation: MatchTeam) -> MatchTeam: ...

    @abstractmethod
    async def save_match_player(self, performance: MatchPlayer) -> MatchPlayer: ...

    @abstractmethod
    async def delete_match(self, match_id: uuid.UUID) -> None: ...
