"""
app/services/standings_service.py
"""
from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.match import Match, MatchStatus
from app.models.standing import Standing
from app.models.team import Team


async def recalculate_standings(tournament_id: int, session: AsyncSession) -> List[Standing]:
    """
    Recalculate the entire standing table for a tournament based on FINISHED matches.
    Sorts by Points, Goal Difference, Goals For.
    """
    # 1. Fetch all FINISHED matches
    matches = (await session.execute(
        select(Match)
        .where(Match.tournament_id == tournament_id)
        .where(Match.status == MatchStatus.FINISHED)
    )).scalars().all()

    # 2. Fetch all teams in the tournament
    teams = (await session.execute(
        select(Team).where(Team.tournament_id == tournament_id)
    )).scalars().all()

    # 3. Compute stats
    stats = {
        t.id: {"played": 0, "won": 0, "drawn": 0, "lost": 0, "gf": 0, "ga": 0, "pts": 0}
        for t in teams
    }

    for m in matches:
        h = m.home_team_id
        a = m.away_team_id
        hs = m.home_score or 0
        as_ = m.away_score or 0

        if h in stats:
            stats[h]["played"] += 1
            stats[h]["gf"] += hs
            stats[h]["ga"] += as_
            if hs > as_:
                stats[h]["won"] += 1
                stats[h]["pts"] += 3
            elif hs == as_:
                stats[h]["drawn"] += 1
                stats[h]["pts"] += 1
            else:
                stats[h]["lost"] += 1

        if a in stats:
            stats[a]["played"] += 1
            stats[a]["gf"] += as_
            stats[a]["ga"] += hs
            if as_ > hs:
                stats[a]["won"] += 1
                stats[a]["pts"] += 3
            elif as_ == hs:
                stats[a]["drawn"] += 1
                stats[a]["pts"] += 1
            else:
                stats[a]["lost"] += 1

    # 4. Sort teams based on pts, dg, gf
    sorted_teams = sorted(
        stats.items(),
        key=lambda x: (
            x[1]["pts"],
            x[1]["gf"] - x[1]["ga"],
            x[1]["gf"]
        ),
        reverse=True
    )

    # 5. Fetch existing standings to update or create new ones
    existing_standings = (await session.execute(
        select(Standing).where(Standing.tournament_id == tournament_id)
    )).scalars().all()
    standings_map = {s.team_id: s for s in existing_standings}

    result = []
    for pos, (team_id, s_data) in enumerate(sorted_teams, start=1):
        dg = s_data["gf"] - s_data["ga"]

        standing = standings_map.get(team_id)
        if not standing:
            standing = Standing(tournament_id=tournament_id, team_id=team_id)
            session.add(standing)

        standing.position = pos
        standing.played = s_data["played"]
        standing.won = s_data["won"]
        standing.drawn = s_data["drawn"]
        standing.lost = s_data["lost"]
        standing.goals_for = s_data["gf"]
        standing.goals_against = s_data["ga"]
        standing.goal_difference = dg
        standing.points = s_data["pts"]

        result.append(standing)

    await session.flush()
    return result


async def get_standings(tournament_id: int, session: AsyncSession) -> List[Standing]:
    """Retrieve current standings."""
    standings = (await session.execute(
        select(Standing)
        .where(Standing.tournament_id == tournament_id)
        .order_by(Standing.position)
    )).scalars().all()
    
    # If no standings exist yet, maybe the tournament just started. 
    # Let's ensure they are created if missing.
    if not standings:
        standings = await recalculate_standings(tournament_id, session)
        
    return standings
