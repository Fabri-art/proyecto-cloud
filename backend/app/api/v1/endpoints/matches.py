"""
app/api/v1/endpoints/matches.py
"""
from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.match import MatchRead, MatchResultUpdate, MatchStatusUpdate
from app.services import match_service

router = APIRouter(tags=["Matches"])


@router.get(
    "/matches",
    response_model=List[MatchRead],
    summary="List matches",
    description="Lists matches optionally filtered by tournament_id or matchday.",
)
async def list_matches(
    tournament_id: Optional[int] = Query(default=None, description="Filter by tournament"),
    matchday: Optional[int] = Query(default=None, description="Filter by matchday/round"),
    session: AsyncSession = Depends(get_session),
) -> List[MatchRead]:
    matches = await match_service.list_matches(session, tournament_id=tournament_id, matchday=matchday)
    return [MatchRead.model_validate(m) for m in matches]


@router.get(
    "/matches/{match_id}",
    response_model=MatchRead,
    summary="Get match detail",
    description="Retrieves detail of a specific match.",
)
async def get_match(
    match_id: int,
    session: AsyncSession = Depends(get_session),
) -> MatchRead:
    match = await match_service.get_match(match_id, session)
    return MatchRead.model_validate(match)


@router.patch(
    "/matches/{match_id}/status",
    response_model=MatchRead,
    summary="Update match status",
    description="Updates the status of a match (scheduled, live, finished, cancelled).",
)
async def update_match_status(
    match_id: int,
    body: MatchStatusUpdate,
    session: AsyncSession = Depends(get_session),
) -> MatchRead:
    match = await match_service.update_match_status(match_id, body.status, session)
    return MatchRead.model_validate(match)


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
