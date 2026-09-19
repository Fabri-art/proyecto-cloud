"""add chess roles

Revision ID: c3d4e5f6a1b2
Revises: b2c3d4e5f6a1
Create Date: 2026-09-19 19:30:00.000000+00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a1b2'
down_revision: Union[str, None] = 'b2c3d4e5f6a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'chess_main'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'chess_sub_1'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'chess_sub_2'")


def downgrade() -> None:
    pass
