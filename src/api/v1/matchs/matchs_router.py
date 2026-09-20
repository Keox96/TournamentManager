from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.api.dependencies import DbSession
from src.api.exception_schema import COMMON_RESPONSES
from src.api.v1.matchs.matchs_schema import (
    MatchResultRequest,
    MatchResponse,
)
from src.domain.entities.matchs import MatchPlayer
from src.domain.services.matchs_service import MatchService
from src.infrastructure.database.repositories.matchs_repository import SqlMatchRepository
from src.infrastructure.database.repositories.tournaments_repository import SqlTournamentRepository

MATCH_NOT_FOUND = "Match not found"


match_router = APIRouter(
    prefix="/matchs",
    tags=["matchs"],
    responses=COMMON_RESPONSES,
)


@match_router.get(
    "/tournament/{tournament_id}",
    status_code=status.HTTP_200_OK,
)
async def list_tournament_matches(
    tournament_id: UUID,
    session: DbSession,
) -> list[MatchResponse]:
    repository = SqlMatchRepository(session)
    matches = await repository.get_by_tournament(tournament_id)
    return [MatchResponse.from_domain(match) for match in matches]


@match_router.get(
    "/tournament/{tournament_id}/next",
    status_code=status.HTTP_200_OK,
)
async def list_next_tournament_matches(
    tournament_id: UUID,
    session: DbSession,
) -> list[MatchResponse]:
    tournament_repository = SqlTournamentRepository(session)
    tournament = await tournament_repository.get_by_id(tournament_id)
    if tournament is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found")

    service = MatchService(SqlMatchRepository(session), tournament_repository)
    matches = await service.get_next_matches(tournament)
    return [MatchResponse.from_domain(match) for match in matches]


@match_router.get(
    "/{match_id}",
    status_code=status.HTTP_200_OK,
)
async def get_match(match_id: UUID, session: DbSession) -> MatchResponse:
    repository = SqlMatchRepository(session)
    match = await repository.get_by_id(match_id)
    if match is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=MATCH_NOT_FOUND)
    return MatchResponse.from_domain(match)


@match_router.put(
    "/{match_id}/result",
    status_code=status.HTTP_200_OK,
)
async def complete_match(
    match_id: UUID,
    request: MatchResultRequest,
    session: DbSession,
) -> MatchResponse:
    repository = SqlMatchRepository(session)
    tournament_repository = SqlTournamentRepository(session)
    service = MatchService(repository, tournament_repository)
    now = datetime.now(UTC).replace(tzinfo=None)
    player_scores = {
        result.player_id: MatchPlayer(
            match_id=match_id,
            player_id=result.player_id,
            score=result.score,
            kills=result.kills,
            deaths=result.deaths,
            assists=result.assists,
            created_at=now,
            updated_at=None,
        )
        for result in request.players
    }
    try:
        match = await service.complete_match(
            match_id,
            {result.team_id: result.score for result in request.teams},
            player_scores,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return MatchResponse.from_domain(match)