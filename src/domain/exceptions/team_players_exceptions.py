"""
Domain exceptions defining error conditions and codes.
"""

from typing import Any

from src.domain.exceptions import (
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from src.domain.exceptions.error_codes import TeamPlayerErrorCodes


class TeamPlayerNotFoundError(NotFoundError):
    """ """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamPlayerErrorCodes.TEAM_PLAYER_NOT_FOUND,
            message=f"Link between Team with id '{details['team_id']}' and Player with id '{details['player_id']}' not found",
            details=details,
        )


class TeamPlayerAlreadyExistsError(ConflictError):
    """
    Exception raised when the link between the team and the player already exists conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamPlayerErrorCodes.TEAM_PLAYER_EXISTS,
            message=f"Link between Team with id '{details['team_id']}' and Player with id '{details['player_id']}' already exists",
            details=details,
        )


class UnauthorizedAccessError(UnauthorizedError):
    """
    Exception raised when unauthorized access conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamPlayerErrorCodes.UNAUTHORIZED_ACCESS,
            message="Unauthorized access",
            details=details,
        )


class TeamCaptainAlreadyExistsError(ConflictError):
    """
    Exception raised when unauthorized access conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamPlayerErrorCodes.TEAM_CAPTAIN_EXISTS,
            message=f"Team with id '{details['team_id']}' has already a captain",
            details=details,
        )
