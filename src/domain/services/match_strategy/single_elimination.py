import uuid
from datetime import datetime

from src.domain.entities.matchs import Match, MatchStatus, MatchTeam
from src.domain.entities.tournaments import Tournament
from src.domain.services.match_strategy.base import AbstractMatchStrategy


class SingleEliminationMatchStrategy(AbstractMatchStrategy):
    """Generate a simplified knockout bracket for a single-elimination tournament."""

    def generate_matches(self, tournament: Tournament) -> list[Match]:
        team_ids = [team.team_id for team in tournament.registered_teams]
        if len(team_ids) < 2:
            return []

        matches: list[Match] = []
        current_round = list(team_ids)
        round_number = 1

        while len(current_round) > 1:
            next_round: list[uuid.UUID] = []

            for index in range(0, len(current_round), 2):
                pair = current_round[index : index + 2]
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
                    # A simplified single-elimination bracket keeps the first participant
                    # as the provisional winner for the next round.
                    next_round.append(pair[0])
                elif len(pair) == 1:
                    next_round.append(pair[0])

            current_round = next_round
            round_number += 1

        return matches
