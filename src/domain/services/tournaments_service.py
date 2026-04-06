import uuid

from src.domain.entities.tournaments import (
    Tournament,
    TournamentFilters,
    TournamentSortField,
)
from src.domain.exceptions.tournaments_exceptions import (
    TournamentAlreadyExistsError,
    TournamentAlreadyStartedError,
    TournamentNotDraftError,
    TournamentNotFoundError,
)
from src.domain.repositories.filters import PaginationParams, SearchParams, SortParams
from src.domain.repositories.paginations import PaginatedResult
from src.domain.repositories.tournaments_repository import AbstractTournamentRepository
from src.domain.utils.enums import TournamentStatus


class TournamentService:
    def __init__(self, repository: AbstractTournamentRepository) -> None:
        self.repository = repository

    # CRUD operations
    async def list_tournaments(
        self,
        filters: TournamentFilters,
        pagination: PaginationParams,
        sort: SortParams[TournamentSortField],
        search: SearchParams,
    ) -> PaginatedResult[Tournament]:
        return await self.repository.list(filters, pagination, sort, search)

    async def get_tournament_by_id(self, tournament_id: uuid.UUID) -> Tournament:
        tournament = await self.repository.get_by_id(tournament_id)
        if tournament is None:
            raise TournamentNotFoundError(details={"id": str(tournament_id)})
        return tournament

    async def create_tournament(self, tournament: Tournament) -> Tournament:
        existing = await self.repository.get_by_name_and_guild(
            tournament.name, tournament.guild_id
        )
        if existing is not None:
            raise TournamentAlreadyExistsError(
                details={"name": tournament.name, "guild_id": str(tournament.guild_id)}
            )
        return await self.repository.save(tournament)

    async def update_tournament(
        self, tournament_id: uuid.UUID, tournament: Tournament
    ) -> Tournament:
        existing = await self.repository.get_by_id(tournament_id)
        # Check if tournament exists
        if existing is None:
            raise TournamentNotFoundError(details={"id": str(tournament_id)})
        # Check if tournament is in DRAFT status
        if existing.status != TournamentStatus.DRAFT:
            raise TournamentNotDraftError(
                details={
                    "id": str(tournament_id),
                    "status": existing.status.value,
                }
            )
        # Check if name is changing and if new name already exists in the same guild
        if (
            tournament.name != existing.name
            and await self.repository.get_by_name_and_guild(
                tournament.name, tournament.guild_id
            )
            is not None
        ):
            raise TournamentAlreadyExistsError(
                details={"name": tournament.name, "guild_id": str(tournament.guild_id)}
            )
        # Update data
        updated_data = {
            "name": tournament.name,
            "description": tournament.description,
            "game": tournament.game,
            "mode": tournament.mode,
            "max_teams": tournament.max_teams,
            "guild_id": tournament.guild_id,
            "min_players_per_team": tournament.min_players_per_team,
            "best_of": tournament.best_of,
        }
        return await self.repository.update(existing, updated_data)

    async def delete_tournament(self, tournament_id: uuid.UUID) -> None:
        existing = await self.repository.get_by_id(tournament_id)
        if existing is None:
            raise TournamentNotFoundError(details={"id": str(tournament_id)})
        await self.repository.delete(tournament_id)

    # Custom operations

    async def open_tournament(self, tournament_id: uuid.UUID) -> Tournament:
        tournament_in_db = await self.repository.get_by_id(tournament_id)
        # Check if tournament exists
        if tournament_in_db is None:
            raise TournamentNotFoundError(details={"id": str(tournament_id)})
        # Check if tournament is in DRAFT status
        if tournament_in_db.status != TournamentStatus.DRAFT:
            raise TournamentNotDraftError(
                details={
                    "id": str(tournament_id),
                    "status": tournament_in_db.status.value,
                }
            )
        # All checks passed, open the tournament
        return await self.repository.open_tournament(tournament_id)

    async def start_tournament(self, tournament_id: uuid.UUID) -> Tournament:
        tournament_in_db = await self.repository.get_by_id(tournament_id)
        if tournament_in_db is None:
            raise TournamentNotFoundError(details={"id": str(tournament_id)})
        if tournament_in_db.status != TournamentStatus.OPEN:
            raise TournamentAlreadyStartedError(
                details={
                    "id": str(tournament_id),
                    "status": tournament_in_db.status.value,
                }
            )
        return await self.repository.start_tournament(tournament_id)
