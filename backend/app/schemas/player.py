from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator

from app.models.player import PlayerPosition


class PlayerCreate(BaseModel):
    first_name: str
    last_name: str
    dni: str
    shirt_number: Optional[int] = None
    position: Optional[PlayerPosition] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = None

    @field_validator("dni")
    @classmethod
    def normalize_dni(cls, v: str) -> str:
        return v.strip().upper()


class PlayerRead(BaseModel):
    id: int
    team_id: int
    first_name: str
    last_name: str
    dni: str
    shirt_number: Optional[int]
    position: Optional[PlayerPosition]
    nationality: Optional[str]
    date_of_birth: Optional[date]
    is_active: bool

    model_config = {"from_attributes": True}


class PlayerUpdate(BaseModel):
    shirt_number: Optional[int] = None
    position: Optional[PlayerPosition] = None
    is_active: Optional[bool] = None
    photo_url: Optional[str] = None
