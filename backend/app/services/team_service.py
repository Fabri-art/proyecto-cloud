"""
app/services/team_service.py

Business logic for team registration and player DNI validation (NOM-7).
"""
from __future__ import annotations

from typing import List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.player import Player
from app.models.team import Team
from app.models.tournament import Tournament
from app.schemas.player import PlayerCreate
from app.schemas.team import TeamCreate, TeamUpdate


# ── Tournament helpers ────────────────────────────────────────────────────────

async def _get_tournament_or_404(
    tournament_id: int, session: AsyncSession
) -> Tournament:
    result = await session.get(Tournament, tournament_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tournament {tournament_id} not found.",
        )
    return result


# ── Team CRUD ─────────────────────────────────────────────────────────────────

async def create_team(data: TeamCreate, session: AsyncSession) -> Team:
    """Register a new club/team in a tournament."""
    await _get_tournament_or_404(data.tournament_id, session)

    team = Team(**data.model_dump())
    session.add(team)
    try:
        await session.flush()          # get the generated id before commit
        await session.refresh(team)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A team with this name already exists in the tournament.",
        ) from exc
    return team


async def get_team(team_id: int, session: AsyncSession) -> Team:
    result = await session.get(Team, team_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team {team_id} not found.",
        )
    return result


async def list_teams(
    session: AsyncSession,
    tournament_id: Optional[int] = None,
) -> Sequence[Team]:
    stmt = select(Team)
    if tournament_id is not None:
        stmt = stmt.where(Team.tournament_id == tournament_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_team(
    team_id: int, data: TeamUpdate, session: AsyncSession
) -> Team:
    team = await get_team(team_id, session)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(team, key, value)
    session.add(team)
    await session.flush()
    await session.refresh(team)
    return team


# ── Player CRUD + DNI validation ──────────────────────────────────────────────

async def _check_dni_duplicate(
    dni: str, tournament_id: int, session: AsyncSession
) -> None:
    """Raise HTTP 400 if the DNI is already registered in this tournament."""
    stmt = (
        select(Player)
        .join(Team, Player.team_id == Team.id)  # type: ignore[arg-type]
        .where(Team.tournament_id == tournament_id)
        .where(Player.dni == dni)
    )
    result = await session.execute(stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"A player with DNI '{dni}' is already registered "
                f"in tournament {tournament_id}."
            ),
        )


async def add_player_to_team(
    team_id: int, data: PlayerCreate, session: AsyncSession
) -> Player:
    """Register a player into a team, enforcing DNI uniqueness per tournament."""
    team = await get_team(team_id, session)
    await _check_dni_duplicate(data.dni, team.tournament_id, session)

    player = Player(team_id=team_id, **data.model_dump())
    session.add(player)
    try:
        await session.flush()
        await session.refresh(player)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not register player. Check for duplicate shirt number.",
        ) from exc
    return player


async def get_team_players(
    team_id: int, session: AsyncSession
) -> List[Player]:
    """Return the roster of a team."""
    await get_team(team_id, session)   # ensures team exists
    stmt = select(Player).where(Player.team_id == team_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())

