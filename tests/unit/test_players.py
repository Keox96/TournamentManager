"""
Test module for test players.
"""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.players import PlayerFilters, PlayerSortField
from src.domain.repositories.filters import (
    PaginationParams,
    SearchParams,
    SortOrder,
    SortParam,
    SortParams,
)
from src.infrastructure.database.models import PlayerModel
from src.infrastructure.database.repositories.players_repository import (
    SqlPlayerRepository,
)
from tests.fixtures.players_fixtures import create_player


class TestSqlPlayerRepository:
    """
    Repository interface for test sql player persistence operations.
    """

    # CRUD operations
    # Get by ID, Get by username, Get by email
    @pytest.mark.asyncio
    async def test_get_player(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get player.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_entity = create_player()

            await repository.save(player_entity)
            await session.commit()

            result = await repository.get_by_id(player_entity.id)
            assert result is not None
            assert result == player_entity

    @pytest.mark.asyncio
    async def test_get_player_by_username(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get player by username.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_entity = create_player()

            await repository.save(player_entity)
            await session.commit()

            result = await repository.get_by_username(player_entity.username)
            assert result is not None
            assert result == player_entity

    @pytest.mark.asyncio
    async def test_get_player_by_email(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get player by email.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_entity = create_player()

            await repository.save(player_entity)
            await session.commit()

            result = await repository.get_by_email(player_entity.email)  # type: ignore[arg-type]
            assert result is not None
            assert result == player_entity

    @pytest.mark.asyncio
    async def test_get_nonexistent_player(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get nonexistent player.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_id = uuid.uuid4()
            result = await repository.get_by_id(player_id)
            assert result is None

    # List with filters, pagination, sorting and search
    @pytest.mark.asyncio
    async def test_list_players_with_filters_and_sorting(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list players with filters and sorting.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            # Create multiple players with different attributes
            players = [
                create_player(
                    username="player1",
                    display_name="Player One",
                    email="player1@example.com",
                ),
                create_player(
                    username="player2",
                    display_name="Player Two",
                    email="player2@example.com",
                ),
                create_player(
                    username="player3",
                    display_name="Player Three",
                    email="player3@example.com",
                ),
            ]
            for player in players:
                await repository.save(player)
            await session.commit()

            # Test listing with filters
            filters = PlayerFilters(display_name_like="Player")
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(
                sorts=[SortParam(field=PlayerSortField.USERNAME, order=SortOrder.ASC)]
            )
            search = SearchParams()
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 3
            assert result.items[0].username == "player1"
            assert result.items[1].username == "player2"
            assert result.items[2].username == "player3"

    @pytest.mark.asyncio
    async def test_list_players_with_pagination(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list players with pagination.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            # Create multiple players to ensure we have more than 1 page of results
            for i in range(15):
                player = create_player(
                    username=f"player{i}",
                    display_name=f"Player {i}",
                    email=f"player{i}@example.com",
                )
                await repository.save(player)
            await session.commit()

            filters = PlayerFilters(display_name_like="Player")
            pagination = PaginationParams(page=2, size=5)
            sort = SortParams(
                sorts=[SortParam(field=PlayerSortField.USERNAME, order=SortOrder.ASC)]
            )
            search = SearchParams()
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 5
            assert result.total >= 15

    @pytest.mark.asyncio
    async def test_list_players_with_search(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list players with search.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            # Create players with different names and games
            players = [
                create_player(
                    username="player1",
                    display_name="Player 1",
                    email="player1@example.com",
                ),
                create_player(
                    username="player2",
                    display_name="Player 2",
                    email="player2@example.com",
                ),
                create_player(
                    username="player3",
                    display_name="Player 3",
                    email="player3@example.com",
                ),
            ]
            for player in players:
                await repository.save(player)
            await session.commit()

            filters = PlayerFilters(display_name_like="Player")
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(
                sorts=[SortParam(field=PlayerSortField.USERNAME, order=SortOrder.ASC)]
            )
            search = SearchParams(query="Player 2")
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 1
            assert result.items[0].username == "player2"

    @pytest.mark.asyncio
    async def test_list_players_with_no_sorts(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list players with no sorts.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            filters = PlayerFilters(username="dupont", display_name_like="Dupont")
            pagination = PaginationParams(page=1, size=10)
            sort: SortParams[PlayerSortField] = SortParams(sorts=[])
            search = SearchParams()
            # Should not raise an error and return results with default sorting
            result = await repository.list(filters, pagination, sort, search)
            assert result is not None

    @pytest.mark.asyncio
    async def test_list_players_with_none_sorts(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list players with none sorts.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            filters = PlayerFilters(username="dupont", display_name_like="Dupont")
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(sorts=None)  # type: ignore
            search = SearchParams()
            # Should not raise an error and return results with default sorting
            result = await repository.list(filters, pagination, sort, search)
            assert result is not None

    # Create
    @pytest.mark.asyncio
    async def test_create_player(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test create player.

        Args:
            test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_entity = create_player()

            await repository.save(player_entity)
            await session.commit()  # Commit les changements avant de les lire

            query = select(PlayerModel).where(PlayerModel.id == player_entity.id)
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            assert model is not None
            assert model.id == player_entity.id
            assert model.username == player_entity.username
            assert model.display_name == player_entity.display_name
            assert model.email == player_entity.email

    # Update
    @pytest.mark.asyncio
    async def test_update_player(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test update player.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_entity = create_player()

            await repository.save(player_entity)
            await session.commit()

            updated_data = {"display_name": "Updated Player Display Name"}
            updated_player = await repository.update(player_entity, updated_data)
            await session.commit()

            assert updated_player.display_name == "Updated Player Display Name"

    # Delete
    @pytest.mark.asyncio
    async def test_delete_player(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test delete player.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_entity = create_player()
            await repository.save(player_entity)
            await session.commit()

            await repository.delete(player_entity.id)
            await session.commit()

            result = await repository.get_by_id(player_entity.id)
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_player(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test delete nonexistent player.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlPlayerRepository(session)
            player_id = uuid.uuid4()
            # Should not raise an error
            await repository.delete(player_id)
            await session.commit()

    # Custom operations
