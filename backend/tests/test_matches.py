"""
tests/test_matches.py

Integration tests for match management endpoints:
- GET /api/v1/matches (with tournament_id and matchday filters)
- GET /api/v1/matches/{match_id}
- PATCH /api/v1/matches/{match_id}/status (including LIVE integrity check and 409 conflict)
- PATCH /api/v1/matches/{match_id}/score (live score updates and rejection on finished matches)
- PATCH /api/v1/matches/{match_id}/result (finishing match and updating standings)
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tournament import Tournament


TEAM_BASE = {
    "short_name": "TST",
    "delegate_name": "Delegado Test",
    "city": "Ciudad Test",
    "country": "AR",
}


async def _setup_tournament(session: AsyncSession, name: str = "Liga Test") -> int:
    t = Tournament(name=name, slug=name.lower().replace(" ", "-"), season="2025")
    session.add(t)
    await session.flush()
    await session.refresh(t)
    return t.id


async def _add_teams(client: AsyncClient, tournament_id: int, count: int = 4) -> list[int]:
    ids = []
    for i in range(1, count + 1):
        r = await client.post(
            "/api/v1/teams",
            json={
                **TEAM_BASE,
                "tournament_id": tournament_id,
                "name": f"Equipo {chr(64 + i)}",
                "short_name": f"T{i}",
            },
        )
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


@pytest.mark.asyncio
async def test_list_matches_and_filter(client: AsyncClient, session: AsyncSession):
    tid = await _setup_tournament(session, "Torneo List")
    await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert gen_r.status_code == 201

    # List all matches
    r = await client.get("/api/v1/matches")
    assert r.status_code == 200
    all_matches = r.json()
    assert len(all_matches) >= 6

    # Filter by tournament_id
    r = await client.get(f"/api/v1/matches?tournament_id={tid}")
    assert r.status_code == 200
    tournament_matches = r.json()
    assert len(tournament_matches) == 6
    for m in tournament_matches:
        assert m["tournament_id"] == tid

    # Filter by matchday
    r = await client.get(f"/api/v1/matches?tournament_id={tid}&matchday=1")
    assert r.status_code == 200
    day1_matches = r.json()
    assert len(day1_matches) == 2
    for m in day1_matches:
        assert m["matchday"] == 1


@pytest.mark.asyncio
async def test_get_match_by_id(client: AsyncClient, session: AsyncSession):
    tid = await _setup_tournament(session, "Torneo Get")
    await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    first_match_id = gen_r.json()[0]["id"]

    r = await client.get(f"/api/v1/matches/{first_match_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == first_match_id
    assert data["status"] == "scheduled"
    assert data["started_at"] is None

    # Not found
    r = await client.get("/api/v1/matches/999999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_match_status_and_timer(client: AsyncClient, session: AsyncSession):
    tid = await _setup_tournament(session, "Torneo Status")
    await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    match = gen_r.json()[0]
    match_id = match["id"]

    # Set to LIVE
    r = await client.patch(
        f"/api/v1/matches/{match_id}/status",
        json={"status": "live"},
    )
    assert r.status_code == 200
    live_data = r.json()
    assert live_data["status"] == "live"
    assert live_data["started_at"] is not None

    # Pause back to SCHEDULED
    r = await client.patch(
        f"/api/v1/matches/{match_id}/status",
        json={"status": "scheduled"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "scheduled"


@pytest.mark.asyncio
async def test_team_conflict_two_live_matches(client: AsyncClient, session: AsyncSession):
    """A team cannot play two matches in LIVE status simultaneously."""
    tid = await _setup_tournament(session, "Torneo Conflict")
    await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    matches = gen_r.json()

    # Find match 1 and another match sharing the same team
    match1 = matches[0]
    team_a = match1["home_team_id"]

    # Find another match in fixture involving team_a
    match2 = next(
        m for m in matches[1:]
        if m["home_team_id"] == team_a or m["away_team_id"] == team_a
    )

    # Put match 1 into LIVE
    r1 = await client.patch(
        f"/api/v1/matches/{match1['id']}/status",
        json={"status": "live"},
    )
    assert r1.status_code == 200

    # Attempt to put match 2 into LIVE -> should trigger 409 Conflict
    r2 = await client.patch(
        f"/api/v1/matches/{match2['id']}/status",
        json={"status": "live"},
    )
    assert r2.status_code == 409
    assert "ya está jugando otro partido en VIVO" in r2.json()["detail"]

    # Finish or pause match 1
    r_finish = await client.patch(
        f"/api/v1/matches/{match1['id']}/status",
        json={"status": "finished"},
    )
    assert r_finish.status_code == 200

    # Now match 2 CAN go LIVE
    r2_retry = await client.patch(
        f"/api/v1/matches/{match2['id']}/status",
        json={"status": "live"},
    )
    assert r2_retry.status_code == 200
    assert r2_retry.json()["status"] == "live"


@pytest.mark.asyncio
async def test_update_match_score(client: AsyncClient, session: AsyncSession):
    tid = await _setup_tournament(session, "Torneo Score")
    await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    match_id = gen_r.json()[0]["id"]

    # Update live score
    r = await client.patch(
        f"/api/v1/matches/{match_id}/score",
        json={"home_score": 2, "away_score": 1},
    )
    assert r.status_code == 200
    assert r.json()["home_score"] == 2
    assert r.json()["away_score"] == 1

    # Finish match
    await client.patch(
        f"/api/v1/matches/{match_id}/result",
        json={"home_score": 2, "away_score": 1},
    )

    # Updating score of finished match should fail with 400
    r_fail = await client.patch(
        f"/api/v1/matches/{match_id}/score",
        json={"home_score": 3, "away_score": 1},
    )
    assert r_fail.status_code == 400


@pytest.mark.asyncio
async def test_register_match_result_updates_standings(client: AsyncClient, session: AsyncSession):
    tid = await _setup_tournament(session, "Torneo Standings Update")
    team_ids = await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    match = gen_r.json()[0]
    match_id = match["id"]
    home_id = match["home_team_id"]
    away_id = match["away_team_id"]

    # Register result: home team wins 3-1
    res_r = await client.patch(
        f"/api/v1/matches/{match_id}/result",
        json={"home_score": 3, "away_score": 1},
    )
    assert res_r.status_code == 200
    assert res_r.json()["status"] == "finished"
    assert res_r.json()["finished_at"] is not None

    # Verify standings recalculated
    st_r = await client.get(f"/api/v1/tournaments/{tid}/standings")
    assert st_r.status_code == 200
    standings = st_r.json()
    assert len(standings) == 4

    # Top team should be home_id with 3 points
    winner = standings[0]
    assert winner["team_id"] == home_id
    assert winner["points"] == 3
    assert winner["won"] == 1
    assert winner["goals_for"] == 3
    assert winner["goals_against"] == 1

