"""
Test module for test tournaments.
"""

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from src.domain.entities.tournaments import TournamentFilters, TournamentSortField
from src.domain.repositories.filters import (
    PaginationParams,
    SearchParams,
    SortOrder,
    SortParam,
    SortParams,
)
from src.domain.utils.enums import TournamentMode, TournamentStatus
from src.infrastructure.database.models import TournamentModel, TournamentTeamModel
from src.infrastructure.database.repositories.teams_repository import SqlTeamRepository
from src.infrastructure.database.repositories.tournaments_repository import (
    SqlTournamentRepository,
)
from tests.fixtures.teams_fixtures import create_team
from tests.fixtures.tournaments_fixtures import create_tournament, create_tournamentteam


class TestSqlTournamentRepository:
    """
    Repository interface for test sql tournament persistence operations.
    """

    # CRUD operations
    # Get by ID, Get by name and guild
    @pytest.mark.asyncio
    async def test_get_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()

            await repository.save(tournament_entity)
            await session.commit()

            result = await repository.get_by_id(tournament_entity.id)
            assert result is not None
            assert result == tournament_entity

    @pytest.mark.asyncio
    async def test_get_tournament_by_name(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get tournament by name.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()

            await repository.save(tournament_entity)
            await session.commit()

            result = await repository.get_by_name_and_guild(
                tournament_entity.name, tournament_entity.guild_id
            )
            assert result is not None
            assert result == tournament_entity

    @pytest.mark.asyncio
    async def test_get_nonexistent_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test get nonexistent tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_id = uuid.uuid4()
            result = await repository.get_by_id(tournament_id)
            assert result is None

    # List with filters, pagination, sorting and search
    @pytest.mark.asyncio
    async def test_list_tournaments_with_filters_and_sorting(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list tournaments with filters and sorting.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            # Create multiple tournaments with different attributes
            tournaments = [
                create_tournament(
                    name="LoL Tournament",
                    game="League of Legends",
                    mode=TournamentMode.SINGLE_ELIMINATION,
                    guild_id=1,
                ),
                create_tournament(
                    name="CS:GO Tournament",
                    game="Counter-Strike: Global Offensive",
                    mode=TournamentMode.DOUBLE_ELIMINATION,
                    guild_id=1,
                ),
                create_tournament(
                    name="Dota 2 Tournament",
                    game="Dota 2",
                    mode=TournamentMode.ROUND_ROBIN,
                    guild_id=2,
                ),
            ]
            for tournament in tournaments:
                await repository.save(tournament)
            await session.commit()

            # Test listing with filters
            filters = TournamentFilters(guild_id=1)
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(
                sorts=[SortParam(field=TournamentSortField.NAME, order=SortOrder.ASC)]
            )
            search = SearchParams()
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 2
            assert result.items[0].name == "CS:GO Tournament"
            assert result.items[1].name == "LoL Tournament"

    @pytest.mark.asyncio
    async def test_list_tournaments_with_pagination(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list tournaments with pagination.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            # Create multiple tournaments to ensure we have more than 1 page of results
            for i in range(15):
                tournament = create_tournament(name=f"Tournament {i}", guild_id=1)
                await repository.save(tournament)
            await session.commit()

            filters = TournamentFilters(guild_id=1)
            pagination = PaginationParams(page=2, size=5)
            sort = SortParams(
                sorts=[SortParam(field=TournamentSortField.NAME, order=SortOrder.ASC)]
            )
            search = SearchParams()
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 5
            assert result.total >= 15

    @pytest.mark.asyncio
    async def test_list_tournaments_with_search(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list tournaments with search.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            # Create tournaments with different names and games
            tournaments = [
                create_tournament(
                    name="LoL Tournament", game="League of Legends", guild_id=1
                ),
                create_tournament(
                    name="CS:GO Tournament",
                    game="Counter-Strike: Global Offensive",
                    guild_id=1,
                ),
                create_tournament(name="Dota 2 Tournament", game="Dota 2", guild_id=1),
            ]
            for tournament in tournaments:
                await repository.save(tournament)
            await session.commit()

            filters = TournamentFilters(guild_id=1)
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(
                sorts=[SortParam(field=TournamentSortField.NAME, order=SortOrder.ASC)]
            )
            search = SearchParams(query="Dota")
            result = await repository.list(filters, pagination, sort, search)
            assert len(result.items) == 1
            assert result.items[0].name == "Dota 2 Tournament"
            assert result.items[0].game == "Dota 2"

    @pytest.mark.asyncio
    async def test_list_tournaments_with_no_sorts(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list tournaments with no sorts.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            filters = TournamentFilters(guild_id=1)
            pagination = PaginationParams(page=1, size=10)
            sort: SortParams[TournamentSortField] = SortParams(sorts=[])
            search = SearchParams()
            # Should not raise an error and return results with default sorting
            result = await repository.list(filters, pagination, sort, search)
            assert result is not None

    @pytest.mark.asyncio
    async def test_list_tournaments_with_none_sorts(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test list tournaments with none sorts.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            filters = TournamentFilters(guild_id=1)
            pagination = PaginationParams(page=1, size=10)
            sort = SortParams(sorts=None)  # type: ignore
            search = SearchParams()
            # Should not raise an error and return results with default sorting
            result = await repository.list(filters, pagination, sort, search)
            assert result is not None

    # Create
    @pytest.mark.asyncio
    async def test_create_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test create tournament.

        Args:
            test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()

            await repository.save(tournament_entity)
            await session.commit()  # Commit les changements avant de les lire

            query = select(TournamentModel).where(
                TournamentModel.id == tournament_entity.id
            )
            result = await session.execute(query)
            model = result.scalar_one_or_none()
            assert model is not None
            assert model.id == tournament_entity.id
            assert model.guild_id == tournament_entity.guild_id
            assert model.name == tournament_entity.name
            assert model.mode == tournament_entity.mode.value
            assert model.status == tournament_entity.status.value
            assert model.start_date == tournament_entity.start_date
            assert model.end_date == tournament_entity.end_date
            assert model.created_at == tournament_entity.created_at
            assert model.updated_at == tournament_entity.updated_at

    # Update
    @pytest.mark.asyncio
    async def test_update_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test update tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()

            await repository.save(tournament_entity)
            await session.commit()

            updated_data = {"name": "Updated Tournament Name"}
            updated_tournament = await repository.update(
                tournament_entity, updated_data
            )
            await session.commit()

            assert updated_tournament.name == "Updated Tournament Name"

    # Delete
    @pytest.mark.asyncio
    async def test_delete_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test delete tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()
            await repository.save(tournament_entity)
            await session.commit()

            await repository.delete(tournament_entity.id)
            await session.commit()

            result = await repository.get_by_id(tournament_entity.id)
            assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test delete nonexistent tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_id = uuid.uuid4()
            # Should not raise an error
            await repository.delete(tournament_id)
            await session.commit()

    # Custom operations
    # Open tournament
    @pytest.mark.asyncio
    async def test_open_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test open tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()
            await repository.save(tournament_entity)
            await session.commit()
            await repository.open_tournament(tournament_entity.id)
            await session.commit()
            result = await repository.get_by_id(tournament_entity.id)
            assert result is not None
            assert result.status == TournamentStatus.OPEN

    @pytest.mark.asyncio
    async def test_add_team_to_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """
        Execute test open tournament.

        Args:
        test_session_factory: The test_session_factory parameter.
        """
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            team_repository = SqlTeamRepository(session)
            tournament_entity = create_tournament()
            team_entity = create_team()
            tournament_team_entity = create_tournamentteam(
                tournament_id=tournament_entity.id, team_id=team_entity.id
            )
            # tournament part
            await tournament_repository.save(tournament_entity)
            await session.commit()
            await tournament_repository.open_tournament(tournament_entity.id)
            await session.commit()
            result = await tournament_repository.get_by_id(tournament_entity.id)
            assert result is not None
            assert result.status == TournamentStatus.OPEN
            # team part
            await team_repository.save(team_entity)
            await session.commit()
            # tournament team part
            await tournament_repository.save_tournament_membership(
                tournament_team_entity
            )

            query = (
                select(TournamentModel)
                .where(TournamentModel.id == tournament_entity.id)
                .options(
                    selectinload(TournamentModel.registered_teams).selectinload(
                        TournamentTeamModel.team
                    )
                )
            )
            result_query = await session.execute(query)
            model = result_query.scalar_one_or_none()
            assert model is not None
            assert model.id == tournament_entity.id
            assert model.name == tournament_entity.name
            assert len(model.registered_teams) == 1
            team_in_tournament = model.registered_teams[0]
            assert team_in_tournament.tournament_id == tournament_entity.id
            assert team_in_tournament.team_id == team_entity.id
            assert team_in_tournament.team.name == team_entity.name
            assert team_in_tournament.team.tag == team_entity.tag

    async def test_add_team_to_nonexistant_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            team_repository = SqlTeamRepository(session)
            team_entity = create_team()
            tournament_id = uuid.uuid4()

            await team_repository.save(team_entity)
            await session.commit()  # Commit les changements avant de les lire

            await tournament_repository.delete_tournament_membership(
                tournament_id=tournament_id, team_id=team_entity.id
            )
            await session.commit()

    async def test_add_tournament_team_for_nonexistant_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            tournament_entity = create_tournament()
            team_id = uuid.uuid4()

            await tournament_repository.save(tournament_entity)
            await session.commit()  # Commit les changements avant de les lire

            await tournament_repository.delete_tournament_membership(
                tournament_id=tournament_entity.id, team_id=team_id
            )
            await session.commit()

    async def test_remove_rournament_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            team_repository = SqlTeamRepository(session)
            team_entity = create_team()
            tournament_entity = create_tournament()
            tournament_team_entity = create_tournamentteam(
                tournament_id=tournament_entity.id, team_id=team_entity.id
            )

            await tournament_repository.save(tournament_entity)
            await session.commit()  # Commit les changements avant de les lire
            await team_repository.save(team_entity)
            await session.commit()  # Commit les changements avant de les lire
            await tournament_repository.save_tournament_membership(
                tournament_team_entity
            )
            await session.commit()

            await tournament_repository.delete_tournament_membership(
                tournament_id=tournament_entity.id, team_id=team_entity.id
            )
            await session.commit()
            session.expire_all()

            result = await tournament_repository.get_by_id(tournament_entity.id)
            if result:
                assert result.registered_teams == []

    async def test_remove_nonexistant_tournament_member(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            team_id = uuid.uuid4()
            tournament_id = uuid.uuid4()
            # Should not raise an error
            await tournament_repository.delete_tournament_membership(
                team_id=team_id, tournament_id=tournament_id
            )
            await session.commit()

    async def test_remove_tournament_member_team(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            team_repository = SqlTeamRepository(session)
            team_entity = create_team()
            tournament_entity = create_tournament()
            tournament_team_entity = create_tournamentteam(
                tournament_id=tournament_entity.id, team_id=team_entity.id
            )

            await tournament_repository.save(tournament_entity)
            await session.commit()  # Commit les changements avant de les lire
            await team_repository.save(team_entity)
            await session.commit()  # Commit les changements avant de les lire
            await tournament_repository.save_tournament_membership(
                tournament_team_entity
            )
            await session.commit()

            await team_repository.delete(team_entity.id)
            await session.commit()
            session.expire_all()

            result = await tournament_repository.get_by_id(tournament_entity.id)
            if result:
                assert result.registered_teams == []

    async def test_remove_tournament_member_tournament(
        self, test_session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with test_session_factory() as session:
            tournament_repository = SqlTournamentRepository(session)
            team_repository = SqlTeamRepository(session)
            team_entity = create_team()
            tournament_entity = create_tournament()
            tournament_team_entity = create_tournamentteam(
                tournament_id=tournament_entity.id, team_id=team_entity.id
            )

            await tournament_repository.save(tournament_entity)
            await session.commit()  # Commit les changements avant de les lire
            await team_repository.save(team_entity)
            await session.commit()  # Commit les changements avant de les lire
            await tournament_repository.save_tournament_membership(
                tournament_team_entity
            )
            await session.commit()

            await tournament_repository.delete(tournament_entity.id)
            await session.commit()

            result = await team_repository.get_by_id(team_entity.id)
            if result:
                assert result.tournament_entries == []
