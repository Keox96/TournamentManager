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
    TournamentTeam,
)
from src.domain.utils.enums import TournamentMode, TournamentStatus


class TournamentFiltersRequest(BaseModel):
    """
    Schema representing a tournament filters request payload.
    """

    guild_id: int | None = Field(
        None, description="Identifier of the guild to filter tournaments by"
    )
    status: TournamentStatus | None = Field(
        None, description="Status to filter tournaments by"
    )
    mode: TournamentMode | None = Field(
        None, description="Mode to filter tournaments by"
    )
    game_like: Annotated[str | None, Query(max_length=100)] = Field(
        None, description="Game name to filter tournaments by"
    )
    name_like: Annotated[str | None, Query(max_length=100)] = Field(
        None, description="Name to filter tournaments by"
    )
    max_teams_min: int | None = Field(
        None, description="Minimum number of teams to filter tournaments by"
    )
    max_teams_max: int | None = Field(
        None, description="Maximum number of teams to filter tournaments by"
    )
    min_players_per_team_min: int | None = Field(
        None, description="Minimum number of players per team to filter tournaments by"
    )
    min_players_per_team_max: int | None = Field(
        None, description="Maximum number of players per team to filter tournaments by"
    )
    start_date_from: datetime | None = Field(
        None, description="Start date to filter tournaments by"
    )
    start_date_to: datetime | None = Field(
        None, description="End date to filter tournaments by"
    )
    created_at_from: datetime | None = Field(
        None, description="Creation date from to filter tournaments by"
    )
    created_at_to: datetime | None = Field(
        None, description="Creation date to to filter tournaments by"
    )

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

    id: UUID = Field(..., description="Unique identifier of the tournament")
    guild_id: int = Field(
        ..., description="Identifier of the guild the tournament belongs to"
    )
    name: str = Field(..., description="Name of the tournament")
    game: str = Field(..., description="Game of the tournament")
    mode: TournamentMode = Field(..., description="Mode of the tournament")
    status: TournamentStatus = Field(..., description="Status of the tournament")
    min_players_per_team: int = Field(
        ..., description="Minimum number of players per team"
    )
    max_teams: int = Field(..., description="Maximum number of teams")
    description: str | None = Field(None, description="Description of the tournament")
    best_of: int | None = Field(
        None, description="Maximum number of rounds per match for the tournament"
    )
    start_date: datetime | None = Field(
        None, description="Start date of the tournament"
    )
    end_date: datetime | None = Field(None, description="End date of the tournament")
    created_at: datetime = Field(..., description="Creation date of the tournament")
    updated_at: datetime | None = Field(
        None, description="Last update date of the tournament"
    )
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

    name: str = Field(..., description="Name of the tournament")
    game: str = Field(..., description="Game of the tournament")
    mode: TournamentMode = Field(..., description="Mode of the tournament")
    guild_id: int = Field(
        ..., description="Identifier of the guild the tournament belongs to"
    )
    min_players_per_team: int = Field(
        ..., gt=0, description="Minimum number of players per team"
    )
    max_teams: int = Field(..., gt=0, le=8, description="Maximum number of teams")
    description: str | None = Field(None, description="Description of the tournament")
    best_of: int | None = Field(
        None, description="Maximum number of rounds per match for the tournament"
    )

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


class TournamentUpdateRequest(BaseModel):
    """
    Schema representing a tournament update request payload.
    """

    name: str = Field(..., description="Name of the tournament")
    game: str = Field(..., description="Game of the tournament")
    mode: TournamentMode = Field(..., description="Mode of the tournament")
    guild_id: int = Field(
        ..., description="Identifier of the guild the tournament belongs to"
    )
    min_players_per_team: int = Field(
        ..., gt=0, description="Minimum number of players per team"
    )
    max_teams: int = Field(..., gt=0, le=8, description="Maximum number of teams")
    description: str | None = Field(None, description="Description of the tournament")
    best_of: int | None = Field(
        None, description="Maximum number of rounds per match for the tournament"
    )

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


class AddTeamTournamentRequest(BaseModel):
    tournament_id: UUID = Field(..., description="ID of the tournament")
    team_id: UUID = Field(..., description="ID of the team")

    def to_domain(self) -> TournamentTeam:
        """
        Convert the object to domain.

        Returns:
        The result of the operation.
        """
        return TournamentTeam(
            tournament_id=self.tournament_id,
            team_id=self.team_id,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )


TournamentFiltersQuery = Annotated[TournamentFiltersRequest, Depends()]
TournamentSortQuery = Annotated[TournamentSortRequest, Depends()]
