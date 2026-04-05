"""
Domain exceptions defining error conditions and codes.
"""

from typing import Any


class TournamentManagerError(Exception):
    """Erreur de base de l'application."""

    http_status = 500

    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize a new init instance.

        Args:
        code: The code parameter.
        message: The message parameter.
        details: The details parameter.
        """
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundError(TournamentManagerError):
    """Ressource introuvable."""

    http_status = 404


class ValidationError(TournamentManagerError):
    """Données invalides."""

    http_status = 422


class ConflictError(TournamentManagerError):
    """Conflit de données (doublon, état incompatible)."""

    http_status = 409


class UnauthorizedError(TournamentManagerError):
    """Accès non autorisé."""

    http_status = 401


class ForbiddenError(TournamentManagerError):
    """Accès interdit."""

    http_status = 403


class BadRequestError(TournamentManagerError):
    """Requête mal formée."""

    http_status = 400
