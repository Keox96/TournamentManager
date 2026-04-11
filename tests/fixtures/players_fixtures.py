"""
Test module for players fixtures.
"""

import uuid
from datetime import datetime

from src.domain.entities.players import Player


def create_player(
    *,
    id: uuid.UUID | None = None,
    username: str = "dupont",
    display_name: str = "Dupont",
    email: str | None = None,
    icon_url: str | None = None,
    created_at: datetime = datetime(2024, 1, 1),
    updated_at: datetime = datetime(2024, 1, 1),
) -> Player:
    """
    Create a new player.

    Args:
    id: The id parameter.
    username: The username parameter.
    display_name: The display_name parameter.
    email: The email parameter.
    icon_url: The icon_url parameter.
    created_at: The created_at parameter.
    updated_at: The updated_at parameter.

    Returns:
    The result of the operation.
    """
    return Player(
        id=id or uuid.uuid4(),
        username=username,
        display_name=display_name,
        email=email,
        icon_url=icon_url,
        created_at=created_at,
        updated_at=updated_at,
    )
