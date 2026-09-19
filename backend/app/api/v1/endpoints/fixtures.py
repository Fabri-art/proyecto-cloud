"""
app/api/v1/endpoints/fixtures.py

NOM-8 endpoints:
  POST   /api/v1/tournaments/{tournament_id}/fixture/generate
  DELETE /api/v1/tournaments/{tournament_id}/fixture
  GET    /api/v1/tournaments/{tournament_id}/fixture
  PATCH  /api/v1/matches/{match_id}/schedule
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.match import (
    FixtureDeleteInfo,
    FixtureGenerateRequest,
    FixtureRead,
    MatchRead,
    MatchSchedule,
)
from app.services import fixture_service

router = APIRouter(tags=["Fixture"])


# ── Fixture generation ────────────────────────────────────────────────────────

@router.post(
    "/tournaments/{tournament_id}/fixture/generate",
    response_model=List[MatchRead],
    status_code=201,
    summary="Generate Round-Robin fixture",
    description=(
        "Genera un fixture completo round-robin para todos los equipos registrados "
        "en el torneo. Soporta número impar de equipos (bye round). "
        "Si `force=true` en el body, elimina el fixture existente (incluyendo "
        "partidos jugados y estadísticas) y genera uno nuevo en una sola transacción. "
        "Retorna HTTP 409 si ya existe un fixture y force=false (default)."
    ),
)
async def generate_fixture(
    tournament_id: int,
    body: Optional[FixtureGenerateRequest] = None,
    session: AsyncSession = Depends(get_session),
) -> List[MatchRead]:
    force = body.force if body else False
    matches = await fixture_service.generate_fixture(tournament_id, session, force=force)
    return [MatchRead.model_validate(m) for m in matches]


# ── Fixture deletion ──────────────────────────────────────────────────────────

@router.delete(
    "/tournaments/{tournament_id}/fixture",
    response_model=FixtureDeleteInfo,
    status_code=200,
    summary="Delete tournament fixture",
    description=(
        "Elimina todos los partidos del torneo y resetea la tabla de posiciones. "
        "Si hay partidos con resultados (FINALIZADO o EN JUEGO) y `force=false` (default), "
        "retorna HTTP 409 con detalle de cuántos partidos tienen datos jugados. "
        "Con `force=true`, elimina todo incluyendo marcadores y estadísticas."
    ),
)
async def delete_fixture(
    tournament_id: int,
    force: bool = Query(default=False, description="Forzar eliminación aunque haya partidos jugados"),
    session: AsyncSession = Depends(get_session),
) -> FixtureDeleteInfo:
    return await fixture_service.delete_fixture(tournament_id, session, force=force)


# ── Fixture read ──────────────────────────────────────────────────────────────

@router.get(
    "/tournaments/{tournament_id}/fixture",
    response_model=FixtureRead,
    summary="Get fixture grouped by matchday",
    description="Retorna todos los partidos del torneo agrupados por jornada.",
)
async def get_fixture(
    tournament_id: int,
    session: AsyncSession = Depends(get_session),
) -> FixtureRead:
    return await fixture_service.get_fixture(tournament_id, session)


# ── Match scheduling ──────────────────────────────────────────────────────────

@router.patch(
    "/matches/{match_id}/schedule",
    response_model=MatchRead,
    summary="Schedule a match",
    description="Assign a date/time and optional venue to a specific match.",
)
async def schedule_match(
    match_id: int,
    body: MatchSchedule,
    session: AsyncSession = Depends(get_session),
) -> MatchRead:
    match = await fixture_service.schedule_match(match_id, body, session)
    return MatchRead.model_validate(match)
