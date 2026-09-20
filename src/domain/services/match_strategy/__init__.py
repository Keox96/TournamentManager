from src.domain.services.match_strategy.double_elimination import (
    DoubleEliminationMatchStrategy,
)
from src.domain.services.match_strategy.round_robin import RoundRobinMatchStrategy
from src.domain.services.match_strategy.single_elimination import (
    SingleEliminationMatchStrategy,
)
from src.domain.services.match_strategy.swiss import SwissMatchStrategy
from src.domain.utils.enums import TournamentMode

STRATEGIES = {
    TournamentMode.SINGLE_ELIMINATION: SingleEliminationMatchStrategy,
    TournamentMode.DOUBLE_ELIMINATION: DoubleEliminationMatchStrategy,
    TournamentMode.ROUND_ROBIN: RoundRobinMatchStrategy,
    TournamentMode.SWISS: SwissMatchStrategy,
}


def get_match_strategy(mode: TournamentMode):
    """Return the strategy class matching the tournament mode."""
    try:
        return STRATEGIES[mode]()
    except KeyError as exc:  # pragma: no cover - defensive fallback
        raise ValueError(f"Unsupported tournament mode: {mode}") from exc
