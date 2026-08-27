"""
app/api/v1/endpoints/standings.py
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.standing import StandingRead
from app.services import standings_service

router = APIRouter(tags=["Standings"])


@router.get(
    "/tournaments/{tournament_id}/standings",
    response_model=List[StandingRead],
    summary="Get tournament standings",
    description="Retrieves the current standings table for a given tournament.",
)
async def get_standings(
    tournament_id: int,
    session: AsyncSession = Depends(get_session),
) -> List[StandingRead]:
    standings = await standings_service.get_standings(tournament_id, session)
    return [StandingRead.model_validate(s) for s in standings]
