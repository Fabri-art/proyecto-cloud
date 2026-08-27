from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class Team(SQLModel, table=True):
    """A football club or team participating in a tournament."""

    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="tournaments.id", index=True)
    name: str = Field(index=True, max_length=255)
    short_name: str = Field(max_length=10)       # e.g. "BAR", "RMA"
    delegate_name: str = Field(max_length=255)   # Club delegate / coach name
    delegate_phone: Optional[str] = Field(default=None, max_length=30)
    city: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    logo_url: Optional[str] = Field(default=None, max_length=512)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
