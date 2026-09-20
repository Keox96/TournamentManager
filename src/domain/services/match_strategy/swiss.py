import uuid
from datetime import datetime

from src.domain.entities.matchs import Match, MatchTeam
from src.domain.entities.tournaments import Tournament
from src.domain.services.match_strategy.base import AbstractMatchStrategy
from src.domain.utils.enums import MatchStatus


class SwissMatchStrategy(AbstractMatchStrategy):
    """Generate a simplified Swiss-style schedule with one match per round."""

    def generate_matches(self, tournament: Tournament) -> list[Match]:
        team_ids = [team.team_id for team in tournament.registered_teams]
        if len(team_ids) < 2:
            return []

        matches: list[Match] = []
        current_order = list(team_ids)

        for round_number in range(1, len(current_order)):
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
                    team_id=current_order[0],
                    created_at=datetime.now(),
                    updated_at=None,
                ),
                MatchTeam(
                    match_id=match.id,
                    team_id=current_order[1],
                    created_at=datetime.now(),
                    updated_at=None,
                ),
            ]
            matches.append(match)

            current_order = [current_order[0], *current_order[2:], current_order[1]]

        return matches
