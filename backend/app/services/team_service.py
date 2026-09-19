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
import sqlalchemy as sa
from app.schemas.player import PlayerCreate, PlayerRead
from app.schemas.team import TeamCreate, TeamRead, TeamReadWithPlayers, TeamUpdate


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
    """Register a new club/team in a tournament with unique name & short_name."""
    await _get_tournament_or_404(data.tournament_id, session)

    clean_name = data.name.strip()
    clean_short = data.short_name.strip().upper()

    # 1. Validar nombre único en el torneo
    stmt_name = (
        select(Team)
        .where(Team.tournament_id == data.tournament_id)
        .where(sa.func.lower(sa.func.trim(Team.name)) == clean_name.lower())
    )
    existing_name = (await session.execute(stmt_name)).scalars().first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un equipo con el nombre '{clean_name}' en este torneo.",
        )

    # 2. Validar sigla / abreviatura única en el torneo
    stmt_short = (
        select(Team)
        .where(Team.tournament_id == data.tournament_id)
        .where(sa.func.lower(sa.func.trim(Team.short_name)) == clean_short.lower())
    )
    existing_short = (await session.execute(stmt_short)).scalars().first()
    if existing_short:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un equipo con la sigla o abreviatura '{clean_short}' en este torneo.",
        )

    team = Team(
        tournament_id=data.tournament_id,
        name=clean_name,
        short_name=clean_short,
        sport=data.sport,
        delegate_name=data.delegate_name.strip(),
        delegate_phone=data.delegate_phone.strip() if data.delegate_phone else None,
        city=data.city.strip() if data.city else None,
        country=data.country.strip() if data.country else None,
        logo_url=data.logo_url,
    )
    session.add(team)
    try:
        await session.flush()          # get the generated id before commit
        await session.refresh(team)
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error de integridad: ya existe un equipo con datos duplicados en el torneo.",
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
    include_players: bool = False,
) -> Sequence[Union[Team, TeamReadWithPlayers]]:
    stmt = select(Team)
    if tournament_id is not None:
        stmt = stmt.where(Team.tournament_id == tournament_id)
    result = await session.execute(stmt)
    teams = list(result.scalars().all())

    if not include_players or not teams:
        return teams

    # Cargar jugadores de todos los equipos en una única consulta eficiente
    team_ids = [t.id for t in teams if t.id is not None]
    stmt_players = select(Player).where(Player.team_id.in_(team_ids))
    players_result = await session.execute(stmt_players)
    all_players = players_result.scalars().all()

    players_by_team: dict[int, list[Player]] = {tid: [] for tid in team_ids}
    for p in all_players:
        if p.team_id in players_by_team:
            players_by_team[p.team_id].append(p)

    return [
        TeamReadWithPlayers(
            **t.model_dump(),
            players=[PlayerRead.model_validate(p) for p in players_by_team.get(t.id, [])],
        )
        for t in teams
    ]


async def update_team(
    team_id: int, data: TeamUpdate, session: AsyncSession
) -> Team:
    team = await get_team(team_id, session)

    if data.name is not None:
        clean_name = data.name.strip()
        stmt_name = (
            select(Team)
            .where(Team.tournament_id == team.tournament_id)
            .where(Team.id != team_id)
            .where(sa.func.lower(sa.func.trim(Team.name)) == clean_name.lower())
        )
        if (await session.execute(stmt_name)).scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un equipo con el nombre '{clean_name}' en este torneo.",
            )

    if data.short_name is not None:
        clean_short = data.short_name.strip().upper()
        stmt_short = (
            select(Team)
            .where(Team.tournament_id == team.tournament_id)
            .where(Team.id != team_id)
            .where(sa.func.lower(sa.func.trim(Team.short_name)) == clean_short.lower())
        )
        if (await session.execute(stmt_short)).scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un equipo con la sigla '{clean_short}' en este torneo.",
            )

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

