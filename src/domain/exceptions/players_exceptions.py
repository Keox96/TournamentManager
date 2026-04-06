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
from src.domain.exceptions.error_codes import PlayerErrorCodes


class PlayerNotFoundError(NotFoundError):
    """
    Exception raised when player not found conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=PlayerErrorCodes.PLAYER_NOT_FOUND,
            message=f"Player with id '{details['id']}' not found",
            details=details,
        )


class PlayerUsernameAlreadyExistsError(ConflictError):
    """
    Exception raised when player already exists conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=PlayerErrorCodes.PLAYER_USERNAME_EXISTS,
            message=f"Player with username '{details['username']}' already exists",
            details=details,
        )


class PlayerEmailAlreadyExistsError(ConflictError):
    """
    Exception raised when player email already exists conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=PlayerErrorCodes.PLAYER_EMAIL_EXISTS,
            message=f"Player with email '{details['email']}' already exists",
            details=details,
        )


class InvalidPlayerDataError(BadRequestError):
    """
    Exception raised when invalid player data conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=PlayerErrorCodes.INVALID_PLAYER_DATA,
            message="Invalid player data",
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
            code=PlayerErrorCodes.UNAUTHORIZED_ACCESS,
            message="Unauthorized access",
            details=details,
        )
