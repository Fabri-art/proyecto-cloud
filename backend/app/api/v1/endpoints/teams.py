"""
app/api/v1/endpoints/teams.py

Endpoints for NOM-7: Team & Player registration with DNI validation.

Routes:
    POST   /api/v1/teams                          → Register a club/team
    GET    /api/v1/teams                          → List teams (optional ?tournament_id=)
    GET    /api/v1/teams/{team_id}                → Get team + roster
    PATCH  /api/v1/teams/{team_id}                → Update team info
    POST   /api/v1/teams/{team_id}/players        → Add a player (DNI validated)
    GET    /api/v1/teams/{team_id}/players        → List players in a team
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.schemas.player import PlayerCreate, PlayerRead
from app.schemas.team import TeamCreate, TeamRead, TeamReadWithPlayers, TeamUpdate
from app.services import team_service

router = APIRouter(prefix="/teams", tags=["Teams & Players"])


# ── Teams ─────────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=TeamRead,
    status_code=201,
    summary="Register a club/team",
    description="Register a new football club in a tournament. Requires a delegate name.",
)
async def register_team(
    body: TeamCreate,
    session: AsyncSession = Depends(get_session),
) -> TeamRead:
    team = await team_service.create_team(body, session)
    return TeamRead.model_validate(team)


@router.get(
    "",
    response_model=List[TeamRead],
    summary="List teams",
    description="List all teams. Filter by `tournament_id` query param.",
)
async def list_teams(
    tournament_id: Optional[int] = Query(default=None, description="Filter by tournament"),
    session: AsyncSession = Depends(get_session),
) -> List[TeamRead]:
    teams = await team_service.list_teams(session, tournament_id=tournament_id)
    return [TeamRead.model_validate(t) for t in teams]


@router.get(
    "/{team_id}",
    response_model=TeamReadWithPlayers,
    summary="Get team with full roster",
)
async def get_team(
    team_id: int,
    session: AsyncSession = Depends(get_session),
) -> TeamReadWithPlayers:
    team = await team_service.get_team(team_id, session)
    players = await team_service.get_team_players(team_id, session)
    data = TeamReadWithPlayers.model_validate(team)
    data.players = [PlayerRead.model_validate(p) for p in players]
    return data


@router.patch(
    "/{team_id}",
    response_model=TeamRead,
    summary="Update team information",
)
async def update_team(
    team_id: int,
    body: TeamUpdate,
    session: AsyncSession = Depends(get_session),
) -> TeamRead:
    team = await team_service.update_team(team_id, body, session)
    return TeamRead.model_validate(team)


# ── Players ───────────────────────────────────────────────────────────────────

@router.post(
    "/{team_id}/players",
    response_model=PlayerRead,
    status_code=201,
    summary="Add a player to a team",
    description=(
        "Register a player into a team. "
        "Returns HTTP 400 if the player's DNI is already registered in the same tournament."
    ),
)
async def add_player(
    team_id: int,
    body: PlayerCreate,
    session: AsyncSession = Depends(get_session),
) -> PlayerRead:
    player = await team_service.add_player_to_team(team_id, body, session)
    return PlayerRead.model_validate(player)


@router.get(
    "/{team_id}/players",
    response_model=List[PlayerRead],
    summary="List players in a team",
)
async def list_players(
    team_id: int,
    session: AsyncSession = Depends(get_session),
) -> List[PlayerRead]:
    players = await team_service.get_team_players(team_id, session)
    return [PlayerRead.model_validate(p) for p in players]
