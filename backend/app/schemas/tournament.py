from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.tournament import TournamentFormat, TournamentStatus


# ── Create ─────────────────────────────────────────────────────────────────────
class TournamentCreate(BaseModel):
    name: str
    slug: str
    season: str
    format: TournamentFormat = TournamentFormat.LEAGUE
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ── Read ───────────────────────────────────────────────────────────────────────
class TournamentRead(BaseModel):
    id: int
    name: str
    slug: str
    season: str
    format: TournamentFormat
    status: TournamentStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Update ─────────────────────────────────────────────────────────────────────
class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[TournamentStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
