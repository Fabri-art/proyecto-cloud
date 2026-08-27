from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


def _enum_values(enum_cls):
    return [e.value for e in enum_cls]


class Match(SQLModel, table=True):
    """A football match between two teams within a tournament."""

    __tablename__ = "matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournaments.id", index=True)
    home_team_id: int = Field(foreign_key="teams.id", index=True)
    away_team_id: int = Field(foreign_key="teams.id", index=True)

    matchday: Optional[int] = Field(default=None)       # round/jornada number
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    status: MatchStatus = Field(
        default=MatchStatus.SCHEDULED,
        sa_column=sa.Column(
            sa.Enum(
                *_enum_values(MatchStatus),
                name="matchstatus",
                create_type=False,
            ),
            nullable=False,
        ),
    )

    home_score: Optional[int] = Field(default=None, ge=0)
    away_score: Optional[int] = Field(default=None, ge=0)

    # Extra time / penalties
    home_score_et: Optional[int] = Field(default=None, ge=0)
    home_score_pen: Optional[int] = Field(default=None, ge=0)
    away_score_et: Optional[int] = Field(default=None, ge=0)
    away_score_pen: Optional[int] = Field(default=None, ge=0)

    venue: Optional[str] = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
