"""
FastAPI module for player endpoints and schemas.
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, EmailStr, Field

from src.api.base_schema import BaseSortRequest
from src.api.shared_schema import TeamPlayerResponse
from src.domain.entities.players import Player, PlayerFilters, PlayerSortField


class PlayerResponse(BaseModel):
    """
    Schema representing a player response payload.
    """

    id: UUID = Field(..., description="Unique identifier of the player")
    username: str = Field(..., description="Username of the player")
    display_name: str = Field(..., description="Display name of the player")
    email: EmailStr | None = Field(None, description="Email address of the player")
    icon_url: str | None = Field(None, description="URL of the player's icon")
    created_at: datetime = Field(..., description="Creation date of the player")
    updated_at: datetime | None = Field(
        None, description="Last update date of the player"
    )
    team_memberships: list[TeamPlayerResponse] = Field(default_factory=list)
    # matches: list[UUID] | None

    @classmethod
    def from_domain(cls, player: Player) -> "PlayerResponse":
        """
        Create an object from domain.

        Args:
        player: The player parameter.

        Returns:
        The result of the operation.
        """
        return cls(
            id=player.id,
            username=player.username,
            display_name=player.display_name,
            email=player.email,
            icon_url=player.icon_url,
            created_at=player.created_at,
            updated_at=player.updated_at,
            team_memberships=[
                TeamPlayerResponse.from_domain(m) for m in player.team_memberships
            ],
        )


class PlayerCreateRequest(BaseModel):
    """
    Schema representing a player create request payload.
    """

    username: str = Field(..., description="Username of the player")
    display_name: str = Field(..., description="Display name of the player")
    email: EmailStr | None = Field(None, description="Email address of the player")
    icon_url: str | None = Field(None, description="URL of the player's icon")

    def to_domain(self) -> Player:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return Player(
            id=uuid.uuid4(),
            username=self.username,
            display_name=self.display_name or self.username,
            email=self.email,
            icon_url=self.icon_url,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


class PlayerUpdateRequest(BaseModel):
    """
    Schema representing a player update request payload.
    """

    username: str = Field(..., description="Username of the player")
    display_name: str = Field(..., description="Display name of the player")
    email: EmailStr | None = Field(None, description="Email address of the player")
    icon_url: str | None = Field(None, description="URL of the player's icon")

    def to_domain(self) -> Player:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return Player(
            id=uuid.uuid4(),
            username=self.username,
            display_name=self.display_name,
            email=self.email,
            icon_url=self.icon_url,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


class PlayerFiltersRequest(BaseModel):
    """
    Schema representing a player filters request payload.
    """

    username: str | None = Field(None, description="Exact match for player's username")
    display_name_like: str | None = Field(
        None, description="Partial match for player's display name"
    )
    email_like: str | None = Field(
        None, description="Partial match for player's email address"
    )
    created_at_from: datetime | None = Field(
        None, description="Filter for players created after this date"
    )
    created_at_to: datetime | None = Field(
        None, description="Filter for players created before this date"
    )

    def to_domain(self) -> PlayerFilters:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return PlayerFilters(
            username=self.username,
            display_name_like=self.display_name_like,
            email_like=self.email_like,
            created_at_from=self.created_at_from,
            created_at_to=self.created_at_to,
        )


class PlayerSortRequest(BaseSortRequest[PlayerSortField]):
    """
    Schema representing a player sort request payload.
    """

    sort_field_class = PlayerSortField
    default_sort_field = PlayerSortField.CREATED_AT


PlayerFiltersQuery = Annotated[PlayerFiltersRequest, Depends()]
PlayerSortQuery = Annotated[PlayerSortRequest, Depends()]
