from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from src.api.base_schema import PaginatedResponse, PaginationQuery, SearchQuery
from src.api.dependencies import DbSession
from src.api.exception_schema import ErrorResponse
from src.api.v1.tournaments.tournaments_schema import (
    AddTeamTournamentRequest,
    TournamentCreateRequest,
    TournamentFiltersQuery,
    TournamentResponse,
    TournamentSortQuery,
    TournamentUpdateRequest,
)
from src.domain.services.tournament_teams_service import TournamentTeamService
from src.domain.services.tournaments_service import TournamentService
from src.infrastructure.database.repositories.teams_repository import SqlTeamRepository
from src.infrastructure.database.repositories.tournaments_repository import (
    SqlTournamentRepository,
)

common_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}

tournament_router = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    responses=common_responses,
)


# CRUD operations
# Get by ID and list with filters, pagination, sorting and search
@tournament_router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def list_tournaments(
    session: DbSession,
    filters: TournamentFiltersQuery,
    sort: TournamentSortQuery,
    pagination: PaginationQuery,
    search: SearchQuery,
) -> PaginatedResponse[TournamentResponse]:
    """
    List tournaments with filters, sorting, pagination and search.

    Args:
        session: Database session.
        filters: Tournament filters.
        sort: Sort parameters. Format: field:order — ex: name:asc,created_at:desc
        pagination: Pagination parameters.
        search: Search parameters.

    Returns:
        PaginatedResponse[TournamentResponse]: Paginated list of tournaments.
    """
    repository = SqlTournamentRepository(session)
    service = TournamentService(repository)

    pagination_domain = pagination.to_domain()
    result = await service.list_tournaments(
        filters.to_domain(),
        pagination_domain,
        sort.to_domain(),
        search.to_domain(),
    )

    return PaginatedResponse(
        items=[TournamentResponse.from_domain(t) for t in result.items],
        total=result.total,
        page=pagination_domain.page,
        size=pagination_domain.size,
        total_pages=-(-result.total // pagination_domain.size),
    )


@tournament_router.get(
    "/{tournament_id}",
    status_code=status.HTTP_200_OK,
)
async def get_tournament(
    tournament_id: UUID,
    session: DbSession,
) -> TournamentResponse:
    """
    Retrieve a tournament by its ID.

    Args:
        tournament_id: The unique identifier of the tournament.
        session: Database session.

    Returns:
        TournamentResponse: The details of the requested tournament.

    Raises:
        TournamentNotFoundError: If the tournament is not found.
    """
    repository = SqlTournamentRepository(session)
    service = TournamentService(repository)
    tournament = await service.get_tournament_by_id(tournament_id)
    return TournamentResponse.from_domain(tournament)


# Create
@tournament_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_tournament(
    tournament_data: TournamentCreateRequest,
    session: DbSession,
) -> TournamentResponse:
    """
    Create a new tournament.

    Args:
        tournament_data: The data for the tournament to create.
        session: Database session.

    Returns:
        TournamentResponse: The details of the created tournament.
    """
    repository = SqlTournamentRepository(session)
    service = TournamentService(repository)
    tournament = await service.create_tournament(tournament_data.to_domain())
    return TournamentResponse.from_domain(tournament)


# Update
@tournament_router.put(
    "/{tournament_id}",
    status_code=status.HTTP_200_OK,
)
async def update_tournament(
    tournament_id: UUID,
    tournament_data: TournamentUpdateRequest,
    session: DbSession,
) -> TournamentResponse:
    """
    Update an existing tournament.

    Args:
        tournament_id: The unique identifier of the tournament to update.
        tournament_data: The updated data for the tournament.
        session: Database session.

    Returns:
        TournamentResponse: The details of the updated tournament.

    Raises:
        TournamentNotFoundError: If the tournament is not found.
    """
    repository = SqlTournamentRepository(session)
    service = TournamentService(repository)
    tournament = await service.update_tournament(
        tournament_id, tournament_data.to_domain()
    )
    return TournamentResponse.from_domain(tournament)


# Delete
@tournament_router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(
    tournament_id: UUID,
    session: DbSession,
) -> None:
    """
    Delete a tournament by its ID.

    Args:
        tournament_id: The unique identifier of the tournament to delete.
        session: Database session.

    Returns:
        None

    Raises:
        TournamentNotFoundError: If the tournament is not found.
    """
    repository = SqlTournamentRepository(session)
    service = TournamentService(repository)
    await service.delete_tournament(tournament_id)


# Custom operations
# Open tournament
@tournament_router.post(
    "/{tournament_id}/open",
    status_code=status.HTTP_200_OK,
)
async def open_tournament(
    tournament_id: UUID,
    session: DbSession,
) -> TournamentResponse:
    """
    Open a tournament by its ID.

    Args:
        tournament_id: The unique identifier of the tournament to open.
        session: Database session.

    Returns:
        TournamentResponse: The details of the opened tournament.

    Raises:
        TournamentNotFoundError: If the tournament is not found.
        TournamentAlreadyOpenedError: If the tournament is already opened.
        TournamentAlreadyStartedError: If the tournament is already started.
    """
    repository = SqlTournamentRepository(session)
    service = TournamentService(repository)
    tournament = await service.open_tournament(tournament_id)
    return TournamentResponse.from_domain(tournament)


@tournament_router.post(
    "/teams",
    status_code=status.HTTP_201_CREATED,
)
async def add_team_to_tournament(
    request: AddTeamTournamentRequest,
    session: DbSession,
) -> TournamentResponse:
    """ """
    tournament_repository = SqlTournamentRepository(session)
    team_repository = SqlTeamRepository(session)
    service = TournamentTeamService(
        tournament_repository=tournament_repository, team_repository=team_repository
    )
    tournament = await service.add_team_to_tournament(request.to_domain())
    return TournamentResponse.from_domain(tournament)


@tournament_router.delete(
    "{tournament_id}/teams/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_team_to_tournament(
    session: DbSession,
    tournament_id: UUID,
    team_id: UUID,
) -> None:
    tournament_repository = SqlTournamentRepository(session)
    team_repository = SqlTeamRepository(session)
    service = TournamentTeamService(
        tournament_repository=tournament_repository, team_repository=team_repository
    )
    await service.remove_team_from_tournament(
        tournament_id=tournament_id, team_id=team_id
    )
