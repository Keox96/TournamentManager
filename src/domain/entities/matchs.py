"""
Domain entity definitions for the tournament manager.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from typing import TYPE_CHECKING

from src.domain.entities import BaseEntity
from src.domain.exceptions.generic_exceptions import EntityValidationError
from src.domain.utils.enums import MatchStatus

if TYPE_CHECKING:
    import uuid

    from src.domain.entities.players import Player
    from src.domain.entities.teams import Team


@dataclass
class MatchTeam(BaseEntity):
    """
    Represents a team's participation in a specific match with their result.
    """

    _: KW_ONLY
    match_id: uuid.UUID
    team_id: uuid.UUID
    score: int = 0
    rank: int | None = None
    match: Match | None = None
    team: Team | None = None

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if self.score < 0:
            raise EntityValidationError(message="score cannot be negative")


@dataclass
class MatchPlayer(BaseEntity):
    """
    Represents a player's individual performance in a specific match.
    """

    _: KW_ONLY
    match_id: uuid.UUID
    player_id: uuid.UUID
    score: int = 0
    rank: int | None = None
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    match: Match | None = None
    player: Player | None = None

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if self.score < 0:
            raise EntityValidationError(message="score cannot be negative")
        if self.kills < 0:
            raise EntityValidationError(message="kills cannot be negative")
        if self.deaths < 0:
            raise EntityValidationError(message="deaths cannot be negative")
        if self.assists < 0:
            raise EntityValidationError(message="assists cannot be negative")


@dataclass
class Match(BaseEntity):
    """
    Represents a single match between two (or more) teams within a tournament round.
    """

    _: KW_ONLY
    id: uuid.UUID
    tournament_id: uuid.UUID
    status: MatchStatus
    round: int
    participants: list[MatchTeam] = field(default_factory=list)
    player_performances: list[MatchPlayer] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if self.round < 1:
            raise EntityValidationError(message="round must be >= 1")

    @property
    def winner(self) -> MatchTeam | None:
        """
        Return whether the winner condition is met.

        Returns:
        The result of the operation.
        """
        if self.status != MatchStatus.COMPLETED:
            return None
        return next((p for p in self.participants if p.rank == 1), None)
