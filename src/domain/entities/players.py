"""
Domain entity definitions for the tournament manager.
"""

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from src.domain.entities import BaseEntity
from src.domain.exceptions.generic_exceptions import EntityValidationError

if TYPE_CHECKING:
    import uuid
    from datetime import datetime

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
            raise EntityValidationError(message="username cannot be empty")
        if not self.display_name:
            raise EntityValidationError(message="display_name cannot be empty")


class PlayerSortField(StrEnum):
    """
    Enumeration of valid player sort values.
    """

    CREATED_AT = "created_at"
    USERNAME = "username"
    DISPLAY_NAME = "display_name"
    EMAIL = "email"


@dataclass
class PlayerFilters:
    """
    Filter container for player.
    """

    username: str | None = None
    display_name_like: str | None = None
    email_like: str | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None
