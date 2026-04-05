"""
FastAPI API module.
"""

from typing import Any

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
