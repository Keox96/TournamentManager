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
from src.domain.exceptions.error_codes import TournamentErrorCodes


class TournamentNotFoundError(NotFoundError):
    """
    Exception raised when tournament not found conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.TOURNAMENT_NOT_FOUND,
            message=f"Tournament with id '{details['id']}' not found",
            details=details,
        )


class TournamentAlreadyExistsError(ConflictError):
    """
    Exception raised when tournament already exists conditions occur.
    """

    def __init__(self, *, details: dict[str, Any]):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.TOURNAMENT_ALREADY_EXISTS,
            message=f"Tournament with name '{details['name']}' already exists in guild {details['guild_id']}",
            details=details,
        )


class InvalidTournamentDataError(BadRequestError):
    """
    Exception raised when invalid tournament data conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.INVALID_TOURNAMENT_DATA,
            message="Invalid tournament data",
            details=details,
        )


class TournamentNotDraftError(BadRequestError):
    """
    Exception raised when tournament not in draft status conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.TOURNAMENT_NOT_DRAFT,
            message="Tournament is not in draft status",
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
            code=TournamentErrorCodes.UNAUTHORIZED_ACCESS,
            message="Unauthorized access",
            details=details,
        )


class TournamentFullError(BadRequestError):
    """
    Exception raised when tournament full conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.TOURNAMENT_FULL,
            message="Tournament is full",
            details=details,
        )


class TournamentAlreadyOpenedError(BadRequestError):
    """
    Exception raised when tournament already opened conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.TOURNAMENT_ALREADY_OPEN,
            message="Tournament has already been opened",
            details=details,
        )


class TournamentAlreadyStartedError(BadRequestError):
    """
    Exception raised when tournament already started conditions occur.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentErrorCodes.TOURNAMENT_ALREADY_STARTED,
            message="Tournament has already started",
            details=details,
        )
