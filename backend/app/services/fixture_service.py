"""
app/services/fixture_service.py

NOM-8 – Round-Robin fixture generator, delete, and scheduling logic.

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
from typing import Dict, List, Optional, Sequence, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete as sql_delete
from sqlmodel import select

from app.models.match import Match, MatchStatus
from app.models.player import Player
from app.models.standing import Standing
from app.models.team import Team
from app.models.tournament import Tournament
from app.schemas.match import FixtureDeleteInfo, FixtureRead, MatchdayRead, MatchRead, MatchSchedule


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


async def _count_played_matches(tournament_id: int, session: AsyncSession) -> Tuple[int, int]:
    """
    Returns (total_matches, played_matches) for the given tournament.
    'played' means status FINISHED or LIVE (have real score data).
    """
    all_result = await session.execute(
        select(Match).where(Match.tournament_id == tournament_id)
    )
    all_matches: Sequence[Match] = all_result.scalars().all()
    total = len(all_matches)
    played = sum(
        1 for m in all_matches
        if m.status in (MatchStatus.FINISHED, MatchStatus.LIVE)
    )
    return total, played


async def delete_fixture(
    tournament_id: int,
    session: AsyncSession,
    force: bool = False,
    delete_teams: bool = False,
) -> FixtureDeleteInfo:
    """
    Elimina todos los partidos (y standings asociados) del torneo indicado.

    Args:
        tournament_id: ID del torneo.
        session:       Sesión de base de datos activa.
        force:         Si False (default), lanza HTTP 409 cuando existen partidos
                       FINISHED o LIVE (datos ya jugados).
                       Si True, elimina todo sin importar el estado.
        delete_teams:  Si True, también elimina todos los equipos y jugadores.

    Returns:
        FixtureDeleteInfo con información sobre los partidos eliminados.

    Raises:
        404 – Torneo no encontrado.
        409 – Hay partidos jugados y force=False.
    """
    await _get_tournament_or_404(tournament_id, session)

    total_matches, played_matches = await _count_played_matches(tournament_id, session)

    if played_matches > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"El fixture tiene {played_matches} partido(s) con resultados registrados "
                f"(FINALIZADO o EN JUEGO). Usa force=true para eliminar igualmente. "
                f"⚠️ Se perderán todos los marcadores y estadísticas."
            ),
        )

    had_played = played_matches > 0

    # 1. Eliminar standings de este torneo (integridad referencial)
    await session.execute(
        sql_delete(Standing).where(Standing.tournament_id == tournament_id)
    )

    # 2. Eliminar partidos de este torneo
    await session.execute(
        sql_delete(Match).where(Match.tournament_id == tournament_id)
    )

    # 3. Obtener todos los IDs de equipos del torneo
    team_ids_res = await session.execute(
        select(Team.id).where(Team.tournament_id == tournament_id)
    )
    team_ids = [t for t in team_ids_res.scalars().all() if t is not None]

    deleted_players = 0
    if delete_teams and team_ids:
        # Eliminar jugadores asociados a estos equipos
        players_count_res = await session.execute(
            select(Player.id).where(Player.team_id.in_(team_ids))
        )
        deleted_players = len(players_count_res.scalars().all())
        await session.execute(
            sql_delete(Player).where(Player.team_id.in_(team_ids))
        )

        # 4. Eliminar todos los equipos del torneo
        await session.execute(
            sql_delete(Team).where(Team.tournament_id == tournament_id)
        )

    await session.flush()

    return FixtureDeleteInfo(
        tournament_id=tournament_id,
        deleted_matches=total_matches,
        had_played_matches=had_played,
        deleted_teams=len(team_ids) if delete_teams else 0,
        deleted_players=deleted_players,
    )


async def generate_fixture(
    tournament_id: int,
    session: AsyncSession,
    force: bool = False,
) -> List[Match]:
    """
    Generate a full round-robin fixture for the given tournament and persist
    all Match rows to the database.

    Args:
        tournament_id: ID del torneo.
        session:       Sesión de base de datos activa.
        force:         Si True, elimina el fixture existente y todos los equipos
                       asociados, retornando el fixture reseteado listo para
                       nuevos equipos.
                       Si False (default), lanza HTTP 409 si ya existe un fixture.

    Raises:
        404 – tournament not found
        409 – fixture already exists and force=False
        400 – fewer than 2 teams registered
    """
    await _get_tournament_or_404(tournament_id, session)

    # Check for existing fixture
    existing = await session.execute(
        select(Match).where(Match.tournament_id == tournament_id).limit(1)
    )
    if existing.scalars().first():
        if not force:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Fixture already exists for this tournament. "
                    "Delete it first, or use force=true to reset and regenerate."
                ),
            )
        # force=True → eliminar fixture existente (NO equipos) atómicamente
        await delete_fixture(tournament_id, session, force=True, delete_teams=False)

    # Fetch all teams
    result = await session.execute(
        select(Team).where(Team.tournament_id == tournament_id)
    )
    teams: List[Team] = list(result.scalars().all())

    if len(teams) < 2:
        if force:
            # Al regenerar forzadamente tras borrar los equipos,
            # el fixture queda vacío listo para la inscripción de nuevos equipos.
            return []
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requieren al menos 2 equipos registrados para generar el fixture.",
        )

    # Group teams by sport
    teams_by_sport: Dict[str, List[int]] = defaultdict(list)
    for t in teams:
        teams_by_sport[t.sport].append(t.id) # type: ignore[misc]

    # Generate rounds per sport independently
    all_rounds: List[List[tuple[int | None, int | None]]] = []
    for sport, ids in teams_by_sport.items():
        if len(ids) < 2:
            continue
        
        # Shuffle for randomness
        random.shuffle(ids)
        sport_rounds = _round_robin_pairs(ids)
        
        # Merge sport_rounds into all_rounds
        for i, pairs in enumerate(sport_rounds):
            if len(all_rounds) <= i:
                all_rounds.append([])
            all_rounds[i].extend(pairs)

    if not all_rounds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay suficientes equipos de la misma disciplina para armar partidos.",
        )

    created: List[Match] = []
    for matchday_num, pairs in enumerate(all_rounds, start=1):
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

