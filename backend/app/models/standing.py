from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Standing(SQLModel, table=True):
    """
    League standing / position table entry for a team within a tournament.

    Updated after each match result.
    """

    __tablename__ = "standings"

    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournaments.id", index=True)
    team_id: int = Field(foreign_key="teams.id", index=True)

    position: int = Field(default=0)            # rank in table

    played: int = Field(default=0, ge=0)        # matches played
    won: int = Field(default=0, ge=0)
    drawn: int = Field(default=0, ge=0)
    lost: int = Field(default=0, ge=0)

    goals_for: int = Field(default=0, ge=0)
    goals_against: int = Field(default=0, ge=0)
    goal_difference: int = Field(default=0)     # GF - GA (can be negative)

    points: int = Field(default=0, ge=0)

    # Form string, e.g. "WWDLW" (last 5)
    form: Optional[str] = Field(default=None, max_length=10)

    updated_at: datetime = Field(default_factory=datetime.utcnow)
