"""add volleyball support

Revision ID: a1b2c3d4e5f6
Revises: 000000000001
Create Date: 2026-09-19 17:30:00.000000+00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '000000000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend sporttype enum (used in tournaments table)
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE sporttype ADD VALUE IF NOT EXISTS 'volleyball'")

    # Extend teamsporttype enum (used in teams table)
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE teamsporttype ADD VALUE IF NOT EXISTS 'volleyball'")

    # Extend playerposition enum with volleyball positions
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'setter'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'libero'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'outside_hitter'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'opposite'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'middle_blocker'")


def downgrade() -> None:
    # Note: removing enum values is not supported in PostgreSQL without recreating the type.
    # Downgrade is intentionally a no-op for enum additions.
    pass
