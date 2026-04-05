"""
Test module for tournaments fixtures.
"""

import uuid
from datetime import datetime

from src.domain.entities.tournaments import Tournament
from src.domain.utils.enums import TournamentMode, TournamentStatus


def create_tournament(
    *,
    id: uuid.UUID | None = None,
    guild_id: int = 123456789,
    name: str = "Dupont",
    mode: TournamentMode = TournamentMode.SINGLE_ELIMINATION,
    status: TournamentStatus = TournamentStatus.OPEN,
    description: str | None = None,
    game: str = "League of Legends",
    min_players_per_team: int = 1,
    max_teams: int = 8,
    best_of: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    created_at: datetime = datetime(2024, 1, 1),
    updated_at: datetime = datetime(2024, 1, 1),
) -> Tournament:
    """
    Create a new tournament.

    Args:
    id: The id parameter.
    guild_id: The guild_id parameter.
    name: The name parameter.
    mode: The mode parameter.
    status: The status parameter.
    description: The description parameter.
    game: The game parameter.
    min_players_per_team: The min_players_per_team parameter.
    max_teams: The max_teams parameter.
    best_of: The best_of parameter.
    start_date: The start_date parameter.
    end_date: The end_date parameter.
    created_at: The created_at parameter.
    updated_at: The updated_at parameter.

    Returns:
    The result of the operation.
    """
    return Tournament(
        id=id or uuid.uuid4(),
        guild_id=guild_id,
        name=name,
        mode=mode,
        status=status,
        description=description,
        game=game,
        min_players_per_team=min_players_per_team,
        max_teams=max_teams,
        best_of=best_of,
        start_date=start_date,
        end_date=end_date,
        created_at=created_at,
        updated_at=updated_at,
    )
