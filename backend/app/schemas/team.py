from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, field_validator

from app.schemas.player import PlayerRead


class TeamCreate(BaseModel):
    tournament_id: int
    name: str
    short_name: str
    delegate_name: str
    delegate_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("short_name")
    @classmethod
    def upper_short_name(cls, v: str) -> str:
        return v.upper().strip()


class TeamRead(BaseModel):
    id: int
    tournament_id: int
    name: str
    short_name: str
    delegate_name: str
    delegate_phone: Optional[str]
    city: Optional[str]
    country: Optional[str]
    logo_url: Optional[str]

    model_config = {"from_attributes": True}


class TeamReadWithPlayers(TeamRead):
    """Extended response that includes the full player roster."""
    players: List[PlayerRead] = []


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    delegate_name: Optional[str] = None
    delegate_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
