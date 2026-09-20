import uuid
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exception_handlers import (
    tournament_manager_exception_handler,
    validation_exception_handler,
)
from src.domain.entities.players import PlayerFilters, PlayerSortField
from src.domain.entities.teams import TeamFilters, TeamSortField
from src.domain.entities.tournaments import TournamentFilters, TournamentSortField
from src.domain.exceptions.players_exceptions import (
    PlayerEmailAlreadyExistsError,
    PlayerNotFoundError,
    PlayerUsernameAlreadyExistsError,
)
from src.domain.exceptions.team_players_exceptions import (
    TeamCaptainAlreadyExistsError,
    TeamPlayerAlreadyExistsError,
    TeamPlayerNotFoundError,
)
from src.domain.exceptions.teams_exceptions import (
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
    TeamTagAlreadyExistsError,
)
from src.domain.exceptions.tournament_teams_exception import (
    TournamentPlayerAlreadyRegisteredError,
    TournamentTeamAlreadyRegisteredError,
    TournamentTeamNotEnoughPlayersError,
    TournamentTeamNotFoundError,
)
from src.domain.exceptions.tournaments_exceptions import (
    TournamentAlreadyExistsError,
    TournamentAlreadyStartedError,
    TournamentFullError,
    TournamentNotDraftError,
    TournamentNotEnoughTeams,
    TournamentNotFoundError,
    TournamentNotOpenError,
)
from src.domain.repositories.filters import PaginationParams, SearchParams, SortParams
from src.domain.repositories.paginations import PaginatedResult
from src.domain.services.players_service import PlayerService
from src.domain.services.team_players_service import TeamPlayerService
from src.domain.services.teams_service import TeamService
from src.domain.services.tournament_teams_service import TournamentTeamService
from src.domain.services.tournaments_service import TournamentService
from src.domain.utils.enums import TeamRole, TournamentStatus
from src.infrastructure.database import session as database_module
from src.infrastructure.database.session import Database
from tests.fixtures.players_fixtures import create_player
from tests.fixtures.teams_fixtures import create_team, create_teamplayer
from tests.fixtures.tournaments_fixtures import create_tournament, create_tournamentteam


