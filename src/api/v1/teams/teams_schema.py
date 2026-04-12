"""
FastAPI module for team endpoints and schemas.
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi.params import Depends
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator

from src.api.base_schema import BaseSortRequest
from src.api.shared_schema import TeamPlayerResponse
from src.domain.entities.teams import Team, TeamFilters, TeamPlayer, TeamSortField
from src.domain.exceptions.generic_exceptions import EntityValidationError
from src.domain.utils.enums import TeamRole


class TeamResponse(BaseModel):
    """
    Schema representing a team response payload.
    """

    id: uuid.UUID = Field(..., description="Unique identifier of the team")
    name: str = Field(..., description="Name of the team")
    tag: str = Field(..., description="Tag of the team")
    logo_url: str | None = Field(None, description="URL of the team's logo")
    description: str | None = Field(None, description="Description of the team")
    created_at: datetime = Field(..., description="Timestamp when the team was created")
    updated_at: datetime | None = Field(
        None, description="Timestamp when the team was last updated"
    )
    members: list[TeamPlayerResponse] = Field(
        default_factory=list, description="List of team members"
    )
    # tournament_entries: List[UUID] = Field(default_factory=list, description="List of tournament IDs the team is registered in")
    # match_participations: List[UUID] = Field(default_factory=list, description="List of match IDs the team has participated in")

    @classmethod
    def from_domain(cls, team: Team) -> "TeamResponse":
        """
        Create an object from domain.

        Args:
        team: The team parameter.

        Returns:
        The result of the operation.
        """
        return cls(
            id=team.id,
            name=team.name,
            tag=team.tag,
            logo_url=team.logo_url,
            description=team.description,
            created_at=team.created_at,
            updated_at=team.updated_at,
            members=[TeamPlayerResponse.from_domain(m) for m in team.members],
        )


class TeamCreateRequest(BaseModel):
    """
    Schema representing a team create request payload.
    """

    name: str = Field(..., description="Name of the team")
    tag: str = Field(
        ...,
        description="Tag of the team",
        min_length=2,
        max_length=5,
        json_schema_extra={"example": "TA"},
    )
    logo_url: AnyHttpUrl | None = Field(None, description="URL of the team's logo")
    description: str | None = Field(None, description="Description of the team")

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, v: str) -> str:
        if not v.strip():
            raise EntityValidationError(
                message="tag cannot be empty", details={"tag": v}
            )
        if not v.isalnum():
            raise EntityValidationError(
                message="Tag must be alphanumeric", details={"tag": v}
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise EntityValidationError(
                message="name cannot be empty", details={"name": v}
            )
        if not v.replace(" ", "").isalnum():
            raise EntityValidationError(
                message="Name must be alphanumeric", details={"name": v}
            )
        return v

    def to_domain(self) -> Team:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return Team(
            id=uuid.uuid4(),
            name=self.name,
            tag=self.tag,
            logo_url=str(self.logo_url) if self.logo_url is not None else None,
            description=self.description,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


class TeamUpdateRequest(BaseModel):
    name: str = Field(..., description="Name of the team")
    tag: str = Field(
        ...,
        description="Tag of the team",
        min_length=2,
        max_length=5,
        json_schema_extra={"example": "TA"},
    )
    logo_url: AnyHttpUrl | None = Field(None, description="URL of the team's logo")
    description: str | None = Field(None, description="Description of the team")

    @field_validator("tag")
    @classmethod
    def validate_tag(cls, v: str) -> str:
        if not v.strip():
            raise EntityValidationError(
                message="tag cannot be empty", details={"tag": v}
            )
        if not v.isalnum():
            raise EntityValidationError(
                message="Tag must be alphanumeric", details={"tag": v}
            )
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise EntityValidationError(
                message="name cannot be empty", details={"name": v}
            )
        if not v.replace(" ", "").isalnum():
            raise EntityValidationError(
                message="Name must be alphanumeric", details={"name": v}
            )
        return v

    def to_domain(self) -> Team:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return Team(
            id=uuid.uuid4(),
            name=self.name,
            tag=self.tag,
            logo_url=str(self.logo_url) if self.logo_url is not None else None,
            description=self.description,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


class TeamFiltersRequest(BaseModel):
    """
    Schema representing a team filters request payload.
    """

    name_like: str | None = Field(
        None, description="Filter for teams with names containing this value"
    )
    tag_like: str | None = Field(
        None, description="Filter for teams with tags containing this value"
    )
    created_at_from: datetime | None = Field(
        None, description="Filter for teams created after this date"
    )
    created_at_to: datetime | None = Field(
        None, description="Filter for teams created before this date"
    )

    def to_domain(self) -> TeamFilters:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return TeamFilters(
            name_like=self.name_like,
            tag_like=self.tag_like,
            created_at_from=self.created_at_from,
            created_at_to=self.created_at_to,
        )


class TeamSortRequest(BaseSortRequest[TeamSortField]):
    """
    Schema representing a team sort request payload.
    """

    sort_field_class = TeamSortField
    default_sort_field = TeamSortField.CREATED_AT


class TeamAddMemberRequest(BaseModel):
    team_id: uuid.UUID = Field(..., description="The unique identifier of the team")
    player_id: uuid.UUID = Field(
        ..., description="The unique identifier of the player to add"
    )
    role_player: TeamRole = Field(
        default=TeamRole.PLAYER, description="Role of the player in the team"
    )

    def to_domain(self) -> TeamPlayer:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return TeamPlayer(
            team_id=self.team_id,
            player_id=self.player_id,
            role=self.role_player,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


class TeamUpdateMemberRequest(BaseModel):
    role_player: TeamRole = Field(
        default=TeamRole.PLAYER, description="Role of the player in the team"
    )


TeamFiltersQuery = Annotated[TeamFiltersRequest, Depends()]
TeamSortQuery = Annotated[TeamSortRequest, Depends()]
