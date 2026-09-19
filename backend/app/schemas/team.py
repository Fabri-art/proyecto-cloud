from __future__ import annotations

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.player import PlayerRead


class TeamCreate(BaseModel):
    tournament_id: int
    name: str = Field(min_length=2, max_length=100)
    short_name: str = Field(min_length=2, max_length=5)
    delegate_name: str = Field(min_length=2, max_length=100)
    delegate_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) < 2:
            raise ValueError("La sigla debe tener al menos 2 caracteres.")
        if len(v) > 5:
            raise ValueError("La sigla no puede superar 5 caracteres.")
        if not re.match(r"^[A-Z0-9]+$", v):
            raise ValueError("La sigla solo puede contener letras mayúsculas y números.")
        return v

    @field_validator("delegate_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # Extraer solo los dígitos para verificar longitud mínima
        digits = re.sub(r"[^\d]", "", v)
        if len(digits) < 7:
            raise ValueError(
                "El teléfono debe tener al menos 7 dígitos. "
                "Formato aceptado: +51 987 654 321 o 987654321."
            )
        # Validar que el formato general sea razonable (dígitos, +, espacios, guiones, paréntesis)
        if not re.match(r"^\+?[\d\s\-(). ]{7,25}$", v):
            raise ValueError(
                "Formato de teléfono inválido. Usa dígitos, espacios, guiones o paréntesis."
            )
        return v


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
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    short_name: Optional[str] = Field(default=None, min_length=2, max_length=5)
    delegate_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    delegate_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator("short_name")
    @classmethod
    def validate_short_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().upper()
        if len(v) < 2:
            raise ValueError("La sigla debe tener al menos 2 caracteres.")
        if not re.match(r"^[A-Z0-9]+$", v):
            raise ValueError("La sigla solo puede contener letras mayúsculas y números.")
        return v

    @field_validator("delegate_phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        digits = re.sub(r"[^\d]", "", v)
        if len(digits) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos.")
        if not re.match(r"^\+?[\d\s\-(). ]{7,25}$", v):
            raise ValueError("Formato de teléfono inválido.")
        return v
