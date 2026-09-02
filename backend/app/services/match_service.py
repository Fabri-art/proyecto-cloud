"""
app/services/match_service.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.match import Match, MatchStatus
from app.schemas.match import MatchResultUpdate
from app.services.standings_service import recalculate_standings


async def get_match(match_id: int, session: AsyncSession) -> Match:
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found.")
    return match


async def list_matches(
    session: AsyncSession,
    tournament_id: Optional[int] = None,
    matchday: Optional[int] = None,
) -> Sequence[Match]:
    stmt = select(Match)
    if tournament_id is not None:
        stmt = stmt.where(Match.tournament_id == tournament_id)
    if matchday is not None:
        stmt = stmt.where(Match.matchday == matchday)
    stmt = stmt.order_by(Match.matchday, Match.id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_match_status(
    match_id: int,
    new_status: MatchStatus,
    session: AsyncSession,
) -> Match:
    match = await get_match(match_id, session)
    match.status = new_status
    if new_status == MatchStatus.LIVE and not match.started_at:
        match.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
    elif new_status == MatchStatus.FINISHED and not match.finished_at:
        match.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)

    match.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(match)
    await session.flush()
    await session.refresh(match)
    return match


async def register_match_result(
    match_id: int, data: MatchResultUpdate, session: AsyncSession
) -> Match:
    match = await get_match(match_id, session)

    # Update scores
    match.home_score = data.home_score
    match.away_score = data.away_score
    match.home_score_et = data.home_score_et
    match.away_score_et = data.away_score_et
    match.home_score_pen = data.home_score_pen
    match.away_score_pen = data.away_score_pen

    # Mark as finished
    match.status = MatchStatus.FINISHED
    match.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)

    session.add(match)
    await session.flush()

    # Recalculate standings for this tournament
    await recalculate_standings(match.tournament_id, session)

    await session.refresh(match)
    return match
