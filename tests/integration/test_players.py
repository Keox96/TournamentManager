"""
Test module for test players.
"""

from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.domain.exceptions.error_codes import GenericErrorCodes, PlayerErrorCodes


class TestTPlayersAPI:
    """
    Model representing a test players api.
    """

    PLAYER_BASE_PATH = "/api/v1/players"

    # CRUD operations
    # Get by ID, username and email
    @pytest.mark.asyncio
    async def test_get_player_by_id(self, test_client: AsyncClient) -> None:
        # First, create a player to retrieve
        """
        Execute test get player by id.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "username": "get_by_id_player",
            "display_name": "Get By ID Player",
            "email": "get_by_id_player@example.com",
        }
        create_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=request
        )
        assert create_response.status_code == HTTPStatus.CREATED.value
        player_id = create_response.json()["id"]

        # Now, retrieve the player by ID
        get_response = await test_client.get(f"{self.PLAYER_BASE_PATH}/{player_id}")
        assert get_response.status_code == HTTPStatus.OK.value
        data = get_response.json()
        assert data["id"] == player_id
        assert data["username"] == request["username"]
        assert data["display_name"] == request["display_name"]
        assert data["email"] == request["email"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_player(self, test_client: AsyncClient) -> None:
        """
        Execute test get nonexistent player.

        Args:
            test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(f"{self.PLAYER_BASE_PATH}/{non_existent_id}")
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND

    # List with filters, pagination, sorting and search
    @pytest.mark.asyncio
    async def test_list_players_with_filters(self, test_client: AsyncClient) -> None:
        """
        Execute test list players with filters.

        Args:
            test_client: The test_client parameter.
        """
        # Create players to filter
        players = [
            {
                "username": "filter_player1",
                "display_name": "Filter Player 1",
                "email": "filter_player1@example.com",
            },
            {
                "username": "filter_player2",
                "display_name": "Filter Player 2",
                "email": "filter_player2@example.com",
            },
        ]
        for player in players:
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list players with a filter
        params = {"display_name_like": "Filter Player 1"}
        response = await test_client.get(f"{self.PLAYER_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["display_name"] == "Filter Player 1"

    @pytest.mark.asyncio
    async def test_list_players_with_pagination(self, test_client: AsyncClient) -> None:
        """
        Execute test list players with pagination.

        Args:
            test_client: The test_client parameter.
        """
        # Create players to paginate
        for i in range(15):
            player = {
                "username": f"pagination_player{i}",
                "display_name": f"Pagination Player {i}",
                "email": f"pagination_player{i}@example.com",
            }
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list players with pagination
        params = {"page": 2, "size": 5}
        response = await test_client.get(f"{self.PLAYER_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 5
        assert data["items"][0]["username"] == "pagination_player9"
        assert data["items"][1]["username"] == "pagination_player8"
        assert data["items"][2]["username"] == "pagination_player7"
        assert data["items"][3]["username"] == "pagination_player6"
        assert data["items"][4]["username"] == "pagination_player5"

    @pytest.mark.asyncio
    async def test_list_players_with_sorting(self, test_client: AsyncClient) -> None:
        """
        Execute test list players with sorting.

        Args:
            test_client: The test_client parameter.
        """
        # Create players to sort
        for i in range(3):
            player = {
                "username": f"sort_player{i}",
                "display_name": f"Sort Player {i}",
                "email": f"sort_player{i}@example.com",
            }
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list players with sorting
        params = {"sort": "username:desc"}
        response = await test_client.get(f"{self.PLAYER_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 3
        assert data["items"][0]["username"] == "sort_player2"
        assert data["items"][1]["username"] == "sort_player1"
        assert data["items"][2]["username"] == "sort_player0"

    @pytest.mark.asyncio
    async def test_list_players_with_invalid_sorting(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test list players with invalid sorting.

        Args:
            test_client: The test_client parameter.
        """
        params = {"sort": "invalid_field:asc"}
        response = await test_client.get(f"{self.PLAYER_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.INVALID_SORT_FORMAT

    @pytest.mark.asyncio
    async def test_list_players_with_search(self, test_client: AsyncClient) -> None:
        """
        Execute test list players with search.

        Args:
            test_client: The test_client parameter.
        """
        # Create players to search
        for i in range(3):
            player = {
                "username": f"search_player{i}",
                "display_name": f"Search Player {i}",
                "email": f"search_player{i}@example.com",
            }
            response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player)
            assert response.status_code == HTTPStatus.CREATED.value
        # Now, list players with search
        params = {"search": "Search Player 1"}
        response = await test_client.get(f"{self.PLAYER_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["display_name"] == "Search Player 1"

    # Create
    @pytest.mark.asyncio
    async def test_create_new_player(self, test_client: AsyncClient) -> None:
        """
        Execute test create new player.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "username": "new_player",
            "display_name": "New Player",
            "email": "new_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        data = response.json()
        assert data["username"] == request["username"]
        assert data["display_name"] == request["display_name"]
        assert data["email"] == request["email"]

    @pytest.mark.asyncio
    async def test_create_duplicate_player(self, test_client: AsyncClient) -> None:
        """
        Execute test create duplicate player.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "username": "duplicate_player",
            "display_name": "Duplicate Player",
            "email": "duplicate_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        # Attempt to create the same player again
        duplicate_response = await test_client.post(
            f"{self.PLAYER_BASE_PATH}/", json=request
        )
        assert duplicate_response.status_code == HTTPStatus.CONFLICT.value
        data = duplicate_response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_USERNAME_EXISTS

    @pytest.mark.asyncio
    async def test_create_player_with_invalid_data(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test create player with invalid data.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "username": "",  # Invalid: empty username
            "display_name": "Invalid Player",
            "email": "invalid_email@example.com",  # Valid email
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.VALIDATION_ERROR

    # Update
    @pytest.mark.asyncio
    async def test_update_player(self, test_client: AsyncClient) -> None:
        """
        Execute test update player.

        Args:
            test_client: The test_client parameter.
        """
        # First, create a player to update
        request = {
            "username": "update_player",
            "display_name": "Update Player",
            "email": "update_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        player_id = response.json()["id"]
        # Now, update the player's display name and email
        update_request = {
            "username": "update_player",  # Username cannot be changed in this test
            "display_name": "Updated Player",
            "email": "updated_player@example.com",
        }
        response = await test_client.put(
            f"{self.PLAYER_BASE_PATH}/{player_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert data["display_name"] == update_request["display_name"]
        assert data["email"] == update_request["email"]

    @pytest.mark.asyncio
    async def test_update_player_with_invalid_data(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update player with invalid data.

        Args:
            test_client: The test_client parameter.
        """
        # First, create a player to update
        request = {
            "username": "invalid_update_player",
            "display_name": "Invalid Update Player",
            "email": "invalid_update_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        player_id = response.json()["id"]

        # Attempt to update the player with invalid data
        invalid_update_request = {
            "display_name": "",  # Invalid: empty display name
            "email": "invalid_update_player@example.com",
        }
        response = await test_client.put(
            f"{self.PLAYER_BASE_PATH}/{player_id}", json=invalid_update_request
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.VALIDATION_ERROR

    @pytest.mark.asyncio
    async def test_update_nonexistent_player(self, test_client: AsyncClient) -> None:
        """
        Execute test update nonexistent player.

        Args:
            test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        update_request = {
            "username": "nonexistent_player",
            "display_name": "Nonexistent Player",
            "email": "nonexistent_player@example.com",
        }
        response = await test_client.put(
            f"{self.PLAYER_BASE_PATH}/{non_existent_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_player_with_duplicate_username(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update player with duplicate username.

        Args:
            test_client: The test_client parameter.
        """
        # First, create two players
        player1 = {
            "username": "original_player",
            "display_name": "Original Player",
            "email": "original_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player1)
        assert response.status_code == HTTPStatus.CREATED.value

        player2 = {
            "username": "duplicate_player",
            "display_name": "Duplicate Player",
            "email": "duplicate_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player2)
        assert response.status_code == HTTPStatus.CREATED.value
        player2_id = response.json()["id"]

        # Attempt to update the second player with the first player's username
        update_request = {
            "username": "original_player",  # This username is already taken
            "display_name": "Updated Duplicate Player",
            "email": "updated_duplicate_player@example.com",
        }
        response = await test_client.put(
            f"{self.PLAYER_BASE_PATH}/{player2_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.CONFLICT.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_USERNAME_EXISTS

    @pytest.mark.asyncio
    async def test_update_player_with_duplicate_email(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update player with duplicate email.

        Args:
            test_client: The test_client parameter.
        """
        # First, create two players
        player1 = {
            "username": "email_original_player",
            "display_name": "Email Original Player",
            "email": "email_original_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player1)
        assert response.status_code == HTTPStatus.CREATED.value

        player2 = {
            "username": "email_duplicate_player",
            "display_name": "Email Duplicate Player",
            "email": "email_duplicate_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=player2)
        assert response.status_code == HTTPStatus.CREATED.value
        player2_id = response.json()["id"]

        # Attempt to update the second player with the first player's email
        update_request = {
            "username": "email_updated_duplicate_player",
            "display_name": "Email Updated Duplicate Player",
            "email": "email_original_player@example.com",  # This email is already taken
        }
        response = await test_client.put(
            f"{self.PLAYER_BASE_PATH}/{player2_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.CONFLICT.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_EMAIL_EXISTS

    # Delete
    @pytest.mark.asyncio
    async def test_delete_player(self, test_client: AsyncClient) -> None:
        """
        Execute test delete player.

        Args:
            test_client: The test_client parameter.
        """
        # First, create a player to delete
        request = {
            "username": "delete_player",
            "display_name": "Delete Player",
            "email": "delete_player@example.com",
        }
        response = await test_client.post(f"{self.PLAYER_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        player_id = response.json()["id"]
        # Now, delete the player
        response = await test_client.delete(f"{self.PLAYER_BASE_PATH}/{player_id}")
        assert response.status_code == HTTPStatus.NO_CONTENT.value
        # Attempt to retrieve the deleted player
        get_response = await test_client.get(f"{self.PLAYER_BASE_PATH}/{player_id}")
        assert get_response.status_code == HTTPStatus.NOT_FOUND.value

    @pytest.mark.asyncio
    async def test_delete_nonexistent_player(self, test_client: AsyncClient) -> None:
        """
        Execute test delete nonexistent player.

        Args:
            test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.delete(
            f"{self.PLAYER_BASE_PATH}/{non_existent_id}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == PlayerErrorCodes.PLAYER_NOT_FOUND

    # Custom operations
