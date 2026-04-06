"""
Domain entity definitions for the tournament manager.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from typing import TYPE_CHECKING

from src.domain.entities import BaseEntity
from src.domain.exceptions.generic_exceptions import EntityValidationError
from src.domain.utils.enums import TeamRole

if TYPE_CHECKING:
    import uuid

    from src.domain.entities.matchs import MatchTeam
    from src.domain.entities.players import Player
    from src.domain.entities.tournaments import TournamentTeam


@dataclass
class TeamPlayer(BaseEntity):
    """
    Represents a player's membership within a team, including their role and stats.
    """

    _: KW_ONLY
    player_id: uuid.UUID
    team_id: uuid.UUID
    role: TeamRole = TeamRole.PLAYER
    rank: int | None = None
    score: int = 0
    player: Player | None = None
    team: Team | None = None

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if self.score < 0:
            raise EntityValidationError(message="score cannot be negative")


@dataclass
class Team(BaseEntity):
    """
    Represents a competitive team that can register for tournaments.
    """

    _: KW_ONLY
    id: uuid.UUID
    name: str
    tag: str
    logo_url: str | None = None
    description: str | None = None
    members: list[TeamPlayer] = field(default_factory=list)
    tournament_entries: list[TournamentTeam] = field(default_factory=list)
    match_participations: list[MatchTeam] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if not self.name:
            raise EntityValidationError(message="name cannot be empty")
        if not self.tag:
            raise EntityValidationError(message="tag cannot be empty")

    @property
    def captain(self) -> TeamPlayer | None:
        """
        Return whether the captain condition is met.

        Returns:
        The result of the operation.
        """
        return next((m for m in self.members if m.role == TeamRole.CAPTAIN), None)
