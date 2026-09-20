import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.matchs import Match, MatchPlayer, MatchTeam
from src.domain.utils.enums import MatchStatus, TeamRole, TournamentStatus
from src.infrastructure.database.repositories.matchs_repository import (
    SqlMatchRepository,
)
from src.infrastructure.database.repositories.players_repository import (
    SqlPlayerRepository,
)
from src.infrastructure.database.repositories.teams_repository import SqlTeamRepository
from src.infrastructure.database.repositories.tournaments_repository import (
    SqlTournamentRepository,
)
from tests.fixtures.players_fixtures import create_player
from tests.fixtures.teams_fixtures import create_team, create_teamplayer
from tests.fixtures.tournaments_fixtures import create_tournament


@pytest.mark.asyncio
async def test_match_repository_crud_and_result_persistence(
    test_session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with test_session_factory() as session:
        tournament_repository = SqlTournamentRepository(session)
        team_repository = SqlTeamRepository(session)
        player_repository = SqlPlayerRepository(session)
        repository = SqlMatchRepository(session)

        tournament = create_tournament(status=TournamentStatus.IN_PROGRESS)
        team_one = create_team(name="One", tag="ONE")
        team_two = create_team(name="Two", tag="TWO")
        player_one = create_player(username="one")
        player_two = create_player(username="two")
        await tournament_repository.save(tournament)
        await team_repository.save(team_one)
        await team_repository.save(team_two)
        await player_repository.save(player_one)
        await player_repository.save(player_two)
        await team_repository.save_team_membership(
            create_teamplayer(
                team_id=team_one.id, player_id=player_one.id, role=TeamRole.PLAYER
            )
        )
        await team_repository.save_team_membership(
            create_teamplayer(
                team_id=team_two.id, player_id=player_two.id, role=TeamRole.PLAYER
            )
        )
        await session.commit()

        match = Match(
            id=uuid.uuid4(),
            tournament_id=tournament.id,
            status=MatchStatus.PENDING,
            round=1,
            created_at=tournament.created_at,
            participants=[
                MatchTeam(
                    match_id=uuid.uuid4(),
                    team_id=team_one.id,
                    created_at=tournament.created_at,
                ),
                MatchTeam(
                    match_id=uuid.uuid4(),
                    team_id=team_two.id,
                    created_at=tournament.created_at,
                ),
            ],
        )
        for participant in match.participants:
            participant.match_id = match.id
        created = await repository.create_match(match)
        assert created.id == match.id
        assert len(created.player_performances) == 2
        assert await repository.get_by_tournament(tournament.id)
        assert await repository.get_by_tournament_and_round(tournament.id, 1)
        updated_match = await repository.update_match_status(
            match.id, MatchStatus.IN_PROGRESS
        )
        assert updated_match is not None
        assert updated_match.status == MatchStatus.IN_PROGRESS
        assert (
            await repository.update_match_status(uuid.uuid4(), MatchStatus.COMPLETED)
        ) is None
        participant = created.participants[0]
        updated_participant = await repository.update_match_score(
            match.id, participant.team_id, 3
        )
        assert updated_participant is not None
        assert updated_participant.score == 3
        assert await repository.update_match_score(match.id, uuid.uuid4(), 3) is None

        performance = MatchPlayer(
            match_id=match.id,
            player_id=player_one.id,
            score=2,
            kills=1,
            deaths=0,
            assists=1,
            created_at=tournament.created_at,
        )
        assert await repository.save_match_player(performance)
        participant.rank = 1
        participant.score = 3
        other_participant = created.participants[1]
        other_participant.rank = 2
        other_participant.score = 1
        assert await repository.save_match_team(other_participant)
        completed = await repository.save_match_result(
            match.id,
            {item.team_id: item for item in created.participants},
            {player_one.id: performance, player_two.id: performance},
        )
        assert completed is not None
        assert completed.status == MatchStatus.COMPLETED
        assert await repository.save_match_result(uuid.uuid4(), {}, {}) is None
        await repository.delete_match(match.id)
        await session.commit()
        assert await repository.get_by_id(match.id) is None
