"""
Test module for test teams.
"""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.entities.teams import TeamFilters, TeamSortField
from src.domain.repositories.filters import (
    PaginationParams,
    SearchParams,
    SortOrder,
    SortParam,
    SortParams,
)
from src.infrastructure.database.models import TeamModel
from src.infrastructure.database.repositories.teams_repository import SqlTeamRepository
from tests.fixtures.teams_fixtures import create_team


class TestSqlTeamRepository:
    """
    Repository interface for test sql team persistence operations.
    """

    # CRUD operations
    # Get by ID, Get by username, Get by email
    @pytest.mark.asyncio
    async def test_get_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get team.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_entity = create_team()

            await repository.save(team_entity)
            await session.commit()

            result = await repository.get_by_id(team_entity.id)
            assert result is not None
            assert result == team_entity

    @pytest.mark.asyncio
    async def test_get_team_by_name(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get team by name.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_entity = create_team()

            await repository.save(team_entity)
            await session.commit()

            result = await repository.get_by_name(team_entity.name)
            assert result is not None
            assert result == team_entity

    @pytest.mark.asyncio
    async def test_get_team_by_tag(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get team by tag.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_entity = create_team()

            await repository.save(team_entity)
            await session.commit()

            result = await repository.get_by_tag(team_entity.tag)
            assert result is not None
            assert result == team_entity

    @pytest.mark.asyncio
    async def test_get_nonexistent_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get nonexistent team.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_id = uuid.uuid4()
            result = await repository.get_by_id(team_id)
            assert result is None

    # List with filters, pagination, sorting and search
    @pytest.mark.asyncio
    async def test_list_teams_with_filters_and_sorting(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list teams with filters and sorting.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            # Create multiple teams with different attributes
            teams = [
                create_team(
                    name="Team 1",
                    tag="T1",
                ),
                create_team(
                    name="Team 2",
                    tag="T2",
                ),
                create_team(
                    name="Team 3",
                    tag="T3",
                ),
            ]
            for team in teams:
                await repository.save(team)
            await session.commit()

            # Test listing with filters
            filters = TeamFilters(name_like="Team")
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(
                sorts=[SortParam(field=TeamSortField.NAME, order=SortOrder.ASC)]
            )
            search = SearchParams()
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 3
            assert result.items[0].name == "Team 1"
            assert result.items[1].name == "Team 2"
            assert result.items[2].name == "Team 3"

    @pytest.mark.asyncio
    async def test_list_teams_with_pagination(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list teams with pagination.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            # Create multiple teams to ensure we have more than 1 page of results
            for i in range(15):
                team = create_team(
                    name=f"Team {i}",
                    tag=f"T{i}",
                )
                await repository.save(team)
            await session.commit()

            filters = TeamFilters(name_like="Team")
            pagination = PaginationParams(page=2, size=5)
            sort = SortParams(
                sorts=[SortParam(field=TeamSortField.NAME, order=SortOrder.ASC)]
            )
            search = SearchParams()
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 5
            assert result.total >= 15

    @pytest.mark.asyncio
    async def test_list_teams_with_search(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list teams with search.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            # Create teams with different names and tags
            teams = [
                create_team(
                    name="Team 1",
                    tag="T1",
                ),
                create_team(
                    name="Team 2",
                    tag="T2",
                ),
                create_team(
                    name="Team 3",
                    tag="T3",
                ),
            ]
            for team in teams:
                await repository.save(team)
            await session.commit()

            filters = TeamFilters(name_like="Team")
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(
                sorts=[SortParam(field=TeamSortField.NAME, order=SortOrder.ASC)]
            )
            search = SearchParams(query="Team 2")
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 1
            assert result.items[0].name == "Team 2"

    @pytest.mark.asyncio
    async def test_list_teams_with_no_sorts(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list teams with no sorts.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            filters = TeamFilters(name_like="Team", tag_like="T")
            pagination = PaginationParams(page=1, size=10)
            sort: SortParams[TeamSortField] = SortParams(sorts=[])
            search = SearchParams()
            # Should not raise an error and return results with default sorting
            result = await repository.list(filters, pagination, sort, search)
            assert result is not None

    @pytest.mark.asyncio
    async def test_list_teams_with_none_sorts(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list teams with none sorts.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            filters = TeamFilters(name_like="Team", tag_like="T")
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(sorts=None)  # type: ignore
            search = SearchParams()
            # Should not raise an error and return results with default sorting
            result = await repository.list(filters, pagination, sort, search)
            assert result is not None

    # Create
    @pytest.mark.asyncio
    async def test_create_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test create team.

        Args:
            test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_entity = create_team()

            await repository.save(team_entity)
            await session.commit()  # Commit les changements avant de les lire

            query = select(TeamModel).where(TeamModel.id == team_entity.id)
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            assert model is not None
            assert model.id == team_entity.id
            assert model.name == team_entity.name
            assert model.tag == team_entity.tag

    # Update
    @pytest.mark.asyncio
    async def test_update_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test update team.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_entity = create_team()

            await repository.save(team_entity)
            await session.commit()

            updated_data = {"name": "Updated Team Name"}
            updated_team = await repository.update(team_entity, updated_data)
            await session.commit()

            assert updated_team.name == "Updated Team Name"

    # Delete
    @pytest.mark.asyncio
    async def test_delete_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test delete team.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_entity = create_team()
            await repository.save(team_entity)
            await session.commit()

            await repository.delete(team_entity.id)
            await session.commit()

            result = await repository.get_by_id(team_entity.id)
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test delete nonexistent team.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTeamRepository(session)
            team_id = uuid.uuid4()
            # Should not raise an error
            await repository.delete(team_id)
            await session.commit()

    # Custom operations
