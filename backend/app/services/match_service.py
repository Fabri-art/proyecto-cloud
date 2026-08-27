"""
app/services/match_service.py
"""
from __future__ import annotations

from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match import Match, MatchStatus
from app.schemas.match import MatchResultUpdate
from app.services.standings_service import recalculate_standings

async def register_match_result(match_id: int, data: MatchResultUpdate, session: AsyncSession) -> Match:
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found.")

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
