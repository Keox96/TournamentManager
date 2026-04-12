import uuid
from datetime import UTC, datetime

from src.domain.entities.teams import Team, TeamPlayer
from src.domain.exceptions.players_exceptions import PlayerNotFoundError
from src.domain.exceptions.team_players_exceptions import (
    TeamCaptainAlreadyExistsError,
    TeamPlayerAlreadyExistsError,
    TeamPlayerNotFoundError,
)
from src.domain.exceptions.teams_exceptions import TeamNotFoundError
from src.domain.repositories.players_repository import AbstractPlayerRepository
from src.domain.repositories.teams_repository import AbstractTeamRepository
from src.domain.utils.enums import TeamRole


class TeamPlayerService:
    def __init__(
        self,
        team_repository: AbstractTeamRepository,
        player_repository: AbstractPlayerRepository,
    ) -> None:
        self.team_repository = team_repository
        self.player_repository = player_repository

    async def add_team_member(self, team_member: TeamPlayer) -> Team:
        team = await self.team_repository.get_by_id(team_member.team_id)
        if team is None:
            raise TeamNotFoundError(details={"id": str(team_member.team_id)})
        player = await self.player_repository.get_by_id(team_member.player_id)
        if player is None:
            raise PlayerNotFoundError(details={"id": str(team_member.player_id)})
        if any(m for m in team.members if m.player_id == team_member.player_id):
            raise TeamPlayerAlreadyExistsError(
                details={
                    "team_id": team_member.team_id,
                    "player_id": team_member.player_id,
                }
            )
        if team_member.role == TeamRole.CAPTAIN and team.captain:
            raise TeamCaptainAlreadyExistsError(
                details={"team_id": team_member.team_id}
            )
        team_membership = TeamPlayer(
            player_id=team_member.player_id,
            team_id=team_member.team_id,
            role=team_member.role,
            created_at=datetime.now(UTC).replace(tzinfo=None),
            updated_at=None,
        )
        return await self.team_repository.save_membership(team_membership)

    async def update_team_member(
        self, team_id: uuid.UUID, player_id: uuid.UUID, role_player: TeamRole
    ) -> Team:
        team = await self.team_repository.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(details={"id": str(team_id)})
        player = await self.player_repository.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(details={"id": str(player_id)})
        if not any(m for m in team.members if m.player_id == player_id):
            raise TeamPlayerNotFoundError(
                details={"team_id": team_id, "player_id": player_id}
            )
        if role_player == TeamRole.CAPTAIN and team.captain:
            raise TeamCaptainAlreadyExistsError(details={"team_id": team_id})
        team_membership = [m for m in team.members if m.player_id == player_id][0]
        team_membership.role = role_player
        return await self.team_repository.save_membership(team_membership)

    # Remove team member
    async def remove_team_member(
        self, team_id: uuid.UUID, player_id: uuid.UUID
    ) -> None:
        team = await self.team_repository.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(details={"id": str(team_id)})
        player = await self.player_repository.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(details={"id": str(player_id)})
        if not any(m for m in team.members if m.player_id == player_id):
            raise TeamPlayerNotFoundError(
                details={"team_id": team_id, "player_id": player_id}
            )
        await self.team_repository.delete_membership(
            team_id=team_id, player_id=player_id
        )
