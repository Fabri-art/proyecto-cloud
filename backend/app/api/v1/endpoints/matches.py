"""
app/api/v1/endpoints/matches.py
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.match import MatchRead, MatchResultUpdate
from app.services import match_service

router = APIRouter(tags=["Matches"])


@router.patch(
    "/matches/{match_id}/result",
    response_model=MatchRead,
    summary="Register match result",
    description="Registers the final result for a match, marks it as FINISHED, and automatically recalculates tournament standings.",
)
async def register_match_result(
    match_id: int,
    body: MatchResultUpdate,
    session: AsyncSession = Depends(get_session),
) -> MatchRead:
    match = await match_service.register_match_result(match_id, body, session)
    return MatchRead.model_validate(match)
