"""
Domain entity definitions for the tournament manager.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from typing import TYPE_CHECKING

from src.domain.entities import BaseEntity

if TYPE_CHECKING:
    import uuid

    from src.domain.entities.matchs import MatchPlayer
    from src.domain.entities.teams import TeamPlayer


@dataclass
class Player(BaseEntity):
    """
    Represents a registered user who can join teams and participate in tournaments.
    """

    _: KW_ONLY
    id: uuid.UUID
    username: str
    display_name: str
    email: str | None = None
    icon_url: str | None = None
    team_memberships: list[TeamPlayer] = field(default_factory=list)
    match_performances: list[MatchPlayer] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Validate and normalize object state after initialization.
        """
        if not self.username:
            raise ValueError("username cannot be empty")
        if not self.display_name:
            raise ValueError("display_name cannot be empty")
