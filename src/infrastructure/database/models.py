"""
SQLAlchemy ORM models for Tournament Manager.
These belong to the infrastructure layer and are kept strictly separate
from the domain entities defined in domain/entities.py.

Mappers are defined at the bottom of this file so that the domain layer
never imports from here (dependency rule: domain ← application ← infrastructure).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from src.domain.entities.players import Player
from src.domain.entities.teams import Team
from src.domain.entities.tournaments import Tournament
from src.domain.utils.enums import (
    TournamentMode,
    TournamentStatus,
)

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """
    Model representing a base.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.now(UTC).replace(tzinfo=None),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )


# ---------------------------------------------------------------------------
# ORM Models
# ---------------------------------------------------------------------------


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    icon_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # relationships
    # team_memberships: Mapped[list[TeamPlayerModel]] = relationship(
    #     "TeamPlayerModel",
    #     back_populates="player",
    #     cascade="all, delete-orphan",
    # )
    # match_performances: Mapped[list[MatchPlayerModel]] = relationship(
    #     "MatchPlayerModel",
    #     back_populates="player",
    #     cascade="all, delete-orphan",
    # )

    def __repr__(self) -> str:
        return f"<PlayerModel id={self.id} username={self.username!r}>"

    @classmethod
    def from_domain(cls, player: Player) -> PlayerModel:
        return cls(
            id=player.id,
            username=player.username,
            display_name=player.display_name,
            email=player.email,
            icon_url=player.icon_url,
            created_at=player.created_at,
            updated_at=player.updated_at,
        )

    @classmethod
    def to_domain(cls, model: PlayerModel) -> Player:
        return Player(
            id=model.id,
            username=model.username,
            display_name=model.display_name,
            email=model.email,
            icon_url=model.icon_url,
            # team_memberships=[
            #     TeamPlayerModel.to_domain(m) for m in model.team_memberships
            # ],
            # match_performances=[
            #     MatchPlayerModel.to_domain(m) for m in model.match_performances
            # ],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    tag: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # relationships
    # members: Mapped[list[TeamPlayerModel]] = relationship(
    #     "TeamPlayerModel",
    #     back_populates="team",
    #     cascade="all, delete-orphan",
    # )
    # tournament_entries: Mapped[list[TournamentTeamModel]] = relationship(
    #     "TournamentTeamModel",
    #     back_populates="team",
    # )
    # match_participations: Mapped[list[MatchTeamModel]] = relationship(
    #     "MatchTeamModel",
    #     back_populates="team",
    # )

    def __repr__(self) -> str:
        return f"<TeamModel id={self.id} name={self.name!r}>"

    @classmethod
    def from_domain(cls, team: Team) -> TeamModel:
        return cls(
            id=team.id,
            name=team.name,
            tag=team.tag,
            description=team.description,
            logo_url=team.logo_url,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @classmethod
    def to_domain(cls, model: TeamModel) -> Team:
        return Team(
            id=model.id,
            name=model.name,
            tag=model.tag,
            description=model.description,
            logo_url=model.logo_url,
            # members=[TeamPlayerModel.to_domain(m) for m in model.members],
            # tournament_entries=[
            #     TournamentTeamModel.to_domain(t) for t in model.tournament_entries
            # ],
            # match_participations=[
            #     MatchTeamModel.to_domain(m) for m in model.match_participations
            # ],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# class TeamPlayerModel(Base):
#     """
#     Join table between players and teams.
#     Composite PK: (player_id, team_id).
#     """

#     __tablename__ = "team_players"

#     player_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("players.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     team_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("teams.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     role: Mapped[str] = mapped_column(
#         String(255), nullable=False, default=TeamRole.PLAYER.value
#     )

#     # relationships
#     player: Mapped[PlayerModel] = relationship(
#         "PlayerModel", back_populates="team_memberships"
#     )
#     team: Mapped[TeamModel] = relationship("TeamModel", back_populates="members")

#     def __repr__(self) -> str:
#         return f"<TeamPlayerModel player={self.player_id} team={self.team_id} role={self.role!r}>"

#     @classmethod
#     def from_domain(cls, membership: TeamPlayer) -> TeamPlayerModel:
#         return cls(
#             player_id=membership.player_id,
#             team_id=membership.team_id,
#             role=membership.role.value,
#             rank=membership.rank,
#             score=membership.score,
#             created_at=membership.created_at,
#             updated_at=membership.updated_at,
#         )

#     @classmethod
#     def to_domain(cls, model: TeamPlayerModel) -> TeamPlayer:
#         return TeamPlayer(
#             player_id=model.player_id,
#             team_id=model.team_id,
#             role=TeamRole(model.role),
#             rank=model.rank,
#             score=model.score,
#             player=PlayerModel.to_domain(model.player) if model.player else None,
#             team=TeamModel.to_domain(model.team) if model.team else None,
#             created_at=model.created_at,
#             updated_at=model.updated_at,
#         )


class TournamentModel(Base):
    """
    Model representing a tournament model.
    """

    __tablename__ = "tournaments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mode: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    game: Mapped[str] = mapped_column(String(255), nullable=False)
    min_players_per_team: Mapped[int] = mapped_column(Integer, nullable=False)
    max_teams: Mapped[int] = mapped_column(Integer, nullable=False)
    best_of: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    # relationships
    # matches: Mapped[list[MatchModel]] = relationship(
    #     "MatchModel",
    #     back_populates="tournament",
    #     cascade="all, delete-orphan",
    # )
    # registered_teams: Mapped[list[TournamentTeamModel]] = relationship(
    #     "TournamentTeamModel",
    #     back_populates="tournament",
    #     cascade="all, delete-orphan",
    # )

    def __repr__(self) -> str:
        """
        Return a string representation of the object.

        Returns:
        The result of the operation.
        """
        return (
            f"<TournamentModel id={self.id} name={self.name!r} status={self.status!r}>"
        )

    @classmethod
    def from_domain(cls, tournament: Tournament) -> TournamentModel:
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
            mode=tournament.mode.value,
            status=tournament.status.value,
            description=tournament.description,
            game=tournament.game,
            min_players_per_team=tournament.min_players_per_team,
            max_teams=tournament.max_teams,
            best_of=tournament.best_of,
            start_date=tournament.start_date,
            end_date=tournament.end_date,
            created_at=tournament.created_at,
            updated_at=tournament.updated_at,
        )

    @classmethod
    def to_domain(cls, model: TournamentModel) -> Tournament:
        """
        Convert the object to domain.

        Args:
        model: The model parameter.

        Returns:
        The result of the operation.
        """
        return Tournament(
            id=model.id,
            guild_id=model.guild_id,
            name=model.name,
            mode=TournamentMode(model.mode),
            status=TournamentStatus(model.status),
            description=model.description,
            game=model.game,
            min_players_per_team=model.min_players_per_team,
            max_teams=model.max_teams,
            best_of=model.best_of,
            start_date=model.start_date,
            end_date=model.end_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            # registered_teams=[
            #     TournamentTeamModel.to_domain(t) for t in model.registered_teams
            # ],
            # matches=[MatchModel.to_domain(m) for m in model.matches],
        )


# class TournamentTeamModel(Base):
#     """
#     Join table between tournaments and teams (standings).
#     Composite PK: (tournament_id, team_id).
#     """

#     __tablename__ = "tournament_teams"

#     tournament_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("tournaments.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     team_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("teams.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

#     # relationships
#     tournament: Mapped[TournamentModel] = relationship(
#         "TournamentModel", back_populates="registered_teams"
#     )
#     team: Mapped[TeamModel] = relationship(
#         "TeamModel", back_populates="tournament_entries"
#     )

#     def __repr__(self) -> str:
#         return (
#             f"<TournamentTeamModel tournament={self.tournament_id} "
#             f"team={self.team_id} rank={self.rank}>"
#         )

#     @classmethod
#     def from_domain(cls, enrollment: TournamentTeam) -> TournamentTeamModel:
#         return cls(
#             tournament_id=enrollment.tournament_id,
#             team_id=enrollment.team_id,
#             score=enrollment.score,
#             wins=enrollment.wins,
#             losses=enrollment.losses,
#             draws=enrollment.draws,
#             rank=enrollment.rank,
#             created_at=enrollment.created_at,
#             updated_at=enrollment.updated_at,
#         )

#     @classmethod
#     def to_domain(cls, model: TournamentTeamModel) -> TournamentTeam:
#         return TournamentTeam(
#             tournament_id=model.tournament_id,
#             team_id=model.team_id,
#             score=model.score,
#             wins=model.wins,
#             losses=model.losses,
#             draws=model.draws,
#             rank=model.rank,
#             tournament=TournamentModel.to_domain(model.tournament)
#             if model.tournament
#             else None,
#             team=TeamModel.to_domain(model.team) if model.team else None,
#             created_at=model.created_at,
#             updated_at=model.updated_at,
#         )


# class MatchModel(Base):
#     __tablename__ = "matches"

#     id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
#     tournament_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("tournaments.id", ondelete="CASCADE"),
#         nullable=False,
#     )
#     status: Mapped[str] = mapped_column(String(255), nullable=False)
#     round: Mapped[int] = mapped_column(Integer, nullable=False)

#     __table_args__ = (Index("matches_tournament_id_index", "tournament_id"),)

#     # relationships
#     tournament: Mapped[TournamentModel] = relationship(
#         "TournamentModel", back_populates="matches"
#     )
#     participants: Mapped[list[MatchTeamModel]] = relationship(
#         "MatchTeamModel",
#         back_populates="match",
#         cascade="all, delete-orphan",
#     )
#     player_performances: Mapped[list[MatchPlayerModel]] = relationship(
#         "MatchPlayerModel",
#         back_populates="match",
#         cascade="all, delete-orphan",
#     )

#     def __repr__(self) -> str:
#         return f"<MatchModel id={self.id} round={self.round} status={self.status!r}>"

#     @classmethod
#     def from_domain(cls, match: Match) -> MatchModel:
#         return cls(
#             id=match.id,
#             tournament_id=match.tournament_id,
#             status=match.status.value,
#             round=match.round,
#             created_at=match.created_at,
#             updated_at=match.updated_at,
#         )

#     @classmethod
#     def to_domain(cls, model: MatchModel) -> Match:
#         return Match(
#             id=model.id,
#             tournament_id=model.tournament_id,
#             status=MatchStatus(model.status),
#             round=model.round,
#             participants=[MatchTeamModel.to_domain(p) for p in model.participants],
#             player_performances=[
#                 MatchPlayerModel.to_domain(p) for p in model.player_performances
#             ],
#             created_at=model.created_at,
#             updated_at=model.updated_at,
#         )


# class MatchTeamModel(Base):
#     """
#     Join table between matches and teams (per-match results).
#     Composite PK: (match_id, team_id).
#     """

#     __tablename__ = "match_teams"

#     match_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("matches.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     team_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("teams.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

#     # relationships
#     match: Mapped[MatchModel] = relationship(
#         "MatchModel", back_populates="participants"
#     )
#     team: Mapped[TeamModel] = relationship(
#         "TeamModel", back_populates="match_participations"
#     )

#     def __repr__(self) -> str:
#         return f"<MatchTeamModel match={self.match_id} team={self.team_id} rank={self.rank}>"

#     @classmethod
#     def from_domain(cls, participation: MatchTeam) -> MatchTeamModel:
#         return cls(
#             match_id=participation.match_id,
#             team_id=participation.team_id,
#             rank=participation.rank,
#             score=participation.score,
#             created_at=participation.created_at,
#             updated_at=participation.updated_at,
#         )

#     @classmethod
#     def to_domain(cls, model: MatchTeamModel) -> MatchTeam:
#         return MatchTeam(
#             match_id=model.match_id,
#             team_id=model.team_id,
#             rank=model.rank,
#             score=model.score,
#             match=MatchModel.to_domain(model.match) if model.match else None,
#             team=TeamModel.to_domain(model.team) if model.team else None,
#             created_at=model.created_at,
#             updated_at=model.updated_at,
#         )


# class MatchPlayerModel(Base):
#     """
#     Join table between matches and players (per-match individual performance).
#     Composite PK: (match_id, player_id).
#     """

#     __tablename__ = "match_players"

#     match_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("matches.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     player_id: Mapped[uuid.UUID] = mapped_column(
#         Uuid,
#         ForeignKey("players.id", ondelete="CASCADE"),
#         primary_key=True,
#     )
#     rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
#     score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     kills: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     deaths: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
#     assists: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

#     # relationships
#     match: Mapped[MatchModel] = relationship(
#         "MatchModel", back_populates="player_performances"
#     )
#     player: Mapped[PlayerModel] = relationship(
#         "PlayerModel", back_populates="match_performances"
#     )

#     def __repr__(self) -> str:
#         return f"<MatchPlayerModel match={self.match_id} player={self.player_id} score={self.score} rank={self.rank}>"

#     @classmethod
#     def from_domain(cls, performance: MatchPlayer) -> MatchPlayerModel:
#         return cls(
#             match_id=performance.match_id,
#             player_id=performance.player_id,
#             rank=performance.rank,
#             score=performance.score,
#             kills=performance.kills,
#             deaths=performance.deaths,
#             assists=performance.assists,
#             created_at=performance.created_at,
#             updated_at=performance.updated_at,
#         )

#     @classmethod
#     def to_domain(cls, model: MatchPlayerModel) -> MatchPlayer:
#         return MatchPlayer(
#             match_id=model.match_id,
#             player_id=model.player_id,
#             rank=model.rank,
#             score=model.score,
#             kills=model.kills,
#             deaths=model.deaths,
#             assists=model.assists,
#             match=MatchModel.to_domain(model.match) if model.match else None,
#             player=PlayerModel.to_domain(model.player) if model.player else None,
#             created_at=model.created_at,
#             updated_at=model.updated_at,
#         )
