from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.domain.exceptions.error_codes import (
    PlayerErrorCodes,
    TeamErrorCodes,
    TeamPlayerErrorCodes,
)
from src.domain.utils.enums import TeamRole


class TestTeamsCustomAPI:
    """
    Model representing a test teams api for custom operations.
    """

    TEAM_BASE_PATH = "/api/v1/teams"
    PLAYER_BASE_PATH = "/api/v1/players"

    # Custom operations
    @pytest.mark.asyncio
    async def test_add_team_member(self, test_client: AsyncClient) -> None:
        """
        Execute test create new team.

        Args:
            test_client: The test_client parameter.
        """
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.PLAYER,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        data = teamplayer_response.json()
        assert len(data["members"]) == 1
        assert data["id"] == request["team_id"]
        assert data["members"][0]["team_id"] == request["team_id"]
        assert data["members"][0]["player_id"] == request["player_id"]
        assert data["members"][0]["role"] == request["role_player"]

    @pytest.mark.asyncio
    async def test_add_already_existing_team_member(
        self, test_client: AsyncClient
    ) -> None:
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.PLAYER,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Attempt to create the same team player again
        duplicate_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=request
        )
        assert duplicate_response.status_code == HTTPStatus.CONFLICT.value
        data = duplicate_response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_PLAYER_EXISTS

    @pytest.mark.asyncio
    async def test_add_team_member_to_nonexistant_team(
        self, test_client: AsyncClient
    ) -> None:
        # create team
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # create player
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        request = {
            "team_id": non_existent_id,
            "player_id": player_data["id"],
            "role_player": TeamRole.PLAYER,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.NOT_FOUND.value
        data = teamplayer_response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    @pytest.mark.asyncio
    async def test_add_team_member_for_nonexistant_player(
        self, test_client: AsyncClient
    ) -> None:
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
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # create team membership
        request = {
            "team_id": team_data["id"],
            "player_id": non_existent_id,
            "role_player": TeamRole.PLAYER,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.NOT_FOUND.value
        data = teamplayer_response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_add_team_captain_in_team_with_captain(
        self, test_client: AsyncClient
    ) -> None:
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        teamplayer_request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.CAPTAIN,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Attempt to create a new player
        player1_request = {
            "username": "new_player1",
            "display_name": "New Player1",
            "email": "new_player1@example.com",
        }
        player1_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player1_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player1_data = player1_response.json()
        # create team membership for player1
        teamplayer1_request = {
            "team_id": team_data["id"],
            "player_id": player1_data["id"],
            "role_player": TeamRole.CAPTAIN,
        }
        teamplayer1_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer1_request
        )
        assert teamplayer1_response.status_code == HTTPStatus.CONFLICT.value
        data = teamplayer1_response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_CAPTAIN_EXISTS

    @pytest.mark.asyncio
    async def test_update_team_member(self, test_client: AsyncClient) -> None:
        """
        Execute test update team player.

        Args:
            test_client: The test_client parameter.
        """
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        teamplayer_request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.PLAYER,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        data = teamplayer_response.json()
        # update team _membership
        update_request = {"role_player": TeamRole.CAPTAIN}
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team_data['id']}/members/{player_data['id']}",
            json=update_request,
        )
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["members"]) == 1
        assert data["id"] == team_data["id"]
        assert data["members"][0]["team_id"] == team_data["id"]
        assert data["members"][0]["player_id"] == player_data["id"]
        assert data["members"][0]["role"] == update_request["role_player"]

    @pytest.mark.asyncio
    async def test_update_nonexistant_team_member(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update non existing team player.

        Args:
            test_client: The test_client parameter.
        """
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # update team membership
        update_request = {"role_player": TeamRole.CAPTAIN}
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team_data['id']}/members/{player_data['id']}",
            json=update_request,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_PLAYER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_team_member_for_non_existing_team(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update team player for non existing team.

        Args:
            test_client: The test_client parameter.
        """
        # create team
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # create player
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # Update team membership
        update_request = {"role_player": TeamRole.CAPTAIN}
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{non_existent_id}/members/{player_data['id']}",
            json=update_request,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_team_member_for_non_existing_player(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update team player for non existing player.

        Args:
            test_client: The test_client parameter.
        """
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
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # Update team membership
        update_request = {"role_player": TeamRole.CAPTAIN}
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team_data['id']}/members/{non_existent_id}",
            json=update_request,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_team_player_with_existing_captain(
        self, test_client: AsyncClient
    ) -> None:

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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        teamplayer_request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.CAPTAIN,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Attempt to create a new player
        player1_request = {
            "username": "new_player1",
            "display_name": "New Player1",
            "email": "new_player1@example.com",
        }
        player1_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player1_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player1_data = player1_response.json()
        # create team membership for player1
        teamplayer1_request = {
            "team_id": team_data["id"],
            "player_id": player1_data["id"],
            "role_player": TeamRole.PLAYER,
        }
        teamplayer1_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer1_request
        )
        assert teamplayer1_response.status_code == HTTPStatus.CREATED.value
        # update team membership for player1
        update_request = {"role_player": TeamRole.CAPTAIN}
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{teamplayer1_request['team_id']}/members/{teamplayer1_request['player_id']}",
            json=update_request,
        )
        assert response.status_code == HTTPStatus.CONFLICT.value
        data = response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_CAPTAIN_EXISTS

    @pytest.mark.asyncio
    async def test_remove_team_member(self, test_client: AsyncClient) -> None:
        """
        Execute test remove team player.

        Args:
            test_client: The test_client parameter.
        """
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # create team membership
        teamplayer_request = {
            "team_id": team_data["id"],
            "player_id": player_data["id"],
            "role_player": TeamRole.PLAYER,
        }
        teamplayer_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members", json=teamplayer_request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Delete team membership
        response = await test_client.delete(
            f"{self.TEAM_BASE_PATH}/{team_data['id']}/members/{player_data['id']}"
        )
        assert response.status_code == HTTPStatus.NO_CONTENT.value
        # Attempt to retrieve the deleted team
        get_response = await test_client.get(f"{self.TEAM_BASE_PATH}/{team_data['id']}")
        assert get_response.status_code == HTTPStatus.OK.value
        data = get_response.json()
        assert data["members"] == []

    @pytest.mark.asyncio
    async def test_remove_nonexistant_team_member(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test remove non existing team player.

        Args:
            test_client: The test_client parameter.
        """
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
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # delete team membership
        response = await test_client.delete(
            f"{self.TEAM_BASE_PATH}/{team_data['id']}/members/{player_data['id']}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_PLAYER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_remove_team_member_for_non_existing_team(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test remove membership of a player for non existing team.

        Args:
            test_client: The test_client parameter.
        """
        # create team
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # create player
        player_request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        player_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=player_request
        )
        assert player_response.status_code == HTTPStatus.CREATED.value
        player_data = player_response.json()
        # Delete team membership
        response = await test_client.delete(
            f"{self.TEAM_BASE_PATH}/{non_existent_id}/members/{player_data['id']}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    @pytest.mark.asyncio
    async def test_remove_team_member_for_non_existing_player(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test remove membership non existing player for a team.

        Args:
            test_client: The test_client parameter.
        """
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
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        # Delete team membership
        response = await test_client.delete(
            f"{self.TEAM_BASE_PATH}/{team_data['id']}/members/{non_existent_id}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND
