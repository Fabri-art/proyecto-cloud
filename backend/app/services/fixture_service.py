"""
app/services/fixture_service.py

NOM-8 – Round-Robin fixture generator and scheduling logic.

Algorithm details
─────────────────
Uses the classic "rotating polygon" (Berger tables) method:

  1. If team count is odd → add a BYE team (None).
  2. Pin team[0] at position 0; rotate the remaining N-1 teams clockwise
     once per round.
  3. Each round yields ⌊N/2⌋ real matches (pairs that don't involve BYE).
  4. Total rounds = N-1 for even N, N for odd N.
  5. Home/away assignment: in odd rounds the "pinned" team hosts; in even
     rounds it is the visitor.

The algorithm is deterministic but teams are shuffled before pinning so
each `generate` call produces a different (random) fixture.
"""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.match import Match, MatchStatus
from app.models.team import Team
from app.models.tournament import Tournament
from app.schemas.match import FixtureRead, MatchdayRead, MatchRead, MatchSchedule


# ── Internal helpers ──────────────────────────────────────────────────────────

def _round_robin_pairs(teams: List[int]) -> List[List[tuple[int | None, int | None]]]:
    """
    Generate all rounds of a single round-robin (every team vs every other
    team exactly once).

    Returns a list of rounds; each round is a list of (home_id, away_id)
    tuples. None indicates a BYE (no match for that team that round).
    """
    pool = list(teams)

    # Pad to even number with a BYE sentinel
    bye: int | None = None
    if len(pool) % 2 == 1:
        pool.append(None)  # type: ignore[arg-type]

    n = len(pool)
    rounds: List[List[tuple[int | None, int | None]]] = []

    for rnd in range(n - 1):
        pairs: List[tuple[int | None, int | None]] = []
        for i in range(n // 2):
            a = pool[i]
            b = pool[n - 1 - i]
            # Alternate home/away for the pinned-vs-opponent matchup each round
            if rnd % 2 == 0:
                pairs.append((a, b))
            else:
                pairs.append((b, a))
        rounds.append(pairs)
        # Rotate pool[1:] by one position (pool[0] is pinned)
        pool = [pool[0]] + [pool[-1]] + pool[1:-1]

    return rounds


# ── Public service functions ──────────────────────────────────────────────────

async def _get_tournament_or_404(tid: int, session: AsyncSession) -> Tournament:
    t = await session.get(Tournament, tid)
    if not t:
        raise HTTPException(status_code=404, detail=f"Tournament {tid} not found.")
    return t


async def generate_fixture(tournament_id: int, session: AsyncSession) -> List[Match]:
    """
    Generate a full round-robin fixture for the given tournament and persist
    all Match rows to the database.

    Raises:
        404 – tournament not found
        409 – fixture already exists
        400 – fewer than 2 teams registered
    """
    await _get_tournament_or_404(tournament_id, session)

    # Check for existing fixture
    existing = await session.execute(
        select(Match).where(Match.tournament_id == tournament_id).limit(1)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fixture already exists for this tournament. Delete it first.",
        )

    # Fetch all teams
    result = await session.execute(
        select(Team).where(Team.tournament_id == tournament_id)
    )
    teams: List[Team] = list(result.scalars().all())

    if len(teams) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 teams are required to generate a fixture.",
        )

    # Shuffle for randomness, then extract IDs
    random.shuffle(teams)
    team_ids: List[int] = [t.id for t in teams]  # type: ignore[misc]

    rounds = _round_robin_pairs(team_ids)

    created: List[Match] = []
    for matchday_num, pairs in enumerate(rounds, start=1):
        for home_id, away_id in pairs:
            # Skip BYE matches (one team is None)
            if home_id is None or away_id is None:
                continue

            match = Match(
                tournament_id=tournament_id,
                home_team_id=home_id,
                away_team_id=away_id,
                matchday=matchday_num,
                status=MatchStatus.SCHEDULED,
            )
            session.add(match)
            created.append(match)

    await session.flush()
    # Refresh all to get DB-assigned ids
    for m in created:
        await session.refresh(m)

    return created


async def schedule_match(
    match_id: int,
    data: MatchSchedule,
    session: AsyncSession,
) -> Match:
    """Assign a date/time and optional venue to a match."""
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"Match {match_id} not found.")

    if data.scheduled_at:
        match.scheduled_at = data.scheduled_at.replace(tzinfo=None) if data.scheduled_at.tzinfo else data.scheduled_at
    if data.venue is not None:
        match.venue = data.venue
    match.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    session.add(match)
    await session.flush()
    await session.refresh(match)
    return match


async def get_fixture(tournament_id: int, session: AsyncSession) -> FixtureRead:
    """Return all matches grouped by matchday for a tournament."""
    await _get_tournament_or_404(tournament_id, session)

    result = await session.execute(
        select(Match)
        .where(Match.tournament_id == tournament_id)
        .order_by(Match.matchday, Match.id)
    )
    matches: Sequence[Match] = result.scalars().all()

    # Group by matchday
    by_day: Dict[int, List[MatchRead]] = defaultdict(list)
    for m in matches:
        day = m.matchday or 0
        by_day[day].append(MatchRead.model_validate(m))

    rounds = [
        MatchdayRead(matchday=day, matches=match_list)
        for day, match_list in sorted(by_day.items())
    ]

    return FixtureRead(
        tournament_id=tournament_id,
        total_matchdays=len(rounds),
        rounds=rounds,
    )
