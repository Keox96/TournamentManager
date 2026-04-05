# Generic Error Codes
"""
Domain exceptions defining error conditions and codes.
"""


class GenericErrorCodes:
    """
    Error code definitions for generic.
    """

    UNKNOWN_ERROR = "00000"
    INVALID_INPUT = "00001"
    DATABASE_ERROR = "00002"
    EXTERNAL_API_ERROR = "00003"
    UNAUTHORIZED = "00004"
    FORBIDDEN = "00005"
    NOT_FOUND = "00006"
    VALIDATION_ERROR = "00007"
    INVALID_SORT_FORMAT = "00008"


# Tournament Error Codes
class TournamentErrorCodes:
    """
    Error code definitions for tournament.
    """

    TOURNAMENT_NOT_FOUND = "10000"
    TOURNAMENT_ALREADY_EXISTS = "10001"
    INVALID_TOURNAMENT_DATA = "10002"
    UNAUTHORIZED_ACCESS = "10003"
    TOURNAMENT_FULL = "10004"
    TOURNAMENT_ALREADY_OPEN = "10005"
    TOURNAMENT_ALREADY_STARTED = "10006"
