from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.exceptions import TournamentManagerError
from src.domain.exceptions.error_codes import GenericErrorCodes


async def tournament_manager_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, TournamentManagerError):
        raise exc
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    # Sanitize errors to ensure they are JSON serializable
    sanitized_errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "type": error.get("type"),
        }
        sanitized_errors.append(error_dict)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "code": GenericErrorCodes.VALIDATION_ERROR,
                "message": "Invalid request payload",
                "details": sanitized_errors,
            }
        },
    )
