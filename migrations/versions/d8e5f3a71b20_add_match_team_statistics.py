"""add_match_team_statistics

Revision ID: d8e5f3a71b20
Revises: c7f4d2e91a60
Create Date: 2026-09-20 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d8e5f3a71b20"
down_revision: str | Sequence[str] | None = "c7f4d2e91a60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add aggregate match statistics to team participations."""
    for column in ("kills", "deaths", "assists"):
        op.add_column(
            "match_teams",
            sa.Column(
                column, sa.Integer(), nullable=False, server_default=sa.text("0")
            ),
        )


def downgrade() -> None:
    """Remove aggregate match statistics from team participations."""
    for column in ("assists", "deaths", "kills"):
        op.drop_column("match_teams", column)
