"""
FastAPI API module.
"""

from typing import Any

from fastapi import status
from pydantic import BaseModel, Field


class APIError(BaseModel):
    """
    Exception raised when api conditions occur.
    """

    code: str = Field(description="A unique error code identifying the type of error")
    message: str = Field(description="A human-readable message describing the error")
    details: dict[str, Any] | None = Field(
        default=None, description="Optional additional details about the error"
    )


class ErrorResponse(BaseModel):
    """
    Schema representing a error response payload.
    """

    error: APIError = Field(description="The error information")


COMMON_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}