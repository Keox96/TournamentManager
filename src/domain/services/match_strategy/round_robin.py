import uuid
from datetime import datetime

from src.domain.entities.matchs import Match, MatchTeam
from src.domain.entities.tournaments import Tournament
from src.domain.services.match_strategy.base import AbstractMatchStrategy
from src.domain.utils.enums import MatchStatus


class RoundRobinMatchStrategy(AbstractMatchStrategy):
    """Generate all-vs-all round robin matches for a tournament."""

    def generate_matches(self, tournament: Tournament) -> list[Match]:
        team_ids = [team.team_id for team in tournament.registered_teams]
        if len(team_ids) < 2:
            return []

        matches: list[Match] = []
        for round_number, i in enumerate(range(len(team_ids)), start=1):
            for j in range(i + 1, len(team_ids)):
                match = Match(
                    id=uuid.uuid4(),
                    tournament_id=tournament.id,
                    status=MatchStatus.PENDING,
                    round=round_number,
                    created_at=datetime.now(),
                    updated_at=None,
                )
                match.participants = [
                    MatchTeam(
                        match_id=match.id,
                        team_id=team_ids[i],
                        created_at=datetime.now(),
                        updated_at=None,
                    ),
                    MatchTeam(
                        match_id=match.id,
                        team_id=team_ids[j],
                        created_at=datetime.now(),
                        updated_at=None,
                    ),
                ]
                matches.append(match)

        return matches
