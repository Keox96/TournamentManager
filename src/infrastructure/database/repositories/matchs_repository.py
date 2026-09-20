"""
Database infrastructure module.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.matchs import (
    Match,
    MatchFilters,
    MatchPlayer,
    MatchSortField,
    MatchTeam,
)
from src.domain.repositories.matchs_repository import AbstractMatchRepository
from src.domain.utils.enums import MatchStatus
from src.infrastructure.database.models import (
    MatchModel,
    MatchPlayerModel,
    MatchTeamModel,
    PlayerModel,
    TeamModel,
    TeamPlayerModel,
)
from src.infrastructure.database.repositories.base_repository import SqlBaseRepository


class SqlMatchRepository(
    SqlBaseRepository[Match, MatchModel, MatchFilters, MatchSortField],
    AbstractMatchRepository,
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    @property
    def model_class(self) -> type[MatchModel]:
        return MatchModel

    @property
    def sort_field_map(self) -> dict[MatchSortField, Any]:
        return {
            MatchSortField.CREATED_AT: MatchModel.created_at,
            MatchSortField.STATUS: MatchModel.status,
            MatchSortField.START_DATE: MatchModel.created_at,
        }

    @property
    def search_fields(self) -> list[Any]:
        return [MatchModel.status]

    @property
    def load_options(self) -> list[Any]:
        return [
            selectinload(MatchModel.participants)
            .selectinload(MatchTeamModel.team)
            .selectinload(TeamModel.members),
            selectinload(MatchModel.player_performances)
            .selectinload(MatchPlayerModel.player)
            .selectinload(PlayerModel.team_memberships),
        ]

    def to_domain(self, model: MatchModel) -> Match:
        return MatchModel.to_domain(model)

    def from_domain(self, entity: Match) -> MatchModel:
        return MatchModel.from_domain(entity)

    async def create_match(self, match: Match) -> Match:
        model = MatchModel.from_domain(match)
        self.session.add(model)
        await self.session.flush()

        for participant in match.participants:
            participant_model = MatchTeamModel.from_domain(participant)
            participant_model.match_id = model.id
            self.session.add(participant_model)

            if not match.player_performances:
                player_query = select(TeamPlayerModel.player_id).where(
                    TeamPlayerModel.team_id == participant.team_id
                )
                player_result = await self.session.execute(player_query)
                for (player_id,) in player_result.all():
                    self.session.add(
                        MatchPlayerModel(
                            match_id=model.id,
                            player_id=player_id,
                            score=0,
                            kills=0,
                            deaths=0,
                            assists=0,
                            created_at=match.created_at,
                            updated_at=None,
                        )
                    )

        for performance in match.player_performances:
            performance_model = MatchPlayerModel.from_domain(performance)
            performance_model.match_id = model.id
            self.session.add(performance_model)

        await self.session.flush()
        created_match = await self.get_by_id(model.id)
        if created_match is None:
            raise RuntimeError("Created match could not be loaded")
        return created_match

    async def get_by_tournament(self, tournament_id: uuid.UUID) -> list[Match]:
        query = (
            select(MatchModel)
            .where(MatchModel.tournament_id == tournament_id)
            .options(*self.load_options)
            .order_by(MatchModel.round.asc(), MatchModel.created_at.asc())
        )
        result = await self.session.execute(query)
        return [self.to_domain(model) for model in result.scalars().all()]

    async def get_by_tournament_and_round(
        self, tournament_id: uuid.UUID, round_number: int
    ) -> list[Match]:
        query = (
            select(MatchModel)
            .where(
                MatchModel.tournament_id == tournament_id,
                MatchModel.round == round_number,
            )
            .options(*self.load_options)
            .order_by(MatchModel.created_at.asc())
        )
        result = await self.session.execute(query)
        return [self.to_domain(model) for model in result.scalars().all()]

    async def update_match_status(
        self, match_id: uuid.UUID, status: MatchStatus
    ) -> Match | None:
        query = (
            select(MatchModel)
            .where(MatchModel.id == match_id)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        model.status = status.value
        await self.session.flush()
        return self.to_domain(model)

    async def update_match_score(
        self, match_id: uuid.UUID, team_id: uuid.UUID, score: int
    ) -> MatchTeam | None:
        model = await self.session.get(MatchTeamModel, (match_id, team_id))
        if model is None:
            return None

        model.score = score
        await self.session.flush()
        await self.session.refresh(model)
        return MatchTeamModel.to_domain(model)

    async def save_match_result(
        self,
        match_id: uuid.UUID,
        team_results: dict[uuid.UUID, MatchTeam],
        player_scores: dict[uuid.UUID, MatchPlayer],
    ) -> Match | None:
        query = (
            select(MatchModel)
            .where(MatchModel.id == match_id)
            .options(*self.load_options)
        )
        result = await self.session.execute(query)
        match_model = result.scalar_one_or_none()
        if match_model is None:
            return None

        for participant in match_model.participants:
            team_result = team_results[participant.team_id]
            participant.score = team_result.score
            participant.kills = team_result.kills
            participant.deaths = team_result.deaths
            participant.assists = team_result.assists

        player_models = {
            performance.player_id: performance
            for performance in match_model.player_performances
        }
        for player_id, performance in player_scores.items():
            model = player_models[player_id]
            model.score = performance.score
            model.kills = performance.kills
            model.deaths = performance.deaths
            model.assists = performance.assists

        ordered = sorted(
            match_model.participants, key=lambda item: item.score, reverse=True
        )
        previous_score = None
        previous_rank = 0
        for index, participant in enumerate(ordered, start=1):
            if participant.score != previous_score:
                previous_rank = index
                previous_score = participant.score
            participant.rank = previous_rank

        match_model.status = MatchStatus.COMPLETED.value
        await self.session.flush()
        return self.to_domain(match_model)

    async def save_match_team(self, participation: MatchTeam) -> MatchTeam:
        model = MatchTeamModel.from_domain(participation)
        merged = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged)
        return MatchTeamModel.to_domain(merged)

    async def save_match_player(self, performance: MatchPlayer) -> MatchPlayer:
        model = MatchPlayerModel.from_domain(performance)
        merged = await self.session.merge(model)
        await self.session.flush()
        await self.session.refresh(merged)
        return MatchPlayerModel.to_domain(merged)

    async def delete_match(self, match_id: uuid.UUID) -> None:
        model = await self.session.get(MatchModel, match_id)
        if model:
            await self.session.delete(model)
