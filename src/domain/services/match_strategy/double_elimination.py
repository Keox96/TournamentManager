import uuid
from datetime import datetime

from src.domain.entities.matchs import Match, MatchTeam
from src.domain.entities.tournaments import Tournament
from src.domain.services.match_strategy.base import AbstractMatchStrategy
from src.domain.utils.enums import MatchStatus


class DoubleEliminationMatchStrategy(AbstractMatchStrategy):
    """Generate a basic double-elimination bracket for a tournament."""

    def generate_matches(self, tournament: Tournament) -> list[Match]:
        team_ids = [team.team_id for team in tournament.registered_teams]
        if len(team_ids) < 2:
            return []

        matches: list[Match] = []
        bracket_round = list(team_ids)
        round_number = 1

        while len(bracket_round) > 1:
            for index in range(0, len(bracket_round), 2):
                pair = bracket_round[index : index + 2]
                if len(pair) == 2:
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
                            team_id=team_id,
                            created_at=datetime.now(),
                            updated_at=None,
                        )
                        for team_id in pair
                    ]
                    matches.append(match)
            if len(bracket_round) % 2 != 0:
                bracket_round = [bracket_round[0]] + bracket_round[1:]
            bracket_round = [bracket_round[i] for i in range(1, len(bracket_round), 2)]
            round_number += 1

        return matches
