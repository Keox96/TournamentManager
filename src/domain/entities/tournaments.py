"""
Domain entity definitions for the tournament manager.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from src.domain.entities import BaseEntity
from src.domain.exceptions.generic_exceptions import EntityValidationError
from src.domain.utils.enums import TournamentMode, TournamentStatus

if TYPE_CHECKING:
    import uuid
    from datetime import datetime

    from src.domain.entities.matchs import Match
    from src.domain.entities.teams import Team


@dataclass
class TournamentTeam(BaseEntity):
    """
    Represents a team's enrollment in a specific tournament along with their standings.
    """

    _: KW_ONLY
    tournament_id: uuid.UUID
    team_id: uuid.UUID
    score: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    rank: int | None = None
    tournament: Tournament | None = None
    team: Team | None = None

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        for attr in ("score", "wins", "losses", "draws"):
            if getattr(self, attr) < 0:
                raise EntityValidationError(message=f"{attr} cannot be negative")

    @property
    def games_played(self) -> int:
        """
        Return whether the games played condition is met.

        Returns:
        The result of the operation.
        """
        return self.wins + self.losses + self.draws


@dataclass
class Tournament(BaseEntity):
    """
    Aggregate root representing a tournament event hosted in a Discord guild.
    """

    _: KW_ONLY
    id: uuid.UUID
    guild_id: int
    name: str
    game: str
    start_date: datetime | None = None
    mode: TournamentMode = TournamentMode.SINGLE_ELIMINATION
    status: TournamentStatus = TournamentStatus.OPEN
    min_players_per_team: int = 1
    max_teams: int = 8
    description: str | None = None
    best_of: int | None = None
    end_date: datetime | None = None
    registered_teams: list[TournamentTeam] = field(default_factory=list)
    matches: list[Match] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if not self.name:
            raise EntityValidationError(message="name cannot be empty")
        if self.min_players_per_team < 1:
            raise EntityValidationError(message="min_players_per_team must be >= 1")
        if self.max_teams < 2:
            raise EntityValidationError(message="max_teams must be >= 2")
        if self.best_of is not None and self.best_of % 2 == 0:
            raise EntityValidationError(message="best_of must be an odd number")

    @property
    def is_open_for_registration(self) -> bool:
        """
        Return whether the is open for registration condition is met.

        Returns:
        The result of the operation.
        """
        return self.status == TournamentStatus.OPEN

    @property
    def is_full(self) -> bool:
        """
        Return whether the is full condition is met.

        Returns:
        The result of the operation.
        """
        return len(self.registered_teams) >= self.max_teams


class TournamentSortField(StrEnum):
    """
    Enumeration of valid tournament sort values.
    """

    CREATED_AT = "created_at"
    START_DATE = "start_date"
    NAME = "name"
    STATUS = "status"


@dataclass
class TournamentFilters:
    """
    Filter container for tournament.
    """

    guild_id: int | None = None
    status: TournamentStatus | None = None
    mode: TournamentMode | None = None
    game_like: str | None = None
    name_like: str | None = None
    max_teams_min: int | None = None
    max_teams_max: int | None = None
    min_players_per_team_min: int | None = None
    min_players_per_team_max: int | None = None
    start_date_from: datetime | None = None
    start_date_to: datetime | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None
