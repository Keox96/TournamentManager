"""
Test module for test teams.
"""

from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.domain.exceptions.error_codes import (
    GenericErrorCodes,
    PlayerErrorCodes,
    TeamErrorCodes,
    TeamPlayerErrorCodes,
)
from src.domain.utils.enums import TeamRole


class TestTTeamsAPI:
    """
    Model representing a test teams api.
    """

    TEAM_BASE_PATH = "/api/v1/teams"
    PLAYER_BASE_PATH = "/api/v1/players"

    # CRUD operations
    # Get by ID, username and email
    @pytest.mark.asyncio
    async def test_get_team_by_id(self, test_client: AsyncClient) -> None:
        # First, create a team to retrieve
        """
        Execute test get team by id.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Test Team",
            "tag": "TT",
            "description": "A team for testing purposes",
            "logo_url": "https://example.com/logo.png",
        }
        create_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=request
        )
        assert create_response.status_code == HTTPStatus.CREATED.value
        team_id = create_response.json()["id"]

        # Now, retrieve the team by ID
        get_response = await test_client.get(f"{self.TEAM_BASE_PATH}/{team_id}")
        assert get_response.status_code == HTTPStatus.OK.value
        data = get_response.json()
        assert data["id"] == team_id
        assert data["name"] == request["name"]
        assert data["tag"] == request["tag"]
        assert data["description"] == request["description"]
        assert data["logo_url"] == request["logo_url"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_team(self, test_client: AsyncClient) -> None:
        """
        Execute test get nonexistent team.

        Args:
            test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(f"{self.TEAM_BASE_PATH}/{non_existent_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    # List with filters, pagination, sorting and search
    @pytest.mark.asyncio
    async def test_list_teams_with_filters(self, test_client: AsyncClient) -> None:
        """
        Execute test list teams with filters.

        Args:
            test_client: The test_client parameter.
        """
        # Create teams to filter
        teams = [
            {
                "name": "Test Team",
                "tag": "TT",
                "description": "A team for testing purposes",
                "logo_url": "https://example.com/logo.png",
            },
            {
                "name": "Another Team",
                "tag": "AT",
                "description": "Another team for testing purposes",
                "logo_url": "https://example.com/logo2.png",
            },
        ]
        for team in teams:
            response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list teams with a filter
        params = {"name_like": "Test Team"}
        response = await test_client.get(f"{self.TEAM_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Test Team"

    @pytest.mark.asyncio
    async def test_list_teams_with_pagination(self, test_client: AsyncClient) -> None:
        """
        Execute test list teams with pagination.

        Args:
            test_client: The test_client parameter.
        """
        # Create teams to paginate
        for i in range(15):
            team = {
                "name": f"pagination team{i}",
                "tag": f"PT{i}",
                "description": f"Pagination Team {i}",
                "logo_url": f"https://example.com/logo_{i}.png",
            }
            response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list teams with pagination
        params = {"page": 2, "size": 5}
        response = await test_client.get(f"{self.TEAM_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 5
        assert data["items"][0]["name"] == "pagination team9"
        assert data["items"][1]["name"] == "pagination team8"
        assert data["items"][2]["name"] == "pagination team7"
        assert data["items"][3]["name"] == "pagination team6"
        assert data["items"][4]["name"] == "pagination team5"

    @pytest.mark.asyncio
    async def test_list_teams_with_sorting(self, test_client: AsyncClient) -> None:
        """
        Execute test list teams with sorting.

        Args:
            test_client: The test_client parameter.
        """
        # Create teams to sort
        for i in range(3):
            team = {
                "name": f"sort team{i}",
                "tag": f"ST{i}",
                "description": f"Sort Team {i}",
                "logo_url": f"https://example.com/logo_{i}.png",
            }
            response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list teams with sorting
        params = {"sort": "name:desc"}
        response = await test_client.get(f"{self.TEAM_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 3
        assert data["items"][0]["name"] == "sort team2"
        assert data["items"][1]["name"] == "sort team1"
        assert data["items"][2]["name"] == "sort team0"

    @pytest.mark.asyncio
    async def test_list_teams_with_invalid_sorting(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test list teams with invalid sorting.

        Args:
            test_client: The test_client parameter.
        """
        params = {"sort": "invalid_field:asc"}
        response = await test_client.get(f"{self.TEAM_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.INVALID_SORT_FORMAT

    @pytest.mark.asyncio
    async def test_list_teams_with_search(self, test_client: AsyncClient) -> None:
        """
        Execute test list teams with search.

        Args:
            test_client: The test_client parameter.
        """
        # Create teams to search
        for i in range(3):
            team = {
                "name": f"search team{i}",
                "tag": f"ST{i}",
                "description": f"Search Team {i}",
                "logo_url": f"https://example.com/logo_{i}.png",
            }
            response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list teams with search
        params = {"search": "Search Team 1"}
        response = await test_client.get(f"{self.TEAM_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "search team1"

    # Create
    @pytest.mark.asyncio
    async def test_create_new_team(self, test_client: AsyncClient) -> None:
        """
        Execute test create new team.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "New Team",
            "tag": "NT",
            "description": "New Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        data = response.json()
        assert data["name"] == request["name"]
        assert data["tag"] == request["tag"]
        assert data["description"] == request["description"]
        assert data["logo_url"] == request["logo_url"]

    @pytest.mark.asyncio
    async def test_create_duplicate_team(self, test_client: AsyncClient) -> None:
        """
        Execute test create duplicate team.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Duplicate Team",
            "tag": "DT",
            "description": "Duplicate Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        # Attempt to create the same team again
        duplicate_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/", json=request
        )
        assert duplicate_response.status_code == HTTPStatus.CONFLICT.value
        data = duplicate_response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NAME_EXISTS

    @pytest.mark.asyncio
    async def test_create_team_with_invalid_data(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test create team with invalid data.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "",  # Invalid: empty name
            "tag": "IT",  # Valid tag
            "description": "Invalid Team Description",
            "logo_url": "https://example.com/logo.png",  # Valid logo URL
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.VALIDATION_ERROR

    # Update
    @pytest.mark.asyncio
    async def test_update_team(self, test_client: AsyncClient) -> None:
        """
        Execute test update team.

        Args:
            test_client: The test_client parameter.
        """
        # First, create a team to update
        team_request = {
            "name": "Update Team",
            "tag": "UT",
            "description": "Update Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team_request)
        assert response.status_code == HTTPStatus.CREATED.value
        team_id = response.json()["id"]
        # Now, update the team's name and description
        update_request = {
            "name": "Updated Team",
            "tag": "UT",
            "description": "Updated Team Description",
            "logo_url": "https://example.com/updated_logo.png",
        }
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert data["name"] == update_request["name"]
        assert data["tag"] == update_request["tag"]
        assert data["description"] == update_request["description"]
        assert data["logo_url"] == update_request["logo_url"]

    @pytest.mark.asyncio
    async def test_update_team_with_invalid_data(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update team with invalid data.

        Args:
            test_client: The test_client parameter.
        """
        # First, create a team to update
        team_request = {
            "name": "Invalid Update Team",
            "tag": "IUT",
            "description": "Invalid Update Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team_request)
        assert response.status_code == HTTPStatus.CREATED.value
        team_id = response.json()["id"]

        # Attempt to update the team with invalid data
        invalid_update_request = {
            "name": "",  # Invalid: empty name
            "tag": "IUT",
            "description": "Invalid Update Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team_id}", json=invalid_update_request
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_update_nonexistent_team(self, test_client: AsyncClient) -> None:
        """
        Execute test update nonexistent team.

        Args:
            test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        update_request = {
            "name": "Nonexistent Team",
            "tag": "NT",
            "description": "Nonexistent Team Description",
            "logo_url": "https://example.com/logo.png",
        }
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{non_existent_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_team_with_duplicate_name(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update team with duplicate name.

        Args:
            test_client: The test_client parameter.
        """
        # First, create two teams
        team1 = {
            "name": "Original Team",
            "tag": "OT",
            "description": "Original Team Description",
            "logo_url": "https://example.com/original_logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team1)
        assert response.status_code == HTTPStatus.CREATED.value

        team2 = {
            "name": "duplicate team",
            "tag": "DT",
            "description": "Duplicate Team Description",
            "logo_url": "https://example.com/duplicate_logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team2)
        assert response.status_code == HTTPStatus.CREATED.value
        team2_id = response.json()["id"]

        # Attempt to update the second team with the first team's name
        update_request = {
            "name": "Original Team",  # This name is already taken
            "tag": "UDT",
            "description": "Updated Duplicate Team",
            "logo_url": "https://example.com/updated_duplicate_logo.png",
        }
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team2_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.CONFLICT.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NAME_EXISTS

    @pytest.mark.asyncio
    async def test_update_team_with_duplicate_tag(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update team with duplicate tag.

        Args:
            test_client: The test_client parameter.
        """
        # First, create two teams
        team1 = {
            "name": "Original Team",
            "tag": "OT",
            "description": "Original Team Description",
            "logo_url": "https://example.com/original_logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team1)
        assert response.status_code == HTTPStatus.CREATED.value

        team2 = {
            "name": "duplicate team",
            "tag": "DT",
            "description": "Duplicate Team Description",
            "logo_url": "https://example.com/duplicate_logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team2)
        assert response.status_code == HTTPStatus.CREATED.value
        team2_id = response.json()["id"]

        # Attempt to update the second team with the first team's tag
        update_request = {
            "name": "Updated Duplicate Team",
            "tag": "OT",  # This tag is already taken
            "description": "Updated Duplicate Team Description",
            "logo_url": "https://example.com/updated_duplicate_logo.png",
        }
        response = await test_client.put(
            f"{self.TEAM_BASE_PATH}/{team2_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.CONFLICT.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_TAG_EXISTS

    # Delete
    @pytest.mark.asyncio
    async def test_delete_team(self, test_client: AsyncClient) -> None:
        """
        Execute test delete team.

        Args:
            test_client: The test_client parameter.
        """
        # First, create a team to delete
        team_request = {
            "name": "Delete Team",
            "tag": "DT",
            "description": "Team to be deleted",
            "logo_url": "https://example.com/delete_logo.png",
        }
        response = await test_client.post(f"{self.TEAM_BASE_PATH}/", json=team_request)
        assert response.status_code == HTTPStatus.CREATED.value
        team_id = response.json()["id"]
        # Now, delete the team
        response = await test_client.delete(f"{self.TEAM_BASE_PATH}/{team_id}")
        assert response.status_code == HTTPStatus.NO_CONTENT.value
        # Attempt to retrieve the deleted team
        get_response = await test_client.get(f"{self.TEAM_BASE_PATH}/{team_id}")
        assert get_response.status_code == HTTPStatus.NOT_FOUND.value

    @pytest.mark.asyncio
    async def test_delete_nonexistent_team(self, test_client: AsyncClient) -> None:
        """
        Execute test delete nonexistent team.

        Args:
            test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.delete(f"{self.TEAM_BASE_PATH}/{non_existent_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

    # Custom operations
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
            f"{self.TEAM_BASE_PATH}/members/", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        data = teamplayer_response.json()
        assert len(data["members"]) == 1
        assert data["id"] == request["team_id"]
        assert data["members"][0]["team_id"] == request["team_id"]
        assert data["members"][0]["player_id"] == request["player_id"]
        assert data["members"][0]["role"] == request["role_player"]

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
            f"{self.TEAM_BASE_PATH}/members/", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.CREATED.value
        # Attempt to create the same team player again
        duplicate_response = await test_client.post(
            f"{self.TEAM_BASE_PATH}/members/", json=request
        )
        assert duplicate_response.status_code == HTTPStatus.CONFLICT.value
        data = duplicate_response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_PLAYER_EXISTS

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
            f"{self.TEAM_BASE_PATH}/members/", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.NOT_FOUND.value
        data = teamplayer_response.json()
        assert data["error"]["code"] == TeamErrorCodes.TEAM_NOT_FOUND

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
            f"{self.TEAM_BASE_PATH}/members/", json=request
        )
        assert teamplayer_response.status_code == HTTPStatus.NOT_FOUND.value
        data = teamplayer_response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND

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
            f"{self.TEAM_BASE_PATH}/members/", json=teamplayer_request
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
            f"{self.TEAM_BASE_PATH}/members/", json=teamplayer1_request
        )
        assert teamplayer1_response.status_code == HTTPStatus.CONFLICT.value
        data = teamplayer1_response.json()
        assert data["error"]["code"] == TeamPlayerErrorCodes.TEAM_CAPTAIN_EXISTS

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
            f"{self.TEAM_BASE_PATH}/members/", json=teamplayer_request
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
            f"{self.TEAM_BASE_PATH}/members/", json=teamplayer_request
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
            f"{self.TEAM_BASE_PATH}/members/", json=teamplayer1_request
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
            f"{self.TEAM_BASE_PATH}/members/", json=teamplayer_request
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
