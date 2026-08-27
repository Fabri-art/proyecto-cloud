"""Initial migration – create all tables.

Revision ID: 001
Revises: 
Create Date: 2026-08-27

Tables created:
  - tournaments
  - teams
  - players
  - matches
  - standings
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── tournaments ───────────────────────────────────────────────────────────
    op.create_table(
        "tournaments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(length=255), nullable=False),
        sa.Column("slug", sqlmodel.AutoString(length=255), nullable=False),
        sa.Column("season", sqlmodel.AutoString(length=20), nullable=False),
        sa.Column(
            "format",
            sa.Enum("league", "knockout", "group_knockout", name="tournamentformat"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("upcoming", "ongoing", "finished", "cancelled", name="tournamentstatus"),
            nullable=False,
        ),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tournaments_name", "tournaments", ["name"])
    op.create_index("ix_tournaments_slug", "tournaments", ["slug"], unique=True)

    # ── teams ─────────────────────────────────────────────────────────────────
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tournament_id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.AutoString(length=255), nullable=False),
        sa.Column("short_name", sqlmodel.AutoString(length=10), nullable=False),
        sa.Column("city", sqlmodel.AutoString(length=100), nullable=True),
        sa.Column("country", sqlmodel.AutoString(length=100), nullable=True),
        sa.Column("logo_url", sqlmodel.AutoString(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teams_name", "teams", ["name"])
    op.create_index("ix_teams_tournament_id", "teams", ["tournament_id"])

    # ── players ───────────────────────────────────────────────────────────────
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sqlmodel.AutoString(length=100), nullable=False),
        sa.Column("last_name", sqlmodel.AutoString(length=100), nullable=False),
        sa.Column("shirt_number", sa.Integer(), nullable=True),
        sa.Column(
            "position",
            sa.Enum("goalkeeper", "defender", "midfielder", "forward", name="playerposition"),
            nullable=True,
        ),
        sa.Column("nationality", sqlmodel.AutoString(length=100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("photo_url", sqlmodel.AutoString(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_players_team_id", "players", ["team_id"])

    # ── matches ───────────────────────────────────────────────────────────────
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tournament_id", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("matchday", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("scheduled", "live", "finished", "postponed", "cancelled", name="matchstatus"),
            nullable=False,
        ),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("home_score_et", sa.Integer(), nullable=True),
        sa.Column("away_score_et", sa.Integer(), nullable=True),
        sa.Column("home_score_pen", sa.Integer(), nullable=True),
        sa.Column("away_score_pen", sa.Integer(), nullable=True),
        sa.Column("venue", sqlmodel.AutoString(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matches_away_team_id", "matches", ["away_team_id"])
    op.create_index("ix_matches_home_team_id", "matches", ["home_team_id"])
    op.create_index("ix_matches_tournament_id", "matches", ["tournament_id"])

    # ── standings ─────────────────────────────────────────────────────────────
    op.create_table(
        "standings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tournament_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("played", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("won", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("drawn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lost", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_for", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goals_against", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("goal_difference", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("form", sqlmodel.AutoString(length=10), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["tournament_id"], ["tournaments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_standings_team_id", "standings", ["team_id"])
    op.create_index("ix_standings_tournament_id", "standings", ["tournament_id"])


def downgrade() -> None:
    op.drop_index("ix_standings_tournament_id", table_name="standings")
    op.drop_index("ix_standings_team_id", table_name="standings")
    op.drop_table("standings")

    op.drop_index("ix_matches_tournament_id", table_name="matches")
    op.drop_index("ix_matches_home_team_id", table_name="matches")
    op.drop_index("ix_matches_away_team_id", table_name="matches")
    op.drop_table("matches")

    op.drop_index("ix_players_team_id", table_name="players")
    op.drop_table("players")

    op.drop_index("ix_teams_tournament_id", table_name="teams")
    op.drop_index("ix_teams_name", table_name="teams")
    op.drop_table("teams")

    op.drop_index("ix_tournaments_slug", table_name="tournaments")
    op.drop_index("ix_tournaments_name", table_name="tournaments")
    op.drop_table("tournaments")

    # Drop enums
    sa.Enum(name="matchstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="playerposition").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tournamentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tournamentformat").drop(op.get_bind(), checkfirst=True)
