"""
FastAPI module for player endpoints and schemas.
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel, EmailStr

from src.api.base_schema import BaseSortRequest
from src.domain.entities.players import Player, PlayerFilters, PlayerSortField


class PlayerResponse(BaseModel):
    """
    Schema representing a player response payload.
    """

    id: UUID
    username: str
    display_name: str
    email: EmailStr | None = None
    icon_url: str | None = None
    created_at: datetime
    updated_at: datetime | None
    # registered_teams: list[UUID] | None
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
        )


class PlayerCreateRequest(BaseModel):
    """
    Schema representing a player create request payload.
    """

    username: str
    display_name: str
    email: EmailStr | None = None
    icon_url: str | None = None

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

    username: str
    display_name: str
    email: EmailStr | None = None
    icon_url: str | None = None

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

    username: str | None = None
    display_name_like: str | None = None
    email_like: str | None = None

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
        )


class PlayerSortRequest(BaseSortRequest[PlayerSortField]):
    """
    Schema representing a player sort request payload.
    """

    sort_field_class = PlayerSortField
    default_sort_field = PlayerSortField.CREATED_AT


PlayerFiltersQuery = Annotated[PlayerFiltersRequest, Depends()]
PlayerSortQuery = Annotated[PlayerSortRequest, Depends()]
