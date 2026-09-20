

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entities.matchs import Match, MatchPlayer, MatchTeam
from src.domain.utils.enums import MatchStatus


class MatchTeamResponse(BaseModel):
    match_id: uuid.UUID
    team_id: uuid.UUID
    score: int = 0
    rank: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, participation: MatchTeam) -> "MatchTeamResponse":
        return cls(
            match_id=participation.match_id,
            team_id=participation.team_id,
            score=participation.score,
            rank=participation.rank,
            created_at=participation.created_at,
            updated_at=participation.updated_at,
        )


class MatchPlayerResponse(BaseModel):
    match_id: uuid.UUID
    player_id: uuid.UUID
    score: int = 0
    rank: int | None = None
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, performance: MatchPlayer) -> "MatchPlayerResponse":
        return cls(
            match_id=performance.match_id,
            player_id=performance.player_id,
            score=performance.score,
            rank=performance.rank,
            kills=performance.kills,
            deaths=performance.deaths,
            assists=performance.assists,
            created_at=performance.created_at,
            updated_at=performance.updated_at,
        )


class MatchResponse(BaseModel):
    """
    Schema representing a match response payload.
    """

    id: uuid.UUID
    tournament_id: uuid.UUID
    status: MatchStatus
    round: int
    participants: list[MatchTeamResponse] = Field(default_factory=list)
    player_performances: list[MatchPlayerResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, match: Match) -> "MatchResponse":
        """
        Create an object from domain.

        Args:
        match: The match parameter.

        Returns:
        The result of the operation.
        """
        return cls(
            id=match.id,
            tournament_id=match.tournament_id,
            status=match.status,
            round=match.round,
            participants=[MatchTeamResponse.from_domain(p) for p in match.participants],
            player_performances=[MatchPlayerResponse.from_domain(pl) for pl in match.player_performances],
        )


class TeamMatchResultRequest(BaseModel):
    team_id: uuid.UUID
    score: int = Field(..., ge=0)


class PlayerMatchResultRequest(BaseModel):
    player_id: uuid.UUID
    score: int = Field(..., ge=0)
    kills: int = Field(0, ge=0)
    deaths: int = Field(0, ge=0)
    assists: int = Field(0, ge=0)


class MatchResultRequest(BaseModel):
    teams: list[TeamMatchResultRequest]
    players: list[PlayerMatchResultRequest]
