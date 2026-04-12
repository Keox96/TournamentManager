"""
Domain service layer containing business logic.
"""

import uuid

from src.domain.entities.teams import Team, TeamFilters, TeamSortField
from src.domain.exceptions.teams_exceptions import (
    TeamNameAlreadyExistsError,
    TeamNotFoundError,
    TeamTagAlreadyExistsError,
)
from src.domain.repositories.filters import PaginationParams, SearchParams, SortParams
from src.domain.repositories.paginations import PaginatedResult
from src.domain.repositories.teams_repository import AbstractTeamRepository


class TeamService:
    def __init__(self, team_repository: AbstractTeamRepository) -> None:
        self.team_repository = team_repository

    # CRUD operations
    async def list_teams(
        self,
        filters: TeamFilters,
        pagination: PaginationParams,
        sort: SortParams[TeamSortField],
        search: SearchParams,
    ) -> PaginatedResult[Team]:
        return await self.team_repository.list(filters, pagination, sort, search)

    async def get_team_by_id(self, team_id: uuid.UUID) -> Team:
        team = await self.team_repository.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(details={"id": str(team_id)})
        return team

    async def create_team(self, team: Team) -> Team:
        existing_name = await self.team_repository.get_by_name(team.name)
        if existing_name is not None:
            raise TeamNameAlreadyExistsError(details={"name": team.name})
        existing_tag = await self.team_repository.get_by_tag(team.tag)
        if existing_tag is not None:
            raise TeamTagAlreadyExistsError(details={"tag": team.tag})
        return await self.team_repository.save(team)

    async def update_team(self, team_id: uuid.UUID, team: Team) -> Team:
        existing = await self.team_repository.get_by_id(team_id)
        # Check if team exists
        if existing is None:
            raise TeamNotFoundError(details={"id": str(team_id)})
        # Check if name is changing and if new name already exists
        if (
            team.name != existing.name
            and await self.team_repository.get_by_name(team.name) is not None
        ):
            raise TeamNameAlreadyExistsError(details={"name": team.name})
        # Check if tag is changing and if new tag already exists
        if (
            team.tag != existing.tag
            and await self.team_repository.get_by_tag(team.tag) is not None
        ):
            raise TeamTagAlreadyExistsError(details={"tag": team.tag})
        # Update data
        updated_data = {
            "name": team.name,
            "tag": team.tag,
            "logo_url": team.logo_url,
            "description": team.description,
        }
        return await self.team_repository.update(existing, updated_data)

    async def delete_team(self, team_id: uuid.UUID) -> None:
        existing = await self.team_repository.get_by_id(team_id)
        if existing is None:
            raise TeamNotFoundError(details={"id": str(team_id)})
        await self.team_repository.delete(team_id)
