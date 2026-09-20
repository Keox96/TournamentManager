import uuid
from datetime import datetime

import pytest

from src.domain.entities.matchs import Match, MatchStatus
from src.domain.entities.tournaments import Tournament, TournamentTeam
from src.domain.services.matchs_service import MatchService
from src.domain.utils.enums import TournamentMode


class _DummyRepository:
    def __init__(self) -> None:
        self.matches: list[Match] = []

    async def create_match(self, match: Match) -> Match:
        self.matches.append(match)
        return match


@pytest.mark.parametrize(
    ("mode", "expected_match_count"),
    [
        (TournamentMode.SINGLE_ELIMINATION, 2),
        (TournamentMode.DOUBLE_ELIMINATION, 2),
        (TournamentMode.ROUND_ROBIN, 6),
        (TournamentMode.SWISS, 3),
    ],
)
async def test_match_service_uses_mode_strategy(mode: TournamentMode, expected_match_count: int) -> None:
    teams = [
        TournamentTeam(
            tournament_id=uuid.uuid4(),
            team_id=uuid.uuid4(),
            created_at=datetime.now(),
            updated_at=None,
        )
        for _ in range(4)
    ]
    tournament = Tournament(
        id=uuid.uuid4(),
        guild_id=42,
        name="Mode test",
        game="Test Game",
        mode=mode,
        registered_teams=teams,
        created_at=datetime.now(),
        updated_at=None,
    )

    repository = _DummyRepository()
    generated = await MatchService(repository).generate_matchs(tournament)

    assert generated is tournament
    assert len(generated.matches) == expected_match_count
    assert all(match.tournament_id == tournament.id for match in generated.matches)
    assert all(match.status == MatchStatus.PENDING for match in generated.matches)
    assert all(isinstance(match, Match) for match in generated.matches)
    assert repository.matches == generated.matches
