"""
app/schemas/match.py
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.match import MatchStatus


class MatchCreate(BaseModel):
    tournament_id: int
    home_team_id: int
    away_team_id: int
    matchday: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    venue: Optional[str] = None


class MatchRead(BaseModel):
    id: int
    tournament_id: int
    home_team_id: int
    away_team_id: int
    matchday: Optional[int]
    scheduled_at: Optional[datetime]
    status: MatchStatus
    home_score: Optional[int]
    away_score: Optional[int]
    venue: Optional[str]

    model_config = {"from_attributes": True}


class MatchSchedule(BaseModel):
    """Payload for PATCH /matches/{id}/schedule"""
    scheduled_at: datetime
    venue: Optional[str] = None


class MatchUpdate(BaseModel):
    status: Optional[MatchStatus] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_score_et: Optional[int] = None
    away_score_et: Optional[int] = None
    home_score_pen: Optional[int] = None
    away_score_pen: Optional[int] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class MatchdayRead(BaseModel):
    """A round/jornada grouping matches."""
    matchday: int
    matches: List[MatchRead]


class FixtureRead(BaseModel):
    """Full fixture for a tournament, grouped by matchday."""
    tournament_id: int
    total_matchdays: int
    rounds: List[MatchdayRead]


class MatchResultUpdate(BaseModel):
    """Payload to update match result and finish it."""
    home_score: int
    away_score: int
    home_score_et: Optional[int] = None
    away_score_et: Optional[int] = None
    home_score_pen: Optional[int] = None
    away_score_pen: Optional[int] = None
