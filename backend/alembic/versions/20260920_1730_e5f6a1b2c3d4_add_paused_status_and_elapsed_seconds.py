"""add paused status and elapsed_seconds

Revision ID: e5f6a1b2c3d4
Revises: d4e5f6a1b2c3
Create Date: 2026-09-20 17:30:00.000000+00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a1b2c3d4'
down_revision: Union[str, None] = 'd4e5f6a1b2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend matchstatus enum
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE matchstatus ADD VALUE IF NOT EXISTS 'paused';")

    # 2. Add elapsed_seconds to matches table
    op.execute("ALTER TABLE matches ADD COLUMN IF NOT EXISTS elapsed_seconds INTEGER DEFAULT 0;")


def downgrade() -> None:
    op.execute("ALTER TABLE matches DROP COLUMN IF EXISTS elapsed_seconds;")
