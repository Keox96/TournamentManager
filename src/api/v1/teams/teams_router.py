"""
FastAPI module for team endpoints and schemas.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from src.api.base_schema import PaginatedResponse, PaginationQuery, SearchQuery
from src.api.dependencies import DbSession
from src.api.exception_schema import ErrorResponse
from src.api.v1.teams.teams_schema import (
    TeamCreateRequest,
    TeamFiltersQuery,
    TeamResponse,
    TeamSortQuery,
    TeamUpdateRequest,
)
from src.domain.services.teams_service import TeamService
from src.infrastructure.database.repositories.teams_repository import SqlTeamRepository

common_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}

team_router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses=common_responses,
)


# CRUD operations
# Get by ID and list with filters, pagination, sorting and search
@team_router.get(
    "/",
    response_model=PaginatedResponse[TeamResponse],
    status_code=status.HTTP_200_OK,
)
async def list_teams(
    session: DbSession,
    filters: TeamFiltersQuery,
    sort: TeamSortQuery,
    pagination: PaginationQuery,
    search: SearchQuery,
) -> PaginatedResponse[TeamResponse]:
    """
    List teams with filters, sorting, pagination and search.

    Args:
        session: Database session.
        filters: Player filters.
        sort: Sort parameters. Format: field:order — ex: name:asc,created_at:desc
        pagination: Pagination parameters.
        search: Search parameters.

    Returns:
        PaginatedResponse[TeamResponse]: Paginated list of teams.
    """
    repository = SqlTeamRepository(session)
    service = TeamService(repository)

    pagination_domain = pagination.to_domain()
    result = await service.list_teams(
        filters.to_domain(),
        pagination_domain,
        sort.to_domain(),
        search.to_domain(),
    )

    return PaginatedResponse(
        items=[TeamResponse.from_domain(t) for t in result.items],
        total=result.total,
        page=pagination_domain.page,
        size=pagination_domain.size,
        total_pages=-(-result.total // pagination_domain.size),
    )


@team_router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
)
async def get_team(
    team_id: UUID,
    session: DbSession,
) -> TeamResponse:
    """
    Retrieve a team by their ID.

    Args:
        team_id: The unique identifier of the team.
        session: Database session.

    Returns:
        TeamResponse: The details of the team.

    Raises:
        TeamNotFoundError: If the team is not found.
    """
    repository = SqlTeamRepository(session)
    service = TeamService(repository)
    team = await service.get_team_by_id(team_id)
    return TeamResponse.from_domain(team)


# Create
@team_router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    team_data: TeamCreateRequest,
    session: DbSession,
) -> TeamResponse:
    """
    Create a new team.

    Args:
        team_data: The data for the team to create.
        session: Database session.

    Returns:
        TeamResponse: The details of the created team.

    Raises:
        TeamNameAlreadyExistsError: If a team with the same name already exists.
        TeamTagAlreadyExistsError: If a team with the same tag already exists.
    """
    repository = SqlTeamRepository(session)
    service = TeamService(repository)
    team = await service.create_team(team_data.to_domain())
    return TeamResponse.from_domain(team)


# Update
@team_router.put(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
)
async def update_team(
    team_id: UUID,
    team_data: TeamUpdateRequest,
    session: DbSession,
) -> TeamResponse:
    """
    Update an existing team.

    Args:
        team_id: The unique identifier of the team to update.
        team_data: The updated data for the team.
        session: Database session.

    Returns:
        TeamResponse: The details of the updated team.

    Raises:
        TeamNotFoundError: If the team is not found.
        TeamNameAlreadyExistsError: If a team with the same name already exists.
        TeamTagAlreadyExistsError: If a team with the same tag already exists.
    """
    repository = SqlTeamRepository(session)
    service = TeamService(repository)
    team = await service.update_team(team_id, team_data.to_domain())
    return TeamResponse.from_domain(team)


# Delete
@team_router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    session: DbSession,
) -> None:
    """
    Delete a team by its ID.

    Args:
        team_id: The unique identifier of the team to delete.
        session: Database session.

    Returns:
        None

    Raises:
        TeamNotFoundError: If the team is not found.
    """
    repository = SqlTeamRepository(session)
    service = TeamService(repository)
    await service.delete_team(team_id)
