"""
Domain entity definitions for the tournament manager.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseEntity:
    """
    Base entity model containing shared identity metadata.
    """

    created_at: datetime
    updated_at: datetime | None = None
