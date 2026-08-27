from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class PlayerPosition(str, Enum):
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"


def _enum_values(enum_cls):
    return [e.value for e in enum_cls]


class Player(SQLModel, table=True):
    """A player belonging to a team."""

    __tablename__ = "players"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    dni: str = Field(max_length=20, index=True)  # National ID – unique per tournament

    shirt_number: Optional[int] = Field(default=None, ge=1, le=99)

    position: Optional[PlayerPosition] = Field(
        default=None,
        sa_column=sa.Column(
            sa.Enum(
                *_enum_values(PlayerPosition),
                name="playerposition",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    nationality: Optional[str] = Field(default=None, max_length=100)
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = Field(default=None, max_length=512)
    is_active: bool = Field(default=True)
