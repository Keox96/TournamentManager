from uuid import UUID

from src.domain.entities.tournaments import Tournament, TournamentTeam
from src.domain.exceptions.teams_exceptions import TeamNotFoundError
from src.domain.exceptions.tournament_teams_exception import TournamentPlayerAlreadyRegisteredError, TournamentTeamNotEnoughPlayersError
from src.domain.exceptions.tournaments_exceptions import TournamentFullError, TournamentNotFoundError, TournamentNotOpenError
from src.domain.repositories.teams_repository import AbstractTeamRepository
from src.domain.repositories.tournaments_repository import AbstractTournamentRepository
from src.domain.utils.enums import TournamentStatus


class TournamentTeamService:
    def __init__(
        self,
        tournament_repository: AbstractTournamentRepository,
        team_repository: AbstractTeamRepository,
    ):
        self.tournament_repository = tournament_repository
        self.team_repository = team_repository

    async def add_team_to_tournament(
        self, tournament_team: TournamentTeam
    ) -> Tournament: 
        # check tournament exists
        tournament_exists = await self.tournament_repository.get_by_id(tournament_team.tournament_id)
        if not tournament_exists:
            raise TournamentNotFoundError(details={"id":tournament_team.tournament_id})
        # check tournament open status
        if not tournament_exists.is_open_for_registration:
            raise TournamentNotOpenError(details={"status": tournament_exists.status})
        # check tournament not full
        if tournament_exists.is_full:
            raise TournamentFullError()
        # check team exists
        team_exists = await self.team_repository.get_by_id(tournament_team.team_id)
        # check team exists
        if not team_exists:
            raise TeamNotFoundError(details={"id":tournament_team.team_id})
        # check team has enough players
        if len(team_exists.members) < tournament_exists.min_players_per_team:
            raise TournamentTeamNotEnoughPlayersError(details={"team_size": len(team_exists.members), "min_tournament_team_size": tournament_exists.min_players_per_team})
        # check a player is not in multiple teams
        registered_player_ids = {
            m.player_id
            for entry in tournament_exists.registered_teams
            if entry.team
            for m in entry.team.members
        }
        team_player_ids = {m.player_id for m in team_exists.members}
        if registered_player_ids & team_player_ids:
            raise TournamentPlayerAlreadyRegisteredError(details={
                "player_ids": list(registered_player_ids & team_player_ids)
            })
        return await self.tournament_repository.save_tournament_membership(tournament_team)

    async def remove_team_from_tournament(
        self, tournament_id: UUID, team_id: UUID
    ) -> None: ...
        # check tournament exists
        # check team exists
        # check team subscribed to the tournament
        # check tournament not empty
        # check team exists
