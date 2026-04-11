"""
Domain exceptions defining error conditions and codes.
"""

from typing import Any

from src.domain.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from src.domain.exceptions.error_codes import TeamErrorCodes


class TeamNotFoundError(NotFoundError):
    """
    Exception raised when team not found conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamErrorCodes.TEAM_NOT_FOUND,
            message=f"Team with id '{details['id']}' not found",
            details=details,
        )


class TeamNameAlreadyExistsError(ConflictError):
    """
    Exception raised when team name already exists conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamErrorCodes.TEAM_NAME_EXISTS,
            message=f"Team with name '{details['name']}' already exists",
            details=details,
        )


class TeamTagAlreadyExistsError(ConflictError):
    """
    Exception raised when team tag already exists conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamErrorCodes.TEAM_TAG_EXISTS,
            message=f"Team with tag '{details['tag']}' already exists",
            details=details,
        )


class InvalidTeamDataError(BadRequestError):
    """
    Exception raised when invalid team data conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TeamErrorCodes.INVALID_TEAM_DATA,
            message="Invalid team data",
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
            code=TeamErrorCodes.UNAUTHORIZED_ACCESS,
            message="Unauthorized access",
            details=details,
        )
