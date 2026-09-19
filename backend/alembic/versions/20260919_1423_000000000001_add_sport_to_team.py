"""add sport to team

Revision ID: 000000000001
Revises: 5958beee4715
Create Date: 2026-09-19 14:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '000000000001'
down_revision: Union[str, None] = '5958beee4715'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # First create the enum type if it doesn't exist. Actually, teamsporttype doesn't exist.
    teamsporttype = sa.Enum('football', 'basketball', name='teamsporttype')
    teamsporttype.create(op.get_bind(), checkfirst=True)
    
    op.add_column('teams', sa.Column('sport', teamsporttype, nullable=False, server_default='football'))

def downgrade() -> None:
    op.drop_column('teams', 'sport')
    sa.Enum(name='teamsporttype').drop(op.get_bind(), checkfirst=True)
