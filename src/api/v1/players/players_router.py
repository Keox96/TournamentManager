"""
FastAPI module for player endpoints and schemas.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from src.api.base_schema import PaginatedResponse, PaginationQuery, SearchQuery
from src.api.dependencies import DbSession
from src.api.exception_schema import ErrorResponse
from src.api.v1.players.players_schema import (
    PlayerCreateRequest,
    PlayerFiltersQuery,
    PlayerResponse,
    PlayerSortQuery,
    PlayerUpdateRequest,
)
from src.domain.services.players_service import PlayerService
from src.infrastructure.database.repositories.players_repository import (
    SqlPlayerRepository,
)

common_responses: dict[int | str, dict[str, Any]] = {
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_409_CONFLICT: {"model": ErrorResponse},
    status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
}

player_router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses=common_responses,
)


# CRUD operations
# Get by ID and list with filters, pagination, sorting and search
@player_router.get(
    "/",
    response_model=PaginatedResponse[PlayerResponse],
    status_code=status.HTTP_200_OK,
)
async def list_players(
    session: DbSession,
    filters: PlayerFiltersQuery,
    sort: PlayerSortQuery,
    pagination: PaginationQuery,
    search: SearchQuery,
) -> PaginatedResponse[PlayerResponse]:
    """
    List players with filters, sorting, pagination and search.

    Args:
        session: Database session.
        filters: Player filters.
        sort: Sort parameters. Format: field:order — ex: name:asc,created_at:desc
        pagination: Pagination parameters.
        search: Search parameters.

    Returns:
        PaginatedResponse[PlayerResponse]: Paginated list of players.
    """
    repository = SqlPlayerRepository(session)
    service = PlayerService(repository)

    pagination_domain = pagination.to_domain()
    result = await service.list_players(
        filters.to_domain(),
        pagination_domain,
        sort.to_domain(),
        search.to_domain(),
    )

    return PaginatedResponse(
        items=[PlayerResponse.from_domain(p) for p in result.items],
        total=result.total,
        page=pagination_domain.page,
        size=pagination_domain.size,
        total_pages=-(-result.total // pagination_domain.size),
    )


@player_router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    status_code=status.HTTP_200_OK,
)
async def get_player(
    player_id: UUID,
    session: DbSession,
) -> PlayerResponse:
    """
    Retrieve a player by their ID.

    Args:
        player_id: The unique identifier of the player.
        session: Database session.

    Returns:
        PlayerResponse: The details of the requested player.

    Raises:
        PlayerNotFoundError: If the player is not found.
    """
    repository = SqlPlayerRepository(session)
    service = PlayerService(repository)
    player = await service.get_player_by_id(player_id)
    return PlayerResponse.from_domain(player)


# Create
@player_router.post(
    "/",
    response_model=PlayerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_player(
    player_data: PlayerCreateRequest,
    session: DbSession,
) -> PlayerResponse:
    """
    Create a new player.

    Args:
        player_data: The data for the player to create.
        session: Database session.

    Returns:
        PlayerResponse: The details of the created player.
    """
    repository = SqlPlayerRepository(session)
    service = PlayerService(repository)
    player = await service.create_player(player_data.to_domain())
    return PlayerResponse.from_domain(player)


# Update
@player_router.put(
    "/{player_id}",
    response_model=PlayerResponse,
    status_code=status.HTTP_200_OK,
)
async def update_player(
    player_id: UUID,
    player_data: PlayerUpdateRequest,
    session: DbSession,
) -> PlayerResponse:
    """
    Update an existing player.

    Args:
        player_id: The unique identifier of the player to update.
        player_data: The updated data for the player.
        session: Database session.

    Returns:
        PlayerResponse: The details of the updated player.

    Raises:
        PlayerNotFoundError: If the player is not found.
    """
    repository = SqlPlayerRepository(session)
    service = PlayerService(repository)
    player = await service.update_player(player_id, player_data.to_domain())
    return PlayerResponse.from_domain(player)


# Delete
@player_router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(
    player_id: UUID,
    session: DbSession,
) -> None:
    """
    Delete a player by its ID.

    Args:
        player_id: The unique identifier of the player to delete.
        session: Database session.

    Returns:
        None

    Raises:
        PlayerNotFoundError: If the player is not found.
    """
    repository = SqlPlayerRepository(session)
    service = PlayerService(repository)
    await service.delete_player(player_id)