def repository() -> SimpleNamespace:
    return SimpleNamespace(
        list=AsyncMock(),
        get_by_id=AsyncMock(),
        get_by_name=AsyncMock(),
        get_by_tag=AsyncMock(),
        get_by_username=AsyncMock(),
        get_by_email=AsyncMock(),
        get_by_name_and_guild=AsyncMock(),
        save=AsyncMock(),
        update=AsyncMock(),
        delete=AsyncMock(),
        save_team_membership=AsyncMock(),
        delete_team_membership=AsyncMock(),
        open_tournament=AsyncMock(),
        start_tournament=AsyncMock(),
        delete_tournament_membership=AsyncMock(),
        save_tournament_membership=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_player_service_crud_and_duplicate_checks() -> None:
    repo = repository()
    player = create_player(email="old@example.com")
    repo.get_by_id.return_value = player
    repo.save.return_value = player
    repo.update.return_value = player
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = None
    service = PlayerService(cast("Any", repo))

    result = PaginatedResult(items=[player], total=1)
    repo.list.return_value = result
    assert (
        await service.list_players(
            PlayerFilters(),
            PaginationParams(),
            SortParams[PlayerSortField](),
            SearchParams(),
        )
        == result
    )
    assert await service.get_player_by_id(player.id) == player
    assert await service.create_player(player) == player
    assert await service.update_player(player.id, create_player(id=player.id)) == player
    await service.delete_player(player.id)
    repo.get_by_username.return_value = player
    with pytest.raises(PlayerUsernameAlreadyExistsError):
        await service.create_player(create_player(username=player.username))
    with pytest.raises(PlayerUsernameAlreadyExistsError):
        await service.update_player(player.id, create_player(username="new"))
    repo.get_by_username.return_value = None
    repo.get_by_email.return_value = player
    with pytest.raises(PlayerEmailAlreadyExistsError):
        await service.update_player(player.id, create_player(email="new@example.com"))
    repo.get_by_id.return_value = None
    with pytest.raises(PlayerNotFoundError):
        await service.get_player_by_id(uuid.uuid4())
    with pytest.raises(PlayerNotFoundError):
        await service.delete_player(uuid.uuid4())


@pytest.mark.asyncio
async def test_team_service_crud_and_duplicate_checks() -> None:
    repo = repository()
    team = create_team()
    repo.get_by_id.return_value = team
    repo.save.return_value = team
    repo.update.return_value = team
    repo.get_by_name.return_value = None
    repo.get_by_tag.return_value = None
    service = TeamService(cast("Any", repo))

    result = PaginatedResult(items=[team], total=1)
    repo.list.return_value = result
    assert (
        await service.list_teams(
            TeamFilters(),
            PaginationParams(),
            SortParams[TeamSortField](),
            SearchParams(),
        )
        == result
    )
    assert await service.get_team_by_id(team.id) == team
    assert await service.create_team(team) == team
    assert await service.update_team(team.id, team) == team
    await service.delete_team(team.id)
    repo.get_by_name.return_value = team
    with pytest.raises(TeamNameAlreadyExistsError):
        await service.create_team(team)
    with pytest.raises(TeamNameAlreadyExistsError):
        await service.update_team(team.id, create_team(name="new"))
    repo.get_by_name.return_value = None
    repo.get_by_tag.return_value = team
    with pytest.raises(TeamTagAlreadyExistsError):
        await service.create_team(team)
    with pytest.raises(TeamTagAlreadyExistsError):
        await service.update_team(team.id, create_team(tag="NEW"))
    repo.get_by_id.return_value = None
    with pytest.raises(TeamNotFoundError):
        await service.get_team_by_id(uuid.uuid4())
    with pytest.raises(TeamNotFoundError):
        await service.delete_team(uuid.uuid4())


@pytest.mark.asyncio
async def test_team_player_service_all_validation_paths() -> None:
    team_repo = repository()
    player_repo = repository()
    team = create_team()
    player = create_player()
    member = create_teamplayer(team_id=team.id, player_id=player.id)
    team.members = [member]
    team_repo.get_by_id.return_value = team
    player_repo.get_by_id.return_value = player
    team_repo.save_team_membership.return_value = team
    service = TeamPlayerService(cast("Any", team_repo), cast("Any", player_repo))

    assert await service.update_team_member(team.id, player.id, TeamRole.PLAYER) == team
    await service.remove_team_member(team.id, player.id)
    with pytest.raises(TeamPlayerAlreadyExistsError):
        await service.add_team_member(member)
    team.members = []
    assert await service.add_team_member(member) == team
    captain = create_teamplayer(team_id=team.id, role=TeamRole.CAPTAIN)
    team.members = [member, captain]
    with pytest.raises(TeamCaptainAlreadyExistsError):
        await service.add_team_member(
            create_teamplayer(
                team_id=team.id, player_id=uuid.uuid4(), role=TeamRole.CAPTAIN
            )
        )
    with pytest.raises(TeamCaptainAlreadyExistsError):
        await service.update_team_member(team.id, player.id, TeamRole.CAPTAIN)
    team.members = []
    with pytest.raises(TeamPlayerNotFoundError):
        await service.update_team_member(team.id, player.id, TeamRole.PLAYER)
    with pytest.raises(TeamPlayerNotFoundError):
        await service.remove_team_member(team.id, player.id)
    team_repo.get_by_id.return_value = None
    with pytest.raises(TeamNotFoundError):
        await service.add_team_member(member)
    team_repo.get_by_id.return_value = team
    player_repo.get_by_id.return_value = None
    with pytest.raises(PlayerNotFoundError):
        await service.add_team_member(member)


@pytest.mark.asyncio
async def test_tournament_team_service_registration_rules() -> None:
    tournament_repo = repository()
    team_repo = repository()
    tournament = create_tournament(status=TournamentStatus.OPEN, min_players_per_team=1)
    team = create_team()
    team.members = [create_teamplayer(team_id=team.id)]
    membership = create_tournamentteam(tournament_id=tournament.id, team_id=team.id)
    tournament_repo.get_by_id.return_value = tournament
    team_repo.get_by_id.return_value = team
    tournament_repo.save_tournament_membership.return_value = tournament
    service = TournamentTeamService(
        cast("Any", tournament_repo), cast("Any", team_repo)
    )

    assert await service.add_team_to_tournament(membership) == tournament
    tournament.registered_teams = [membership]
    with pytest.raises(TournamentTeamAlreadyRegisteredError):
        await service.add_team_to_tournament(membership)
    await service.remove_team_from_tournament(tournament.id, team.id)
    tournament.registered_teams = []
    team.members = []
    with pytest.raises(TournamentTeamNotEnoughPlayersError):
        await service.add_team_to_tournament(membership)
    existing_membership = create_tournamentteam(
        tournament_id=tournament.id, team_id=uuid.uuid4()
    )
    existing_membership.team = team
    tournament.registered_teams = [existing_membership]
    team.members = [create_teamplayer(team_id=team.id)]
    existing_membership.team.members[0].player_id = team.members[0].player_id
    with pytest.raises(TournamentPlayerAlreadyRegisteredError):
        await service.add_team_to_tournament(membership)
    tournament.registered_teams = []
    tournament.status = TournamentStatus.DRAFT
    with pytest.raises(TournamentNotOpenError):
        await service.add_team_to_tournament(membership)
    tournament.status = TournamentStatus.OPEN
    tournament.max_teams = 0
    with pytest.raises(TournamentFullError):
        await service.add_team_to_tournament(membership)
    team_repo.get_by_id.return_value = None
    tournament.max_teams = 8
    with pytest.raises(TeamNotFoundError):
        await service.add_team_to_tournament(membership)
    tournament_repo.get_by_id.return_value = None
    with pytest.raises(TournamentNotFoundError):
        await service.add_team_to_tournament(membership)


@pytest.mark.asyncio
async def test_tournament_team_service_remove_validation() -> None:
    tournament_repo = repository()
    team_repo = repository()
    tournament = create_tournament(status=TournamentStatus.OPEN)
    team = create_team()
    tournament_repo.get_by_id.return_value = tournament
    team_repo.get_by_id.return_value = team
    service = TournamentTeamService(
        cast("Any", tournament_repo), cast("Any", team_repo)
    )

    with pytest.raises(TournamentTeamNotFoundError):
        await service.remove_team_from_tournament(tournament.id, team.id)
    tournament.status = TournamentStatus.DRAFT
    with pytest.raises(TournamentNotOpenError):
        await service.remove_team_from_tournament(tournament.id, team.id)
    team_repo.get_by_id.return_value = None
    tournament.status = TournamentStatus.OPEN
    with pytest.raises(TeamNotFoundError):
        await service.remove_team_from_tournament(tournament.id, team.id)
    tournament_repo.get_by_id.return_value = None
    with pytest.raises(TournamentNotFoundError):
        await service.remove_team_from_tournament(tournament.id, team.id)


@pytest.mark.asyncio
async def test_tournament_service_state_rules() -> None:
    repo = repository()
    tournament = create_tournament(status=TournamentStatus.DRAFT)
    repo.get_by_id.return_value = tournament
    repo.get_by_name_and_guild.return_value = None
    repo.save.return_value = tournament
    repo.update.return_value = tournament
    repo.open_tournament.return_value = tournament
    service = TournamentService(cast("Any", repo))

    result = PaginatedResult(items=[tournament], total=1)
    repo.list.return_value = result
    assert (
        await service.list_tournaments(
            TournamentFilters(),
            PaginationParams(),
            SortParams[TournamentSortField](),
            SearchParams(),
        )
        == result
    )
    assert await service.create_tournament(tournament) == tournament
    assert await service.update_tournament(tournament.id, tournament) == tournament
    assert await service.open_tournament(tournament.id) == tournament
    repo.get_by_name_and_guild.return_value = tournament
    with pytest.raises(TournamentAlreadyExistsError):
        await service.create_tournament(tournament)
    repo.get_by_name_and_guild.return_value = None
    repo.get_by_id.return_value = None
    with pytest.raises(TournamentNotFoundError):
        await service.update_tournament(tournament.id, tournament)
    with pytest.raises(TournamentNotFoundError):
        await service.open_tournament(tournament.id)
    repo.get_by_id.return_value = create_tournament(status=TournamentStatus.OPEN)
    with pytest.raises(TournamentNotDraftError):
        await service.update_tournament(tournament.id, tournament)
    with pytest.raises(TournamentNotDraftError):
        await service.open_tournament(tournament.id)
    repo.get_by_id.return_value = create_tournament(status=TournamentStatus.DRAFT)
    with pytest.raises(TournamentAlreadyStartedError):
        await service.start_tournament(tournament.id)
    repo.get_by_id.return_value = create_tournament(status=TournamentStatus.OPEN)
    repo.get_by_id.return_value.registered_teams = [SimpleNamespace()]
    with pytest.raises(TournamentNotEnoughTeams):
        await service.start_tournament(tournament.id)


@pytest.mark.asyncio
async def test_exception_handlers_return_sanitized_json() -> None:
    error = PlayerNotFoundError(details={"id": "missing"})
    response = await tournament_manager_exception_handler(cast("Any", None), error)
    assert response.status_code == 404
    assert response.body is not None
    validation_error = RequestValidationError(
        [{"loc": ("body", "name"), "msg": "required", "type": "missing"}]
    )
    response = await validation_exception_handler(cast("Any", None), validation_error)
    assert response.status_code == 422
    assert response.body is not None


@pytest.mark.asyncio
async def test_database_guards_and_session_rollback() -> None:
    database = Database()
    with pytest.raises(RuntimeError):
        async with database.get_session():
            pass
    with pytest.raises(RuntimeError):
        async with database.get_transaction():
            pass

    session = AsyncMock(spec=AsyncSession)
    session_context = AsyncMock()
    session_context.__aenter__.return_value = session
    database.session_factory = cast("Any", lambda: session_context)
    with pytest.raises(RuntimeError):
        async with database.get_session():
            raise RuntimeError("rollback")
    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_database_connect_and_disconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    database = Database()
    engine = AsyncMock()
    monkeypatch.setattr(
        database_module, "create_async_engine", lambda *args, **kwargs: engine
    )

    await database.connect()
    assert database.engine is engine
    assert database.session_factory is not None
    await database.disconnect()
    engine.dispose.assert_awaited_once()
