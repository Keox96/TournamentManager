"""
Domain exceptions defining error conditions and codes.
"""

from src.domain.exceptions import ValidationError
from src.domain.exceptions.error_codes import GenericErrorCodes


class InvalidSortFormatError(ValidationError):
    """
    Exception raised when invalid sort format conditions occur.
    """

    def __init__(self, message: str, details: dict[str, str] | None = None):
        """
        Initialize a new init instance.

        Args:
        message: The message parameter.
        details: The details parameter.
        """
        super().__init__(
            code=GenericErrorCodes.INVALID_SORT_FORMAT,
            message=message,
            details=details,
        )


class EntityValidationError(ValidationError):
    """
    Exception raised when an entity fails validation.
    """

    def __init__(self, message: str, details: dict[str, str] | None = None):
        """
        Initialize a new init instance.

        Args:
        message: The message parameter.
        details: The details parameter.
        """
        super().__init__(
            code=GenericErrorCodes.VALIDATION_ERROR,
            message=message,
            details=details,
        )
