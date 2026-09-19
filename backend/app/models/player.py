from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class PlayerPosition(str, Enum):
    # Football
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    FORWARD = "forward"
    # Basketball
    POINT_GUARD = "point_guard"
    SHOOTING_GUARD = "shooting_guard"
    SMALL_FORWARD = "small_forward"
    POWER_FORWARD = "power_forward"
    CENTER = "center"
    # Volleyball
    SETTER = "setter"
    LIBERO = "libero"
    OUTSIDE_HITTER = "outside_hitter"
    OPPOSITE = "opposite"
    MIDDLE_BLOCKER = "middle_blocker"
    # Chess
    CHESS_PLAYER = "chess_player"
    CHESS_MAIN = "chess_main"
    CHESS_SUB_1 = "chess_sub_1"
    CHESS_SUB_2 = "chess_sub_2"


def _enum_values(enum_cls):
    return [e.value for e in enum_cls]


class Player(SQLModel, table=True):
    """A player belonging to a team."""

    __tablename__ = "players"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    dni: str = Field(max_length=20, index=True)  # National ID — unique per tournament

    shirt_number: Optional[int] = Field(default=None, ge=0, le=99)

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
