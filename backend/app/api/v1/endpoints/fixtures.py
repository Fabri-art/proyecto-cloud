"""
app/api/v1/endpoints/fixtures.py

NOM-8 endpoints:
  POST  /api/v1/tournaments/{tournament_id}/fixture/generate
  GET   /api/v1/tournaments/{tournament_id}/fixture
  PATCH /api/v1/matches/{match_id}/schedule
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.match import FixtureRead, MatchRead, MatchSchedule
from app.services import fixture_service

router = APIRouter(tags=["Fixture"])


# ── Fixture generation ────────────────────────────────────────────────────────

@router.post(
    "/tournaments/{tournament_id}/fixture/generate",
    response_model=List[MatchRead],
    status_code=201,
    summary="Generate Round-Robin fixture",
    description=(
        "Generates a complete round-robin fixture for all registered teams in the "
        "tournament. Supports an odd number of teams (bye round). "
        "Returns HTTP 409 if a fixture already exists."
    ),
)
async def generate_fixture(
    tournament_id: int,
    session: AsyncSession = Depends(get_session),
) -> List[MatchRead]:
    matches = await fixture_service.generate_fixture(tournament_id, session)
    return [MatchRead.model_validate(m) for m in matches]


@router.get(
    "/tournaments/{tournament_id}/fixture",
    response_model=FixtureRead,
    summary="Get fixture grouped by matchday",
    description="Returns all matches for a tournament, grouped by jornada/round.",
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
