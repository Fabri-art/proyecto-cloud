from __future__ import annotations

import re
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.player import PlayerRead
from app.models.tournament import SportType

SOUTH_AMERICAN_COUNTRIES = {
    'Argentina', 'Bolivia', 'Brasil', 'Chile', 'Colombia', 'Ecuador',
    'Guyana', 'Paraguay', 'Perú', 'Peru', 'Surinam', 'Suriname', 'Uruguay', 'Venezuela'
}


class TeamCreate(BaseModel):
    tournament_id: int
    name: str = Field(min_length=2, max_length=100)
    short_name: str = Field(min_length=2, max_length=5)
    sport: SportType = SportType.FOOTBALL
    delegate_name: str = Field(min_length=2, max_length=100)
    delegate_phone: str = Field(min_length=9, max_length=30)
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if any(char.isdigit() for char in v):
            raise ValueError('El nombre del club no puede contener números.')
        return v

    @field_validator('short_name')
    @classmethod
    def validate_short_name(cls, v: str) -> str:
        v = v.strip().upper()
        if len(v) < 2:
            raise ValueError('La sigla debe tener al menos 2 caracteres.')
        if len(v) > 5:
            raise ValueError('La sigla no puede superar 5 caracteres.')
        if not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('La sigla solo puede contener letras mayúsculas y números.')
        return v

    @field_validator('delegate_name')
    @classmethod
    def validate_delegate_name(cls, v: str) -> str:
        v = v.strip()
        if any(char.isdigit() for char in v):
            raise ValueError('El nombre del delegado no puede contener números.')
        return v

    @field_validator('delegate_phone')
    @classmethod
    def validate_delegate_phone(cls, v: str) -> str:
        v = v.strip()
        if any(char.isalpha() for char in v):
            raise ValueError('El teléfono de contacto no puede contener letras.')
        digits = re.sub(r'[^\d]', '', v)
        if len(digits) < 9:
            raise ValueError('El teléfono debe tener al menos 9 dígitos numéricos.')
        if not re.match(r'^\+?[\d\s\-\(\)\.]{9,30}$', v):
            raise ValueError('Formato de teléfono inválido (solo números y signos + - ()).')
        return v

    @field_validator('city')
    @classmethod
    def validate_city(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        if any(char.isdigit() for char in v):
            raise ValueError('La ciudad no puede contener números.')
        return v

    @field_validator('country')
    @classmethod
    def validate_country(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return None
        v = v.strip()
        if v not in SOUTH_AMERICAN_COUNTRIES:
            raise ValueError(f'"{v}" no es un país de Sudamérica válido.')
        return v


class TeamRead(BaseModel):
    id: int
    tournament_id: int
    name: str
    short_name: str
    sport: SportType
    delegate_name: str
    delegate_phone: Optional[str]
    city: Optional[str]
    country: Optional[str]
    logo_url: Optional[str]

    model_config = {'from_attributes': True}


class TeamReadWithPlayers(TeamRead):
    """Extended response that includes the full player roster."""
    players: List[PlayerRead] = []

TeamWithPlayers = TeamReadWithPlayers


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    short_name: Optional[str] = Field(default=None, min_length=2, max_length=5)
    sport: Optional[SportType] = None
    delegate_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    delegate_phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
