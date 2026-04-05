"""
Domain utility types and helper functions.
"""

from enum import StrEnum


class TournamentStatus(StrEnum):
    """
    Model representing a tournament status.
    """

    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TournamentMode(StrEnum):
    """
    Model representing a tournament mode.
    """

    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"


class TeamRole(StrEnum):
    """
    Model representing a team role.
    """

    PLAYER = "player"
    CAPTAIN = "captain"
    SUBSTITUTE = "substitute"


class MatchStatus(StrEnum):
    """
    Model representing a match status.
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
