"""
Domain service layer containing business logic.
"""

import uuid
from typing import TYPE_CHECKING

from src.domain.entities.matchs import Match, MatchPlayer, MatchTeam
from src.domain.entities.tournaments import Tournament
from src.domain.repositories.matchs_repository import AbstractMatchRepository
from src.domain.repositories.tournaments_repository import AbstractTournamentRepository
from src.domain.services.match_strategy import get_match_strategy
from src.domain.services.tournament_ranking_service import TournamentRankingService
from src.domain.utils.enums import MatchStatus, TournamentMode, TournamentStatus

if TYPE_CHECKING:
    from src.domain.services.match_strategy.base import AbstractMatchStrategy


class MatchService:
    def __init__(
        self,
        match_repository: AbstractMatchRepository,
        tournament_repository: AbstractTournamentRepository | None = None,
    ):
        self.match_repository = match_repository
        self.tournament_repository = tournament_repository
        self.ranking_service = TournamentRankingService()

    async def generate_matchs(self, tournament: Tournament) -> Tournament:
        """Generate the tournament matches according to its selected mode."""
        strategy: AbstractMatchStrategy = get_match_strategy(tournament.mode)
        generated_matches = strategy.generate_matches(tournament)
        if tournament.mode in {
            TournamentMode.SINGLE_ELIMINATION,
            TournamentMode.DOUBLE_ELIMINATION,
        }:
            generated_matches = [
                match for match in generated_matches if match.round == 1
            ]
        tournament.matches = generated_matches

        for match in tournament.matches:
            await self.match_repository.create_match(match)

        return tournament

    async def get_next_matches(self, tournament: Tournament) -> list[Match]:
        """Return the matches that are currently playable in a tournament."""
        if tournament.status == TournamentStatus.COMPLETED:
            return []

        matches = await self.match_repository.get_by_tournament(tournament.id)
        return self._select_current_matches(matches)

    @staticmethod
    def _select_current_matches(matches: list[Match]) -> list[Match]:
        active_matches = [
            match for match in matches if match.status == MatchStatus.IN_PROGRESS
        ]
        if active_matches:
            return active_matches

        pending_matches = [
            match for match in matches if match.status == MatchStatus.PENDING
        ]
        if not pending_matches:
            return []

        current_round = min(match.round for match in pending_matches)
        return [match for match in pending_matches if match.round == current_round]

    async def complete_match(
        self,
        match_id: uuid.UUID,
        team_ids: set[uuid.UUID],
        player_scores: dict[uuid.UUID, MatchPlayer],
    ) -> Match:
        match = await self.match_repository.get_by_id(match_id)
        if match is None:
            raise ValueError("Match not found")
        if match.status == MatchStatus.COMPLETED:
            raise ValueError("Match is already completed")

        tournament = await self._get_tournament(match.tournament_id)
        team_results = self._build_team_results(match, team_ids, player_scores)
        if (
            tournament is not None
            and tournament.mode
            in {
                TournamentMode.SINGLE_ELIMINATION,
                TournamentMode.DOUBLE_ELIMINATION,
            }
            and len({result.score for result in team_results.values()})
            < len(team_results)
        ):
            raise ValueError("Elimination matches cannot end in a draw")

        completed = await self.match_repository.save_match_result(
            match_id, team_results, player_scores
        )
        if completed is None:
            raise ValueError("Match not found")

        round_matches = await self.match_repository.get_by_tournament_and_round(
            completed.tournament_id, completed.round
        )
        if self._round_is_complete(round_matches) and self._uses_elimination(
            tournament
        ):
            await self._generate_next_round(completed, round_matches)

        await self._complete_tournament_if_finished(completed.tournament_id)

        return completed

    @staticmethod
    def _build_team_results(
        match: Match,
        team_ids: set[uuid.UUID],
        player_scores: dict[uuid.UUID, MatchPlayer],
    ) -> dict[uuid.UUID, MatchTeam]:
        participant_ids = {participant.team_id for participant in match.participants}
        if team_ids != participant_ids:
            raise ValueError("A team entry is required for every participating team")

        match_player_ids = {
            performance.player_id for performance in match.player_performances
        }
        if set(player_scores) != match_player_ids:
            raise ValueError("A performance is required for every participating player")

        player_teams: dict[uuid.UUID, set[uuid.UUID]] = {}
        for performance in match.player_performances:
            memberships = (
                performance.player.team_memberships if performance.player else []
            )
            team_ids = {
                membership.team_id
                for membership in memberships
                if membership.team_id in participant_ids
            }
            player_teams[performance.player_id] = team_ids

        if set(player_teams) != set(player_scores) or any(
            len(team_ids) != 1 for team_ids in player_teams.values()
        ):
            raise ValueError(
                "Inconsistent scores: every player must belong to one participating team"
            )

        team_results = {
            team_id: MatchTeam(
                match_id=match.id,
                team_id=team_id,
                created_at=match.created_at,
                updated_at=None,
            )
            for team_id in participant_ids
        }
        for player_id, performance in player_scores.items():
            team_id = next(iter(player_teams[player_id]))
            team_result = team_results[team_id]
            team_result.score += performance.score
            team_result.kills += performance.kills
            team_result.deaths += performance.deaths
            team_result.assists += performance.assists
        return team_results

    async def _get_tournament(self, tournament_id: uuid.UUID) -> Tournament | None:
        if self.tournament_repository is None:
            return None
        return await self.tournament_repository.get_by_id(tournament_id)

    @staticmethod
    def _round_is_complete(round_matches: list[Match]) -> bool:
        return bool(round_matches) and all(
            current.status == MatchStatus.COMPLETED for current in round_matches
        )

    @staticmethod
    def _uses_elimination(tournament: Tournament | None) -> bool:
        return tournament is not None and tournament.mode in {
            TournamentMode.SINGLE_ELIMINATION,
            TournamentMode.DOUBLE_ELIMINATION,
        }

    async def _complete_tournament_if_finished(self, tournament_id: uuid.UUID) -> None:
        if self.tournament_repository is None:
            return
        all_matches = await self.match_repository.get_by_tournament(tournament_id)
        if not all_matches or not all(
            current.status == MatchStatus.COMPLETED for current in all_matches
        ):
            return
        tournament = await self.tournament_repository.get_by_id(tournament_id)
        if tournament is not None:
            standings = self.ranking_service.calculate(tournament, all_matches)
            await self.tournament_repository.complete_tournament(
                tournament_id, standings
            )

    async def _generate_next_round(
        self, completed: Match, round_matches: list[Match]
    ) -> None:
        if len(round_matches) < 2:
            return

        winners = [match.winner for match in round_matches]
        winner_ids = [winner.team_id for winner in winners if winner is not None]
        if len(winner_ids) < 2:
            return

        for index in range(0, len(winner_ids) - 1, 2):
            next_match = Match(
                id=uuid.uuid4(),
                tournament_id=completed.tournament_id,
                status=MatchStatus.PENDING,
                round=completed.round + 1,
                created_at=completed.created_at,
                updated_at=None,
            )
            next_match.participants = [
                MatchTeam(
                    match_id=next_match.id,
                    team_id=team_id,
                    created_at=completed.created_at,
                    updated_at=None,
                )
                for team_id in winner_ids[index : index + 2]
            ]
            await self.match_repository.create_match(next_match)
