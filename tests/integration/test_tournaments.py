"""
Test module for test tournaments.
"""

from http import HTTPStatus

import pytest
from httpx import AsyncClient

from src.domain.exceptions.error_codes import GenericErrorCodes, TournamentErrorCodes
from src.domain.utils.enums import TournamentMode, TournamentStatus


class TestTournamentsCrudAPI:
    """
    Model representing a test tournaments api for crud operations.
    """

    TOURNAMENT_BASE_PATH = "/api/v1/tournaments"

    # CRUD operations
    # Get by ID, name and guild
    @pytest.mark.asyncio
    async def test_get_tournament_by_id(self, test_client: AsyncClient) -> None:
        # First, create a tournament to retrieve
        """
        Execute test get tournament by id.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Get By ID Tournament",
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

        # Now, retrieve the tournament by ID
        get_response = await test_client.get(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}"
        )
        assert get_response.status_code == HTTPStatus.OK.value
        data = get_response.json()
        assert data["id"] == tournament_id
        assert data["name"] == request["name"]
        assert data["game"] == request["game"]
        assert data["mode"] == request["mode"]
        assert data["guild_id"] == request["guild_id"]
        assert data["min_players_per_team"] == request["min_players_per_team"]
        assert data["max_teams"] == request["max_teams"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_tournament(self, test_client: AsyncClient) -> None:
        """
        Execute test get nonexistent tournament.

        Args:
        test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(
            f"{self.TOURNAMENT_BASE_PATH}/{non_existent_id}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND

    # List with filters, pagination, sorting and search
    @pytest.mark.asyncio
    async def test_list_tournaments_with_filters(
        self, test_client: AsyncClient
    ) -> None:
        # Create multiple tournaments with different attributes
        """
        Execute test list tournaments with filters.

        Args:
            test_client: The test_client parameter.
        """
        tournaments = [
            {
                "name": "LoL Tournament",
                "game": "League of Legends",
                "mode": TournamentMode.SINGLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            },
            {
                "name": "CS:GO Tournament",
                "game": "Counter-Strike: Global Offensive",
                "mode": TournamentMode.DOUBLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            },
            {
                "name": "Dota 2 Tournament",
                "game": "Dota 2",
                "mode": TournamentMode.ROUND_ROBIN,
                "guild_id": 2,
                "min_players_per_team": 5,
                "max_teams": 8,
            },
        ]
        for tournament in tournaments:
            response = await test_client.post(
                f"{self.TOURNAMENT_BASE_PATH}/", json=tournament
            )
            assert response.status_code == HTTPStatus.CREATED.value

        # Test filtering by game
        params = {"game_like": "League"}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["game"] == "League of Legends"

        # Test filtering by guild_id
        params = {"guild_id": "1"}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["guild_id"] == 1

    @pytest.mark.asyncio
    async def test_list_tournaments_with_pagination(
        self, test_client: AsyncClient
    ) -> None:
        # Create multiple tournaments to ensure we have more than 1 page of results
        """
        Execute test list tournaments with pagination.

        Args:
            test_client: The test_client parameter.
        """
        for i in range(15):
            request = {
                "name": f"Tournament {i}",
                "game": "Test Game",
                "mode": TournamentMode.SINGLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            }
            response = await test_client.post(
                f"{self.TOURNAMENT_BASE_PATH}/", json=request
            )
            assert response.status_code == HTTPStatus.CREATED.value

        # Test pagination with page size of 10
        params = {"page": 1, "size": 10}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] >= 15

        # Test second page
        params = {"page": 2, "size": 10}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) >= 5  # At least 5 items on the second page
        assert data["total"] >= 15

    @pytest.mark.asyncio
    async def test_list_tournaments_with_sorting(
        self, test_client: AsyncClient
    ) -> None:
        # Create multiple tournaments with different names
        """
        Execute test list tournaments with sorting.

        Args:
            test_client: The test_client parameter.
        """
        for i in range(5):
            request = {
                "name": f"Tournament {chr(65 + i)}",  # Tournament A, B, C, D, E
                "game": "Test Game",
                "mode": TournamentMode.SINGLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            }
            response = await test_client.post(
                f"{self.TOURNAMENT_BASE_PATH}/", json=request
            )
            assert response.status_code == HTTPStatus.CREATED.value

        # Test sorting by name ascending
        params = {"sort": "name:asc"}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == sorted(names)

        # Test sorting by name descending
        params = {"sort": "name:desc"}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == sorted(names, reverse=True)

    @pytest.mark.asyncio
    async def test_list_tournaments_with_invalid_sorting(
        self, test_client: AsyncClient
    ) -> None:
        # Create multiple tournaments with different names
        """
        Execute test list tournaments with invalid sorting.

        Args:
            test_client: The test_client parameter.
        """
        for i in range(5):
            request = {
                "name": f"Tournament {chr(65 + i)}",  # Tournament A, B, C, D, E
                "game": "Test Game",
                "mode": TournamentMode.SINGLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            }
            response = await test_client.post(
                f"{self.TOURNAMENT_BASE_PATH}/", json=request
            )
            assert response.status_code == HTTPStatus.CREATED.value

        # Test sorting with invalid field
        params = {"sort": "invalid_field:asc"}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.INVALID_SORT_FORMAT

    @pytest.mark.asyncio
    async def test_list_tournaments_with_search(self, test_client: AsyncClient) -> None:
        # Create multiple tournaments with different names and games
        """
        Execute test list tournaments with search.

        Args:
            test_client: The test_client parameter.
        """
        tournaments = [
            {
                "name": "League of Legends Championship",
                "game": "League of Legends",
                "mode": TournamentMode.SINGLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            },
            {
                "name": "CS:GO Major",
                "game": "Counter-Strike: Global Offensive",
                "mode": TournamentMode.DOUBLE_ELIMINATION,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            },
            {
                "name": "Dota 2 International",
                "game": "Dota 2",
                "mode": TournamentMode.ROUND_ROBIN,
                "guild_id": 1,
                "min_players_per_team": 5,
                "max_teams": 8,
            },
        ]
        for tournament in tournaments:
            response = await test_client.post(
                f"{self.TOURNAMENT_BASE_PATH}/", json=tournament
            )
            assert response.status_code == HTTPStatus.CREATED.value

        # Test searching for tournaments with 'International' in the name
        params = {"search": "International"}
        response = await test_client.get(f"{self.TOURNAMENT_BASE_PATH}/", params=params)
        assert response.status_code == HTTPStatus.OK.value
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Dota 2 International"

    # Create
    @pytest.mark.asyncio
    async def test_create_new_tournament(self, test_client: AsyncClient) -> None:
        """
        Execute test create new tournament.

        Args:
        test_client: The test_client parameter.
        """
        request = {
            "name": "Test Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
            "description": "Test Description",
            "best_of": 3,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)

        assert response.status_code == HTTPStatus.CREATED.value
        data = response.json()
        assert data["name"] == request["name"]
        assert data["game"] == request["game"]
        assert data["mode"] == request["mode"]
        assert data["guild_id"] == request["guild_id"]
        assert data["min_players_per_team"] == request["min_players_per_team"]
        assert data["max_teams"] == request["max_teams"]
        assert data["description"] == request["description"]
        assert data["best_of"] == request["best_of"]

    @pytest.mark.asyncio
    async def test_create_duplicate_tournament(self, test_client: AsyncClient) -> None:
        """
        Execute test create duplicate tournament.

        Args:
        test_client: The test_client parameter.
        """
        request = {
            "name": "Duplicate Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        # Create the tournament for the first time
        response1 = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/", json=request
        )
        assert response1.status_code == HTTPStatus.CREATED.value

        # Attempt to create the same tournament again
        response2 = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/", json=request
        )
        assert response2.status_code == HTTPStatus.CONFLICT.value
        data = response2.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_ALREADY_EXISTS

    @pytest.mark.asyncio
    async def test_create_tournament_with_invalid_data(
        self, test_client: AsyncClient
    ) -> None:
        # Test creating a tournament with missing required fields
        """
        Execute test create tournament with invalid data.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY.value
        data = response.json()
        assert data["error"]["code"] == GenericErrorCodes.VALIDATION_ERROR

    # Update
    @pytest.mark.asyncio
    async def test_update_tournament(self, test_client: AsyncClient) -> None:
        # Create a tournament to update
        """
        Execute test update tournament.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Tournament to Update",
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

        # Update the tournament's name
        update_request = {
            "name": "Updated Tournament Name",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        update_response = await test_client.put(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}", json=update_request
        )
        assert update_response.status_code == HTTPStatus.OK.value
        data = update_response.json()
        assert data["id"] == tournament_id
        assert data["name"] == update_request["name"]

    @pytest.mark.asyncio
    async def test_update_tournament_with_invalid_status(
        self, test_client: AsyncClient
    ) -> None:
        # Create a tournament to update
        """
        Execute test update tournament with invalid status.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Tournament to Update",
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

        open_response = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}/open"
        )
        assert open_response.status_code == HTTPStatus.OK.value
        assert open_response.json()["status"] == TournamentStatus.OPEN.value

        # Attempt to update the tournament's name while it's in OPEN status
        update_request = {
            "name": "Updated Tournament Name",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        update_response = await test_client.put(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}", json=update_request
        )
        assert update_response.status_code == HTTPStatus.BAD_REQUEST.value
        data = update_response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_DRAFT

    @pytest.mark.asyncio
    async def test_update_nonexistent_tournament(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test update nonexistent tournament.

        Args:
        test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        update_request = {
            "name": "Updated Tournament Name",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        response = await test_client.put(
            f"{self.TOURNAMENT_BASE_PATH}/{non_existent_id}", json=update_request
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_tournament_with_duplicate_name(
        self, test_client: AsyncClient
    ) -> None:
        # Create two tournaments to test duplicate name update
        """
        Execute test update tournament with duplicate name.

        Args:
            test_client: The test_client parameter.
        """
        request1 = {
            "name": "Original Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        create_response1 = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/", json=request1
        )
        assert create_response1.status_code == HTTPStatus.CREATED.value
        tournament_id1 = create_response1.json()["id"]

        request2 = {
            "name": "Another Tournament",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        create_response2 = await test_client.post(
            f"{self.TOURNAMENT_BASE_PATH}/", json=request2
        )
        assert create_response2.status_code == HTTPStatus.CREATED.value

        # Attempt to update the first tournament's name to the second tournament's name
        update_request = {
            "name": request2["name"],  # Duplicate name
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        update_response = await test_client.put(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id1}", json=update_request
        )
        assert update_response.status_code == HTTPStatus.CONFLICT.value
        data = update_response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_ALREADY_EXISTS

    # Delete
    @pytest.mark.asyncio
    async def test_delete_tournament(self, test_client: AsyncClient) -> None:
        # Create a tournament to delete
        """
        Execute test delete tournament.

        Args:
            test_client: The test_client parameter.
        """
        request = {
            "name": "Tournament to Delete",
            "game": "Test Game",
            "mode": TournamentMode.SINGLE_ELIMINATION,
            "guild_id": 1,
            "min_players_per_team": 5,
            "max_teams": 8,
        }
        response = await test_client.post(f"{self.TOURNAMENT_BASE_PATH}/", json=request)
        assert response.status_code == HTTPStatus.CREATED.value
        tournament_id = response.json()["id"]

        # Delete the tournament
        delete_response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}"
        )
        assert delete_response.status_code == HTTPStatus.NO_CONTENT.value

        # Verify the tournament has been deleted
        get_response = await test_client.get(
            f"{self.TOURNAMENT_BASE_PATH}/{tournament_id}"
        )
        assert get_response.status_code == HTTPStatus.NOT_FOUND.value
        data = get_response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tournament(
        self, test_client: AsyncClient
    ) -> None:
        """
        Execute test delete nonexistent tournament.

        Args:
        test_client: The test_client parameter.
        """
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.delete(
            f"{self.TOURNAMENT_BASE_PATH}/{non_existent_id}"
        )
        assert response.status_code == HTTPStatus.NOT_FOUND.value
        data = response.json()
        assert data["error"]["code"] == TournamentErrorCodes.TOURNAMENT_NOT_FOUND
