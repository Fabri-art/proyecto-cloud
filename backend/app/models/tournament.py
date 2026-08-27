from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class TournamentFormat(str, Enum):
    LEAGUE = "league"              # round-robin league
    KNOCKOUT = "knockout"          # single-elimination
    GROUP_KNOCKOUT = "group_knockout"   # groups + knockout phase


class TournamentStatus(str, Enum):
    UPCOMING = "upcoming"
    ONGOING = "ongoing"
    FINISHED = "finished"
    CANCELLED = "cancelled"


def _enum_values(enum_cls):
    """Return the .value strings of an Enum – forces SA to use lowercase labels."""
    return [e.value for e in enum_cls]


class Tournament(SQLModel, table=True):
    """Represents a football tournament or competition."""

    __tablename__ = "tournaments"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    slug: str = Field(unique=True, max_length=255, index=True)
    season: str = Field(max_length=20)          # e.g. "2024-25"

    format: TournamentFormat = Field(
        default=TournamentFormat.LEAGUE,
        sa_column=sa.Column(
            sa.Enum(
                *_enum_values(TournamentFormat),
                name="tournamentformat",
                create_type=False,   # type already exists in DB from migration
            ),
            nullable=False,
        ),
    )

    status: TournamentStatus = Field(
        default=TournamentStatus.UPCOMING,
        sa_column=sa.Column(
            sa.Enum(
                *_enum_values(TournamentStatus),
                name="tournamentstatus",
                create_type=False,
            ),
            nullable=False,
        ),
    )

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
