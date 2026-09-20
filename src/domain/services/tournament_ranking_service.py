"""Tournament ranking rules for each supported tournament mode."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.domain.utils.enums import MatchStatus, TournamentMode

if TYPE_CHECKING:
    from collections.abc import Callable
    from uuid import UUID

    from src.domain.entities.matchs import Match
    from src.domain.entities.tournaments import Tournament


@dataclass
class TournamentStanding:
    """Computed final standing for one tournament team."""

    team_id: UUID
    rank: int = 0
    points: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    score_for: int = 0
    score_against: int = 0
    opponents: set[UUID] = field(default_factory=set)
    beaten_opponents: set[UUID] = field(default_factory=set)
    drawn_opponents: set[UUID] = field(default_factory=set)

    @property
    def score_difference(self) -> int:
        return self.score_for - self.score_against


class TournamentRankingService:
    """Calculate final rankings from completed match results."""

    def calculate(
        self, tournament: Tournament, matches: list[Match]
    ) -> dict[UUID, TournamentStanding]:
        standings = {
            team.team_id: TournamentStanding(team_id=team.team_id)
            for team in tournament.registered_teams
        }
        completed_matches = [
            match for match in matches if match.status == MatchStatus.COMPLETED
        ]

        for match in completed_matches:
            self._accumulate_match(standings, match)

        if tournament.mode in {
            TournamentMode.SINGLE_ELIMINATION,
            TournamentMode.DOUBLE_ELIMINATION,
        }:
            self._rank_elimination(standings, completed_matches)
        elif tournament.mode == TournamentMode.ROUND_ROBIN:
            self._rank_league(standings, head_to_head=True)
        else:
            self._rank_swiss(standings)
        return standings

    @staticmethod
    def _accumulate_match(
        standings: dict[UUID, TournamentStanding], match: Match
    ) -> None:
        participants = match.participants
        for participant in participants:
            standing = standings[participant.team_id]
            standing.score_for += participant.score
            standing.score_against += sum(
                other.score
                for other in participants
                if other.team_id != participant.team_id
            )

        if len(participants) == 2:
            first, second = participants
            first_standing = standings[first.team_id]
            second_standing = standings[second.team_id]
            first_standing.opponents.add(second.team_id)
            second_standing.opponents.add(first.team_id)
            if first.score == second.score:
                first_standing.draws += 1
                second_standing.draws += 1
                first_standing.points += 1
                second_standing.points += 1
                first_standing.drawn_opponents.add(second.team_id)
                second_standing.drawn_opponents.add(first.team_id)
            else:
                winner = max(participants, key=lambda participant: participant.score)
                loser = min(participants, key=lambda participant: participant.score)
                standings[winner.team_id].wins += 1
                standings[loser.team_id].losses += 1
                standings[winner.team_id].points += 3
                standings[winner.team_id].beaten_opponents.add(loser.team_id)

    @staticmethod
    def _rank_elimination(
        standings: dict[UUID, TournamentStanding], matches: list[Match]
    ) -> None:
        if not matches:
            return
        final = max(matches, key=lambda match: match.round)
        TournamentRankingService._rank_final(standings, final)

        max_round = max(match.round for match in matches)
        TournamentRankingService._rank_eliminated_teams(standings, matches, max_round)

        next_rank = (
            max((standing.rank for standing in standings.values()), default=0) + 1
        )
        for standing in standings.values():
            if standing.rank == 0:
                standing.rank = next_rank

    @staticmethod
    def _rank_final(standings: dict[UUID, TournamentStanding], final: Match) -> None:
        winner = final.winner
        if winner is None:
            return
        standings[winner.team_id].rank = 1
        for participant in final.participants:
            if participant.team_id != winner.team_id:
                standings[participant.team_id].rank = 2

    @staticmethod
    def _rank_eliminated_teams(
        standings: dict[UUID, TournamentStanding],
        matches: list[Match],
        max_round: int,
    ) -> None:
        for match in matches:
            rank = 2 ** (max_round - match.round) + 1
            for participant in match.participants:
                if participant.rank != 1 and standings[participant.team_id].rank == 0:
                    standings[participant.team_id].rank = rank

    def _rank_league(
        self, standings: dict[UUID, TournamentStanding], head_to_head: bool
    ) -> None:
        def key(standing: TournamentStanding) -> tuple[int, int, int, int]:
            direct_points = (
                sum(
                    standings[opponent].points for opponent in standing.beaten_opponents
                )
                if head_to_head
                else 0
            )
            return (
                standing.points,
                direct_points,
                standing.score_difference,
                standing.score_for,
            )

        self._assign_competition_ranks(
            sorted(standings.values(), key=key, reverse=True), key
        )

    def _rank_swiss(self, standings: dict[UUID, TournamentStanding]) -> None:
        buchholz = {
            team_id: sum(standings[opponent].points for opponent in standing.opponents)
            for team_id, standing in standings.items()
        }
        sonneborn = {
            team_id: sum(
                standings[opponent].points for opponent in standing.beaten_opponents
            )
            + sum(
                standings[opponent].points / 2 for opponent in standing.drawn_opponents
            )
            for team_id, standing in standings.items()
        }
        ordered = sorted(
            standings.values(),
            key=lambda standing: (
                standing.points,
                buchholz[standing.team_id],
                sonneborn[standing.team_id],
                standing.score_difference,
                standing.score_for,
            ),
            reverse=True,
        )
        self._assign_competition_ranks(
            ordered,
            lambda standing: (
                standing.points,
                buchholz[standing.team_id],
                sonneborn[standing.team_id],
                standing.score_difference,
                standing.score_for,
            ),
        )

    @staticmethod
    def _assign_competition_ranks(
        ordered: list[TournamentStanding],
        key: Callable[[TournamentStanding], tuple[int | float, ...]],
    ) -> None:
        previous = None
        for index, standing in enumerate(ordered, start=1):
            current = key(standing)
            if current != previous:
                standing.rank = index
                previous = current
            else:
                standing.rank = ordered[index - 2].rank
