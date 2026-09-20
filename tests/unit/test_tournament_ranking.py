import uuid
from datetime import datetime

from src.domain.entities.matchs import Match, MatchStatus, MatchTeam
from src.domain.entities.tournaments import Tournament, TournamentTeam
from src.domain.services.tournament_ranking_service import TournamentRankingService
from src.domain.utils.enums import TournamentMode


def _match(
    tournament_id: uuid.UUID,
    first_team: uuid.UUID,
    first_score: int,
    second_team: uuid.UUID,
    second_score: int,
) -> Match:
    match_id = uuid.uuid4()
    return Match(
        id=match_id,
        tournament_id=tournament_id,
        status=MatchStatus.COMPLETED,
        round=1,
        participants=[
            MatchTeam(
                match_id=match_id,
                team_id=first_team,
                score=first_score,
                rank=1 if first_score > second_score else 1 if first_score == second_score else 2,
                created_at=datetime.now(),
                updated_at=None,
            ),
            MatchTeam(
                match_id=match_id,
                team_id=second_team,
                score=second_score,
                rank=1 if second_score >= first_score else 2,
                created_at=datetime.now(),
                updated_at=None,
            ),
        ],
        created_at=datetime.now(),
        updated_at=None,
    )


def test_round_robin_ranking_uses_points_and_score_difference() -> None:
    tournament_id = uuid.uuid4()
    teams = [uuid.uuid4() for _ in range(3)]
    tournament = Tournament(
        id=tournament_id,
        guild_id=1,
        name="Ranking test",
        game="Test Game",
        mode=TournamentMode.ROUND_ROBIN,
        registered_teams=[
            TournamentTeam(
                tournament_id=tournament_id,
                team_id=team_id,
                created_at=datetime.now(),
                updated_at=None,
            )
            for team_id in teams
        ],
        created_at=datetime.now(),
        updated_at=None,
    )
    matches = [
        _match(tournament_id, teams[0], 3, teams[1], 0),
        _match(tournament_id, teams[0], 1, teams[2], 0),
        _match(tournament_id, teams[1], 2, teams[2], 0),
    ]

    standings = TournamentRankingService().calculate(tournament, matches)

    assert standings[teams[0]].rank == 1
    assert standings[teams[1]].rank == 2
    assert standings[teams[2]].rank == 3
    assert standings[teams[0]].wins == 2
    assert standings[teams[2]].losses == 2
