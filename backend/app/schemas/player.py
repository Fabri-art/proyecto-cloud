from __future__ import annotations

import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.player import PlayerPosition


class PlayerCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    dni: str
    shirt_number: Optional[int] = Field(default=None, ge=1, le=99)
    position: Optional[PlayerPosition] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[date] = None
    photo_url: Optional[str] = None

    @field_validator("dni")
    @classmethod
    def validate_dni(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) < 5:
            raise ValueError(
                "El DNI/documento debe tener al menos 5 caracteres."
            )
        if len(v) > 20:
            raise ValueError(
                "El DNI/documento no puede superar 20 caracteres."
            )
        # Solo letras, números y guiones (cubre DNI nacionales e internacionales)
        if not re.match(r"^[A-Z0-9\-]+$", v):
            raise ValueError(
                "El DNI/documento solo puede contener letras, números y guiones."
            )
        return v

    @field_validator("shirt_number")
    @classmethod
    def validate_shirt_number(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if not isinstance(v, int) or v < 1 or v > 99:
            raise ValueError("El dorsal debe ser un número entero entre 1 y 99.")
        return v


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
    shirt_number: Optional[int] = Field(default=None, ge=1, le=99)
    position: Optional[PlayerPosition] = None
    is_active: Optional[bool] = None
    photo_url: Optional[str] = None
