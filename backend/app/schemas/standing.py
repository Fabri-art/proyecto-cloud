"""
app/schemas/standing.py
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class StandingRead(BaseModel):
    id: int
    tournament_id: int
    team_id: int
    position: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: Optional[str]

    model_config = {"from_attributes": True}
