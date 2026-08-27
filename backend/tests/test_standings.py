"""
tests/test_standings.py
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tournament import Tournament
from app.models.match import MatchStatus


TEAM_BASE = {
    "short_name": "TST",
    "delegate_name": "Delegado Test",
    "city": "Ciudad",
    "country": "AR",
}


async def _setup_tournament(session: AsyncSession, name: str) -> int:
    t = Tournament(name=name, slug=name.lower().replace(" ", "-"), season="2025")
    session.add(t)
    await session.flush()
    await session.refresh(t)
    return t.id  # type: ignore[return-value]


async def _add_teams(client: AsyncClient, tournament_id: int, count: int) -> list[int]:
    ids = []
    for i in range(count):
        r = await client.post(
            "/api/v1/teams",
            json={
                **TEAM_BASE,
                "tournament_id": tournament_id,
                "name": f"Team {i + 1}",
                "short_name": f"T{i + 1}",
            },
        )
        assert r.status_code == 201
        ids.append(r.json()["id"])
    return ids


@pytest.mark.asyncio
async def test_update_match_result_and_standings(client: AsyncClient, session: AsyncSession):
    # Setup
    tid = await _setup_tournament(session, "Standings Cup")
    team_ids = await _add_teams(client, tid, 4)
    
    # Generate fixture
    r_gen = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r_gen.status_code == 201
    matches = r_gen.json()
    
    # Check initial standings (empty or zeros)
    r_stand = await client.get(f"/api/v1/tournaments/{tid}/standings")
    assert r_stand.status_code == 200
    standings = r_stand.json()
    assert len(standings) == 4
    for s in standings:
        assert s["played"] == 0
        assert s["points"] == 0
        
    # Get one match
    match1 = matches[0]
    m1_id = match1["id"]
    home_id = match1["home_team_id"]
    away_id = match1["away_team_id"]
    
    # Update result: Home 2 - 1 Away
    r_patch = await client.patch(
        f"/api/v1/matches/{m1_id}/result",
        json={"home_score": 2, "away_score": 1}
    )
    assert r_patch.status_code == 200
    m_updated = r_patch.json()
    assert m_updated["home_score"] == 2
    assert m_updated["away_score"] == 1
    assert m_updated["status"] == MatchStatus.FINISHED.value
    
    # Verify standings calculation
    r_stand = await client.get(f"/api/v1/tournaments/{tid}/standings")
    assert r_stand.status_code == 200
    new_standings = r_stand.json()
    
    # Home team should have 3 pts, +1 DG
    home_standing = next(s for s in new_standings if s["team_id"] == home_id)
    assert home_standing["played"] == 1
    assert home_standing["won"] == 1
    assert home_standing["points"] == 3
    assert home_standing["goals_for"] == 2
    assert home_standing["goals_against"] == 1
    assert home_standing["goal_difference"] == 1
    assert home_standing["position"] == 1
    
    # Away team should have 0 pts, -1 DG
    away_standing = next(s for s in new_standings if s["team_id"] == away_id)
    assert away_standing["played"] == 1
    assert away_standing["lost"] == 1
    assert away_standing["points"] == 0
    assert away_standing["goal_difference"] == -1
    
    # Another match: Draw 1 - 1
    match2 = matches[1]
    m2_id = match2["id"]
    h2_id = match2["home_team_id"]
    a2_id = match2["away_team_id"]
    
    r_patch2 = await client.patch(
        f"/api/v1/matches/{m2_id}/result",
        json={"home_score": 1, "away_score": 1}
    )
    assert r_patch2.status_code == 200
    
    # Verify standings again
    r_stand2 = await client.get(f"/api/v1/tournaments/{tid}/standings")
    new_standings2 = r_stand2.json()
    
    h2_standing = next(s for s in new_standings2 if s["team_id"] == h2_id)
    a2_standing = next(s for s in new_standings2 if s["team_id"] == a2_id)
    
    assert h2_standing["played"] == 1
    assert h2_standing["drawn"] == 1
    assert h2_standing["points"] == 1
    assert a2_standing["played"] == 1
    assert a2_standing["drawn"] == 1
    assert a2_standing["points"] == 1
    
    # Wait, they are tied in points (1), GD (0), GF (1). Order between them might be arbitrary but handled by sort
    
    # Check 404 for match update
    r_404 = await client.patch(f"/api/v1/matches/99999/result", json={"home_score": 0, "away_score": 0})
    assert r_404.status_code == 404
