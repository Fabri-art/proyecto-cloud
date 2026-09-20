"""add four new sports (aura battle, sperm triathlon, tire race, mosquito marathon)

Revision ID: d4e5f6a1b2c3
Revises: c3d4e5f6a1b2
Create Date: 2026-09-20 15:00:00.000000+00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a1b2c3'
down_revision: Union[str, None] = 'c3d4e5f6a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Extend sporttype enum (used in tournaments table)
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE sporttype ADD VALUE IF NOT EXISTS 'aura_battle'")
        op.execute("ALTER TYPE sporttype ADD VALUE IF NOT EXISTS 'sperm_triathlon'")
        op.execute("ALTER TYPE sporttype ADD VALUE IF NOT EXISTS 'tire_race'")
        op.execute("ALTER TYPE sporttype ADD VALUE IF NOT EXISTS 'mosquito_marathon'")

    # 2. Extend teamsporttype enum (used in teams table)
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE teamsporttype ADD VALUE IF NOT EXISTS 'aura_battle'")
        op.execute("ALTER TYPE teamsporttype ADD VALUE IF NOT EXISTS 'sperm_triathlon'")
        op.execute("ALTER TYPE teamsporttype ADD VALUE IF NOT EXISTS 'tire_race'")
        op.execute("ALTER TYPE teamsporttype ADD VALUE IF NOT EXISTS 'mosquito_marathon'")

    # 3. Extend playerposition enum with new roles
    with op.get_context().autocommit_block():
        # Aura Battle
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'aura_farmer_main'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'aura_farmer_sub1'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'aura_farmer_sub2'")
        # Sperm Triathlon
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'sperm_main'")
        # Tire Race
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'tire_dir'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'tire_rod'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'tire_fren'")
        # Mosquito Marathon
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'mosquito_pic'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'mosquito_zum'")
        op.execute("ALTER TYPE playerposition ADD VALUE IF NOT EXISTS 'mosquito_evas'")


def downgrade() -> None:
    pass
