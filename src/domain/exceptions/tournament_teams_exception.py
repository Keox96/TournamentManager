from typing import Any

from src.domain.exceptions import BadRequestError
from src.domain.exceptions.error_codes import TournamentTeamErrorCodes


class TournamentTeamNotEnoughPlayersError(BadRequestError):
    """
    Exception raised when team has not enough players for the tournament.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentTeamErrorCodes.TOURNAMENT_TEAM_NOT_ENOUGH_PLAYERS,
            message="Team has not enough players for the tournament",
            details=details,
        )


class TournamentPlayerAlreadyRegisteredError(BadRequestError):
    """
    Exception raised when a player in a team is already registered for the tournament.
    """

    def __init__(self, *, details: dict[str, Any] | None = None):
        """
        Initialize a new init instance.

        Args:
        details: The details parameter.
        """
        super().__init__(
            code=TournamentTeamErrorCodes.TOURNAMENT_TEAM_PLAYER_ALREADY_SUBSCRIBED,
            message="Player in a team is already registered for the tournament",
            details=details,
        )
