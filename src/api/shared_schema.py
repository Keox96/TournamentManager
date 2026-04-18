import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entities.teams import TeamPlayer
from src.domain.entities.tournaments import TournamentTeam
from src.domain.utils.enums import TeamRole


class TeamPlayerResponse(BaseModel):
    player_id: uuid.UUID = Field(..., description="Unique identifier of the player")
    team_id: uuid.UUID = Field(..., description="Unique identifier of the team")
    role: TeamRole = Field(..., description="Unique identifier of the player")
    created_at: datetime = Field(
        ..., description="Timestamp when the membership to the team was created"
    )
    updated_at: datetime | None = Field(
        None, description="Last update date of the membership to the team"
    )

    @classmethod
    def from_domain(cls, membership: TeamPlayer) -> "TeamPlayerResponse":
        return cls(
            player_id=membership.player_id,
            team_id=membership.team_id,
            role=membership.role,
            created_at=membership.created_at,
            updated_at=membership.updated_at,
        )


class TournamentTeamResponse(BaseModel):
    tournament_id: uuid.UUID = Field(
        ..., description="Unique identifier of the tournament"
    )
    team_id: uuid.UUID = Field(..., description="Unique identifier of the team")
    score: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    draws: int = Field(default=0)
    rank: int | None = Field(None)
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, tournament_team: TournamentTeam) -> "TournamentTeamResponse":
        return cls(
            tournament_id=tournament_team.tournament_id,
            team_id=tournament_team.team_id,
            score=tournament_team.score,
            wins=tournament_team.wins,
            losses=tournament_team.losses,
            draws=tournament_team.draws,
            rank=tournament_team.rank,
            created_at=tournament_team.created_at,
            updated_at=tournament_team.updated_at,
        )
