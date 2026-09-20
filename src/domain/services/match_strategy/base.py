from abc import ABC, abstractmethod

from src.domain.entities.matchs import Match
from src.domain.entities.tournaments import Tournament


class AbstractMatchStrategy(ABC):
    """Strategy contract for generating tournament matches."""

    @abstractmethod
    def generate_matches(self, tournament: Tournament) -> list[Match]:
        """Return the list of matches for the given tournament state."""
        raise NotImplementedError
