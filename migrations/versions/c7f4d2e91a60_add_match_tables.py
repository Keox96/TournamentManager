"""add_match_tables

Revision ID: c7f4d2e91a60
Revises: af9b5868f4bb
Create Date: 2026-09-20 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7f4d2e91a60"
down_revision: str | Sequence[str] | None = "af9b5868f4bb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create match and match participation tables."""
    op.create_table(
        "matches",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tournament_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=255), nullable=False),
        sa.Column("round", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tournament_id"], ["tournaments.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "matches_tournament_id_index",
        "matches",
        ["tournament_id"],
    )

    op.create_table(
        "match_teams",
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("team_id", sa.Uuid(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("match_id", "team_id"),
    )

    op.create_table(
        "match_players",
        sa.Column("match_id", sa.Uuid(), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("kills", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("deaths", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("assists", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("match_id", "player_id"),
    )


def downgrade() -> None:
    """Drop match and match participation tables."""
    op.drop_table("match_players")
    op.drop_table("match_teams")
    op.drop_index("matches_tournament_id_index", table_name="matches")
    op.drop_table("matches")
