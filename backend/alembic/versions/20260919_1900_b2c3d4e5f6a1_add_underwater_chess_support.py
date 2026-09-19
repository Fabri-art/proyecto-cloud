"""add underwater chess support

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-09-19 19:00:00.000000+00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a1'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend sporttype enum (used in tournaments table)
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE sporttype ADD VALUE IF NOT EXISTS 'underwater_chess'")

    # Extend teamsporttype enum (used in teams table)
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE teamsporttype ADD VALUE IF NOT EXISTS 'underwater_chess'")

    # Extend playerposition enum with chess player position
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'chess_player'")


def downgrade() -> None:
    pass
