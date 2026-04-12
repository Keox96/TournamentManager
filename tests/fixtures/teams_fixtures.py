"""
Test module for teams fixtures.
"""

import uuid
from datetime import datetime

from src.domain.entities.teams import Team, TeamPlayer
from src.domain.utils.enums import TeamRole


def create_team(
    *,
    id: uuid.UUID | None = None,
    name: str = "Team Alpha",
    tag: str = "TA",
    description: str | None = None,
    created_at: datetime = datetime(2024, 1, 1),
    updated_at: datetime = datetime(2024, 1, 1),
) -> Team:
    """
    Create a new team.

    Args:
        id: The id parameter.
        name: The name parameter.
        tag: The tag parameter.
        description: The description parameter.
        created_at: The created_at parameter.
        updated_at: The updated_at parameter.

    Returns:
        The result of the operation.
    """
    return Team(
        id=id or uuid.uuid4(),
        name=name,
        tag=tag,
        description=description,
        created_at=created_at,
        updated_at=updated_at,
    )


def create_teamplayer(
    *,
    team_id: uuid.UUID | None = None,
    player_id: uuid.UUID | None = None,
    role: TeamRole = TeamRole.PLAYER,
    created_at: datetime = datetime(2024, 1, 1),
    updated_at: datetime = datetime(2024, 1, 1),
) -> TeamPlayer:
    """
    Create a new team member.

    Args:
        team_id: the team_id parameter
        player_id: the player_id parameter
        role:  the role parameter
        created_at: The created_at parameter.
        updated_at: The updated_at parameter.

    Returns:
        The result of the operation.
    """
    return TeamPlayer(
        team_id=team_id or uuid.uuid4(),
        player_id=player_id or uuid.uuid4(),
        role=role,
        created_at=created_at,
        updated_at=updated_at,
    )
