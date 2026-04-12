import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entities.teams import TeamPlayer
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
