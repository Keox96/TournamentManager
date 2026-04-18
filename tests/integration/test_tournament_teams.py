"""
Test module for test tournaments.
"""

import uuid
from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.domain.exceptions.error_codes import (
    TeamErrorCodes,
    TournamentErrorCodes,
    TournamentTeamErrorCodes,
)
from src.domain.utils.enums import TeamRole, TournamentMode, TournamentStatus


class TestTournamentsCustomAPI:
    """
    Model representing a test tournaments api for custom operations.
    """

    TOURNAMENT_BASE_PATH = "/api/v1/tournaments"
    TEAM_BASE_PATH = "/api/v1/teams"
    PLAYER_BASE_PATH = "/api/v1/players"

    # Open Tournament
    @pytest.mark.asyncio
    async def test_open_tournament(self, test_client: AsyncClient) -> None:
        # Create a tournament to open
        """
        Execute test open tournament.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Tournament to Open",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        create_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/", json=request
        )
        assert create_response.status_code == HTTPStatus.CREATED.value
        tournament_id = create_response.json()["id"]

        # Open the tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        data = open_response.json()
        assert data["id"] == tournament_id
        assert data["status"] == TournamentStatus.OPEN.value

    @pytest.mark.asyncio
    async def test_open_nonexistent_tournament(self, test_client: AsyncClient) -> None:
        """
        Execute test open nonexistent tournament.

        Args:
        test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{non_existent_id}/open"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND

    @pytest.mark.asyncio
    async def test_open_tournament_with_invalid_status(
        self, test_client: AsyncClient
    ) -> None:
        # Create a tournament to open
        """
        Execute test open tournament with invalid status.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Tournament to Open",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        create_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/", json=request
        )
        assert create_response.status_code == HTTPStatus.CREATED.value
        tournament_id = create_response.json()["id"]
        # Open the tournament for the first time
        open_response1 = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}/open"
        )
        assert open_response1.status_code == HTTPStatus.OK.value
        data1 = open_response1.json()
        assert data1["id"] == tournament_id
        assert data1["status"] == TournamentStatus.OPEN.value
        # Attempt to open the tournament again while it's already in OPEN status
        open_response2 = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}/open"
        )
        assert open_response2.status_code == HTTPStatus.BAD_REQUEST.value
        data2 = open_response2.json()
        assert data2["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_DRAFT

    # Add team to a tournament
    @pytest.mark.asyncio
    async def test_add_tournament_member(self, test_client: AsyncClient) -> None:
        """
        Execute test create new team.

        Args:
            test_client: The test_client parameter.
        """
        # create tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)

        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # create player
        for i in range(3):
            player = {
                "username": f"search_player{i}",
                "display_name": f"Search Player {i}",
                "email": f"search_player{i}@example.com",
            }
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            print(f"Player {i} creation: {response.status_code} - {response.json()}")
            assert response.status_code == HTTPStatus.CREATED.value
            player_data = response.json()

            teamplayer_request = {
                "team_id": team_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            print(
                f"TeamPlayer {i} creation: {teamplayer_response.status_code} - {teamplayer_response.json()}"
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Open the tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        assert open_data["id"] == tournament_data["id"]
        assert open_data["status"] == TournamentStatus.OPEN.value
        # create tournament membership
        request = {
            "team_id": team_data["id"],
            "tournament_id": open_data["id"],
        }
        tournamentteam_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert tournamentteam_response.status_code == HTTPStatus.CREATED.value
        data = tournamentteam_response.json()
        assert len(data["registered_teams"]) == 1
        assert data["id"] == request["tournament_id"]
        assert data["registered_teams"][0]["team_id"] == request["team_id"]
        assert data["registered_teams"][0]["tournament_id"] == request["tournament_id"]

    @pytest.mark.asyncio
    async def test_add_already_existing_tournament_team(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test create new team.

        Args:
            test_client: The test_client parameter.
        """
        # create tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)

        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # create player
        for i in range(3):
            player = {
                "username": f"search_player{i}",
                "display_name": f"Search Player {i}",
                "email": f"search_player{i}@example.com",
            }
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            print(f"Player {i} creation: {response.status_code} - {response.json()}")
            assert response.status_code == HTTPStatus.CREATED.value
            player_data = response.json()

            teamplayer_request = {
                "team_id": team_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            print(
                f"TeamPlayer {i} creation: {teamplayer_response.status_code} - {teamplayer_response.json()}"
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Open the tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        assert open_data["id"] == tournament_data["id"]
        assert open_data["status"] == TournamentStatus.OPEN.value
        # create tournament membership
        request = {
            "team_id": team_data["id"],
            "tournament_id": open_data["id"],
        }
        tournamentteam_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert tournamentteam_response.status_code == HTTPStatus.CREATED.value
        # Attempt to create the same team player again
        duplicate_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert duplicate_response.status_code == HTTPStatus.CONFLICT.value
        data = duplicate_response.json()
        assert data["error"]["code"] == TournamentTeamErrorCodes.TOURNAMENT_TEAM_EXISTS

    @pytest.mark.asyncio
    async def test_add_tournament_team_to_nonexistant_tournament(
        self, test_client: AsyncClient
    ) -> None:
        # create tournament
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # create player
        for i in range(3):
            player = {
                "username": f"search_player{i}",
                "display_name": f"Search Player {i}",
                "email": f"search_player{i}@example.com",
            }
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            print(f"Player {i} creation: {response.status_code} - {response.json()}")
            assert response.status_code == HTTPStatus.CREATED.value
            player_data = response.json()

            teamplayer_request = {
                "team_id": team_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            print(
                f"TeamPlayer {i} creation: {teamplayer_response.status_code} - {teamplayer_response.json()}"
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # create team membership
        # create tournament membership
        request = {
            "team_id": team_data["id"],
            "tournament_id": non_existent_id,
        }
        tournamentteam_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert tournamentteam_response.status_code == HTTPStatus.NOT_FOUND.value
        data = tournamentteam_response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND

    @pytest.mark.asyncio
    async def test_add_tournament_team_for_nonexistant_team(
        self, test_client: AsyncClient
    ) -> None:
        # create tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)

        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # Open the tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        assert open_data["id"] == tournament_data["id"]
        assert open_data["status"] == TournamentStatus.OPEN.value
        # create team
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # create team membership
        request = {
            "tournament_id": open_data["id"],
            "team_id": non_existent_id,
        }
        tournamentteam_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert tournamentteam_response.status_code == HTTPStatus.NOT_FOUND.value
        data = tournamentteam_response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    @pytest.mark.asyncio
    async def test_add_team_to_not_openned_tournament(
        self, test_client: AsyncClient
    ) -> None:
        # create tournament (status is DRAFT by default, not open)
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # add team without opening tournament first
        request = {
            "team_id": team_data["id"],
            "tournament_id": tournament_data["id"],
        }
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_OPEN

    @pytest.mark.asyncio
    async def test_add_team_already_registered(self, test_client: AsyncClient) -> None:
        # create tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # create players and add to team
        for i in range(2):
            player = {
                "username": f"player_dup{i}",
                "display_name": f"Player Dup {i}",
                "email": f"player_dup{i}@example.com",
            }
            player_response = await test_client.post(
                f"{self.PLAYER_BASE_PATH}/", json=player
            )
            assert player_response.status_code == HTTPStatus.CREATED.value
            player_data = player_response.json()
            teamplayer_request = {
                "team_id": team_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # open tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # add team first time
        request = {
            "team_id": team_data["id"],
            "tournament_id": open_data["id"],
        }
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert response.status_code == HTTPStatus.CREATED.value
        # add team second time
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert response.status_code == HTTPStatus.CONFLICT.value
        data = response.json()
        assert data["error"]["code"] == TournamentTeamErrorCodes.TOURNAMENT_TEAM_EXISTS

    @pytest.mark.asyncio
    async def test_add_team_not_enough_players(self, test_client: AsyncClient) -> None:
        # create tournament with min 3 players
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 3,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team with only 1 player
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        player = {
            "username": "solo_player",
            "display_name": "Solo Player",
            "email": "solo_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        teamplayer_request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.CAPTAIN,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # open tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # add team with not enough players
        request = {
            "team_id": team_data["id"],
            "tournament_id": open_data["id"],
        }
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        data = response.json()
        assert (
            data["error"]["code"]
            == TournamentTeamErrorCodes.TOURNAMENT_TEAM_NOT_ENOUGH_PLAYERS
        )

    @pytest.mark.asyncio
    async def test_add_team_with_player_already_registered(
        self, test_client: AsyncClient
    ) -> None:
        # create tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create 2 shared players
        shared_players = []
        for i in range(2):
            player = {
                "username": f"shared_player{i}",
                "display_name": f"Shared Player {i}",
                "email": f"shared_player{i}@example.com",
            }
            player_response = await test_client.post(
                f"{self.PLAYER_BASE_PATH}/", json=player
            )
            assert player_response.status_code == HTTPStatus.CREATED.value
            shared_players.append(player_response.json())
        # create team 1 with shared players
        team1_request = {
            "name": "Team One",
            "tag": "T1",
            "description": None,
            "logo_url": None,
        }
        team1_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team1_request
        )
        assert team1_response.status_code == HTTPStatus.CREATED.value
        team1_data = team1_response.json()
        for i, player_data in enumerate(shared_players):
            teamplayer_request = {
                "team_id": team1_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # create team 2 with same shared players
        team2_request = {
            "name": "Team Two",
            "tag": "T2",
            "description": None,
            "logo_url": None,
        }
        team2_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team2_request
        )
        assert team2_response.status_code == HTTPStatus.CREATED.value
        team2_data = team2_response.json()
        for i, player_data in enumerate(shared_players):
            teamplayer_request = {
                "team_id": team2_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # open tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # add team 1
        request = {"team_id": team1_data["id"], "tournament_id": open_data["id"]}
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert response.status_code == HTTPStatus.CREATED.value
        # add team 2 with overlapping players
        request = {"team_id": team2_data["id"], "tournament_id": open_data["id"]}
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=request
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        data = response.json()
        assert (
            data["error"]["code"]
            == TournamentTeamErrorCodes.TOURNAMENT_TEAM_PLAYER_ALREADY_SUBSCRIBED
        )

    @pytest.mark.asyncio
    async def test_add_team_to_full_tournament(self, test_client: AsyncClient) -> None:
        # create tournament with max 2 teams
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 1,
            "max_teams": 2,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # open tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # create and register 2 teams to fill the tournament
        for t in range(2):
            team_request = {
                "name": f"Full Team {t}",
                "tag": f"FT{t}",
                "description": None,
                "logo_url": None,
            }
            team_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/", json=team_request
            )
            assert team_response.status_code == HTTPStatus.CREATED.value
            team_data = team_response.json()
            player = {
                "username": f"full_player{t}",
                "display_name": f"Full Player {t}",
                "email": f"full_player{t}@example.com",
            }
            player_response = await test_client.post(
                f"{self.PLAYER_BASE_PATH}/", json=player
            )
            assert player_response.status_code == HTTPStatus.CREATED.value
            player_data = player_response.json()
            teamplayer_request = {
                "team_id": team_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
            register_request = {
                "team_id": team_data["id"],
                "tournament_id": open_data["id"],
            }
            register_response = await test_client.post(
                f"{self.TOURNAMENT_BASE_PATH}/teams", json=register_request
            )
            assert register_response.status_code == HTTPStatus.CREATED.value
        # create a third team
        team_request = {
            "name": "Extra Team",
            "tag": "ET",
            "description": None,
            "logo_url": None,
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        player = {
            "username": "extra_player",
            "display_name": "Extra Player",
            "email": "extra_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        teamplayer_request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.CAPTAIN,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # try to add third team to full tournament
        register_request = {
            "team_id": team_data["id"],
            "tournament_id": open_data["id"],
        }
        response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=register_request
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_FULL

    @pytest.mark.asyncio
    async def test_remove_team_from_tournament(self, test_client: AsyncClient) -> None:
        # create tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": None,
            "logo_url": None,
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # create players and add to team
        for i in range(2):
            player = {
                "username": f"remove_player{i}",
                "display_name": f"Remove Player {i}",
                "email": f"remove_player{i}@example.com",
            }
            player_response = await test_client.post(
                f"{self.PLAYER_BASE_PATH}/", json=player
            )
            assert player_response.status_code == HTTPStatus.CREATED.value
            player_data = player_response.json()
            teamplayer_request = {
                "team_id": team_data["id"],
                "player_id": player_data["id"],
                "role_player": TeamRole.CAPTAIN if i == 0 else TeamRole.PLAYER,
            }
            teamplayer_response = await test_client.post(
                f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
            )
            assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # open tournament
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # register team
        register_request = {
            "team_id": team_data["id"],
            "tournament_id": open_data["id"],
        }
        register_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/teams", json=register_request
        )
        assert register_response.status_code == HTTPStatus.CREATED.value
        # remove team
        response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}{open_data['id']}/teams/{team_data['id']}"
        )
        assert response.status_code == HTTPStatus.NO_CONTENT.value
        # verify team is removed
        get_response = await test_client.get(
            f"{self.TOURNAMENT_BASE_PATH}/{open_data['id']}"
        )
        assert get_response.status_code == HTTPStatus.OK.value
        data = get_response.json()
        assert data["registered_teams"] == []

    @pytest.mark.asyncio
    async def test_remove_team_from_nonexistent_tournament(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}{str(uuid.uuid4())}/teams/{str(uuid.uuid4())}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND

    @pytest.mark.asyncio
    async def test_remove_nonexistent_team_from_tournament(
        self, test_client: AsyncClient
    ) -> None:
        # create and open tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # remove nonexistent team
        response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}{open_data['id']}/teams/{str(uuid.uuid4())}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    @pytest.mark.asyncio
    async def test_remove_team_from_not_openned_tournament(
        self, test_client: AsyncClient
    ) -> None:
        # create tournament without opening it
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        # create team
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": None,
            "logo_url": None,
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # try to remove team from closed tournament
        response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}{tournament_data['id']}/teams/{team_data['id']}"
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_OPEN

    @pytest.mark.asyncio
    async def test_remove_team_not_registered_in_tournament(
        self, test_client: AsyncClient
    ) -> None:
        # create and open tournament
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 2,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_data = response.json()
        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_data['id']}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        open_data = open_response.json()
        # create team without registering it
        team_request = {
            "name": "New Team",
            "tag": "NT",
            "description": None,
            "logo_url": None,
        }
        team_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=team_request
        )
        assert team_response.status_code == HTTPStatus.CREATED.value
        team_data = team_response.json()
        # try to remove team that is not registered
        response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}{open_data['id']}/teams/{team_data['id']}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert (
            data["error"]["code"] == TournamentTeamErrorCodes.TOURNAMENT_TEAM_NOT_FOUND
        )
