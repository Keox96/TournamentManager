"""
FastAPI module for tournament endpoints and schemas.
"""

import uuid
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from pydantic import BaseModel, Field

from src.api.base_schema import BaseSortRequest
from src.domain.entities.tournaments import (
    Tournament,
    TournamentFilters,
    TournamentSortField,
)
from src.domain.utils.enums import TournamentMode, TournamentStatus


class TournamentFiltersRequest(BaseModel):
    """
    Schema representing a tournament filters request payload.
    """

    guild_id: int | None = None
    status: TournamentStatus | None = None
    mode: TournamentMode | None = None
    game_like: Annotated[str | None, Query(max_length=100)] = None
    name_like: Annotated[str | None, Query(max_length=100)] = None
    max_teams_min: int | None = None
    max_teams_max: int | None = None
    min_players_per_team_min: int | None = None
    min_players_per_team_max: int | None = None
    start_date_from: datetime | None = None
    start_date_to: datetime | None = None
    created_at_from: datetime | None = None
    created_at_to: datetime | None = None

    def to_domain(self) -> TournamentFilters:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return TournamentFilters(
            guild_id=self.guild_id,
            status=self.status,
            mode=self.mode,
            game_like=self.game_like,
            name_like=self.name_like,
            max_teams_min=self.max_teams_min,
            max_teams_max=self.max_teams_max,
            min_players_per_team_min=self.min_players_per_team_min,
            min_players_per_team_max=self.min_players_per_team_max,
            start_date_from=self.start_date_from,
            start_date_to=self.start_date_to,
            created_at_from=self.created_at_from,
            created_at_to=self.created_at_to,
        )


class TournamentSortRequest(BaseSortRequest[TournamentSortField]):
    """
    Schema representing a tournament sort request payload.
    """

    sort_field_class = TournamentSortField
    default_sort_field = TournamentSortField.CREATED_AT


class TournamentResponse(BaseModel):
    """
    Schema representing a tournament response payload.
    """

    id: UUID
    guild_id: int
    name: str
    game: str
    mode: TournamentMode
    status: TournamentStatus
    min_players_per_team: int
    max_teams: int
    description: str | None
    best_of: int | None
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime
    updated_at: datetime | None
    # registered_teams: list[UUID] | None
    # matches: list[UUID] | None

    @classmethod
    def from_domain(cls, tournament: Tournament) -> "TournamentResponse":
        """
        Create an object from domain.

        Args:
        tournament: The tournament parameter.

        Returns:
        The result of the operation.
        """
        return cls(
            id=tournament.id,
            guild_id=tournament.guild_id,
            name=tournament.name,
            game=tournament.game,
            mode=tournament.mode,
            status=tournament.status,
            min_players_per_team=tournament.min_players_per_team,
            max_teams=tournament.max_teams,
            description=tournament.description,
            best_of=tournament.best_of,
            start_date=tournament.start_date,
            end_date=tournament.end_date,
            created_at=tournament.created_at,
            updated_at=tournament.updated_at,
        )


class TournamentCreateRequest(BaseModel):
    """
    Schema representing a tournament create request payload.
    """

    name: str
    game: str
    mode: TournamentMode
    guild_id: int
    min_players_per_team: int = Field(..., gt=0)
    max_teams: int = Field(..., gt=0, le=8)
    description: str | None = None
    best_of: int | None = None

    def to_domain(self) -> Tournament:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return Tournament(
            id=uuid.uuid4(),
            guild_id=self.guild_id,
            name=self.name,
            game=self.game,
            mode=self.mode,
            status=TournamentStatus.DRAFT,
            min_players_per_team=self.min_players_per_team,
            max_teams=self.max_teams,
            description=self.description,
            best_of=self.best_of,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


TournamentFiltersQuery = Annotated[TournamentFiltersRequest, Depends()]
TournamentSortQuery = Annotated[TournamentSortRequest, Depends()]
