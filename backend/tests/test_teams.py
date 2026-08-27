"""
tests/test_teams.py

Tests for NOM-7: Team & Player endpoints with DNI validation.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tournament import Tournament, TournamentFormat


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _create_tournament(session: AsyncSession, name: str = "Liga Test") -> int:
    """Insert a tournament directly into the DB and return its id."""
    t = Tournament(name=name, slug=name.lower().replace(" ", "-"), season="2025")
    session.add(t)
    await session.flush()
    await session.refresh(t)
    return t.id  # type: ignore[return-value]


TEAM_PAYLOAD = {
    "name": "Atlético Python",
    "short_name": "ATP",
    "delegate_name": "Juan Pérez",
    "delegate_phone": "+54 11 1234-5678",
    "city": "Buenos Aires",
    "country": "Argentina",
}

PLAYER_PAYLOAD = {
    "first_name": "Carlos",
    "last_name": "Gómez",
    "dni": "12345678",
    "shirt_number": 10,
    "position": "midfielder",
}


# ── Team endpoints ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_team_success(client: AsyncClient, session: AsyncSession):
    t_id = await _create_tournament(session)
    payload = {**TEAM_PAYLOAD, "tournament_id": t_id}
    resp = await client.post("/api/v1/teams", json=payload)

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Atlético Python"
    assert data["short_name"] == "ATP"
    assert data["delegate_name"] == "Juan Pérez"
    assert data["tournament_id"] == t_id


@pytest.mark.asyncio
async def test_register_team_tournament_not_found(client: AsyncClient):
    payload = {**TEAM_PAYLOAD, "tournament_id": 99999}
    resp = await client.post("/api/v1/teams", json=payload)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient, session: AsyncSession):
    t_id = await _create_tournament(session, "Lista Test")
    payload = {**TEAM_PAYLOAD, "tournament_id": t_id, "name": "FC Lista", "short_name": "FCL"}
    await client.post("/api/v1/teams", json=payload)

    resp = await client.get("/api/v1/teams", params={"tournament_id": t_id})
    assert resp.status_code == 200
    teams = resp.json()
    assert len(teams) >= 1
    assert any(t["name"] == "FC Lista" for t in teams)


@pytest.mark.asyncio
async def test_get_team_with_players(client: AsyncClient, session: AsyncSession):
    t_id = await _create_tournament(session, "Get Team Test")
    team_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Get FC", "short_name": "GFC"},
    )
    team_id = team_resp.json()["id"]

    # Add a player first
    await client.post(f"/api/v1/teams/{team_id}/players", json=PLAYER_PAYLOAD)

    resp = await client.get(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Get FC"
    assert len(data["players"]) == 1
    assert data["players"][0]["dni"] == "12345678"


@pytest.mark.asyncio
async def test_get_team_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/teams/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_team(client: AsyncClient, session: AsyncSession):
    t_id = await _create_tournament(session, "Update Test")
    team_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Old Name FC", "short_name": "ONF"},
    )
    team_id = team_resp.json()["id"]

    resp = await client.patch(
        f"/api/v1/teams/{team_id}",
        json={"name": "New Name FC", "delegate_phone": "+54 11 9999-0000"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name FC"
    assert resp.json()["delegate_phone"] == "+54 11 9999-0000"


# ── Player endpoints & DNI validation ────────────────────────────────────────

@pytest.mark.asyncio
async def test_add_player_success(client: AsyncClient, session: AsyncSession):
    t_id = await _create_tournament(session, "Player Success Test")
    team_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Player FC", "short_name": "PLF"},
    )
    team_id = team_resp.json()["id"]

    resp = await client.post(f"/api/v1/teams/{team_id}/players", json=PLAYER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["dni"] == "12345678"
    assert data["first_name"] == "Carlos"
    assert data["team_id"] == team_id


@pytest.mark.asyncio
async def test_add_player_duplicate_dni_same_tournament(client: AsyncClient, session: AsyncSession):
    """
    Adding a player with the same DNI to two different teams in the SAME tournament
    must fail with HTTP 400.
    """
    t_id = await _create_tournament(session, "DNI Dup Test")

    # Team A
    team_a_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Team A", "short_name": "TMA"},
    )
    team_a_id = team_a_resp.json()["id"]

    # Team B  
    team_b_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Team B", "short_name": "TMB"},
    )
    team_b_id = team_b_resp.json()["id"]

    # Register player in Team A – should succeed
    r1 = await client.post(
        f"/api/v1/teams/{team_a_id}/players",
        json={**PLAYER_PAYLOAD, "dni": "99887766"},
    )
    assert r1.status_code == 201

    # Register same DNI in Team B – must fail
    r2 = await client.post(
        f"/api/v1/teams/{team_b_id}/players",
        json={**PLAYER_PAYLOAD, "dni": "99887766"},
    )
    assert r2.status_code == 400
    assert "99887766" in r2.json()["detail"]


@pytest.mark.asyncio
async def test_add_player_same_dni_different_tournaments(client: AsyncClient, session: AsyncSession):
    """
    Same DNI in two DIFFERENT tournaments must succeed.
    """
    t1_id = await _create_tournament(session, "Tournament Alpha")
    t2_id = await _create_tournament(session, "Tournament Beta")

    team_1_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t1_id, "name": "Alpha FC", "short_name": "AFC"},
    )
    team_2_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t2_id, "name": "Beta FC", "short_name": "BFC"},
    )

    r1 = await client.post(
        f"/api/v1/teams/{team_1_resp.json()['id']}/players",
        json={**PLAYER_PAYLOAD, "dni": "55443322"},
    )
    r2 = await client.post(
        f"/api/v1/teams/{team_2_resp.json()['id']}/players",
        json={**PLAYER_PAYLOAD, "dni": "55443322"},
    )
    assert r1.status_code == 201
    assert r2.status_code == 201


@pytest.mark.asyncio
async def test_add_player_team_not_found(client: AsyncClient):
    resp = await client.post("/api/v1/teams/99999/players", json=PLAYER_PAYLOAD)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_players(client: AsyncClient, session: AsyncSession):
    t_id = await _create_tournament(session, "List Players Test")
    team_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Roster FC", "short_name": "RFC"},
    )
    team_id = team_resp.json()["id"]

    # Add 2 players
    await client.post(
        f"/api/v1/teams/{team_id}/players",
        json={**PLAYER_PAYLOAD, "dni": "11111111"},
    )
    await client.post(
        f"/api/v1/teams/{team_id}/players",
        json={**PLAYER_PAYLOAD, "first_name": "Luis", "dni": "22222222", "shirt_number": 9},
    )

    resp = await client.get(f"/api/v1/teams/{team_id}/players")
    assert resp.status_code == 200
    players = resp.json()
    assert len(players) == 2
    dni_list = [p["dni"] for p in players]
    assert "11111111" in dni_list
    assert "22222222" in dni_list


@pytest.mark.asyncio
async def test_dni_normalized_uppercase(client: AsyncClient, session: AsyncSession):
    """DNI input is normalized to uppercase before storage/comparison."""
    t_id = await _create_tournament(session, "DNI Normalize Test")
    team_resp = await client.post(
        "/api/v1/teams",
        json={**TEAM_PAYLOAD, "tournament_id": t_id, "name": "Normalize FC", "short_name": "NFC"},
    )
    team_id = team_resp.json()["id"]

    # Register with lowercase DNI
    r1 = await client.post(
        f"/api/v1/teams/{team_id}/players",
        json={**PLAYER_PAYLOAD, "dni": "abc123"},
    )
    assert r1.status_code == 201

    # Try again with uppercase – must fail as duplicate
    r2 = await client.post(
        f"/api/v1/teams/{team_id}/players",
        json={**PLAYER_PAYLOAD, "dni": "ABC123"},
    )
    assert r2.status_code == 400
