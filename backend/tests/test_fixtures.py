"""
tests/test_fixtures.py

NOM-8 – Tests for the Round-Robin algorithm and fixture endpoints.

Test strategy
─────────────
• Unit tests for _round_robin_pairs() – pure function, no DB needed.
• Integration tests for the three HTTP endpoints using the async test client
  with SQLite in-memory database (via conftest.py fixtures).
"""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import combinations
from typing import List

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.tournament import Tournament
from app.services.fixture_service import _round_robin_pairs


# ═══════════════════════════════════════════════════════════════════════════════
# Unit tests – pure algorithm (no DB, no HTTP)
# ═══════════════════════════════════════════════════════════════════════════════

class TestRoundRobinAlgorithm:
    """Tests for the _round_robin_pairs() helper."""

    def _all_real_pairs(self, rounds):
        """Flatten rounds, dropping BYE pairs (any None)."""
        return [
            (h, a)
            for rnd in rounds
            for (h, a) in rnd
            if h is not None and a is not None
        ]

    # ── Even number of teams ──────────────────────────────────────────────────

    def test_even_teams_round_count(self):
        """N even → N-1 rounds."""
        teams = [1, 2, 3, 4]
        rounds = _round_robin_pairs(teams)
        assert len(rounds) == 3  # 4 teams → 3 rounds

    def test_even_teams_matches_per_round(self):
        """Each round has exactly N/2 pairs (all real, no BYE)."""
        teams = [1, 2, 3, 4]
        rounds = _round_robin_pairs(teams)
        for rnd in rounds:
            assert len(rnd) == 2

    def test_even_teams_all_pairs_played(self):
        """Every pair (i, j) appears exactly once (home/away collapsed)."""
        teams = [1, 2, 3, 4, 5, 6]
        rounds = _round_robin_pairs(teams)
        real = self._all_real_pairs(rounds)

        normalized = {frozenset(p) for p in real}
        expected = {frozenset(p) for p in combinations(teams, 2)}
        assert normalized == expected

    def test_even_teams_no_team_plays_twice_in_round(self):
        """In each round every team appears at most once."""
        teams = [1, 2, 3, 4, 5, 6]
        rounds = _round_robin_pairs(teams)
        for rnd in rounds:
            participants = [t for pair in rnd for t in pair if t is not None]
            assert len(participants) == len(set(participants)), (
                f"Team plays twice in round: {rnd}"
            )

    def test_even_teams_no_self_match(self):
        """No team plays against itself."""
        teams = list(range(1, 9))
        rounds = _round_robin_pairs(teams)
        for h, a in self._all_real_pairs(rounds):
            assert h != a

    # ── Odd number of teams ───────────────────────────────────────────────────

    def test_odd_teams_round_count(self):
        """N odd → N rounds (each team gets one BYE)."""
        teams = [1, 2, 3, 4, 5]
        rounds = _round_robin_pairs(teams)
        assert len(rounds) == 5  # 5 teams → 5 rounds

    def test_odd_teams_bye_count(self):
        """Each team rests exactly once across all rounds."""
        teams = [1, 2, 3, 4, 5]
        rounds = _round_robin_pairs(teams)
        bye_counts: dict[int, int] = {t: 0 for t in teams}
        for rnd in rounds:
            for h, a in rnd:
                if h is None and a is not None:
                    bye_counts[a] += 1
                elif a is None and h is not None:
                    bye_counts[h] += 1
                elif h is None or a is None:
                    # both-None pair counts for the "extra slot"
                    pass
        for team, count in bye_counts.items():
            assert count == 1, f"Team {team} has {count} byes, expected 1"

    def test_odd_teams_all_pairs_played(self):
        """Every real pair plays exactly once (odd case)."""
        teams = [10, 20, 30, 40, 50]
        rounds = _round_robin_pairs(teams)
        real = self._all_real_pairs(rounds)
        normalized = {frozenset(p) for p in real}
        expected = {frozenset(p) for p in combinations(teams, 2)}
        assert normalized == expected

    def test_odd_teams_no_team_plays_twice_in_round(self):
        """No team appears more than once per round (odd case)."""
        teams = [1, 2, 3, 4, 5, 6, 7]
        rounds = _round_robin_pairs(teams)
        for rnd in rounds:
            participants = [t for pair in rnd for t in pair if t is not None]
            assert len(participants) == len(set(participants))

    # ── Edge cases ────────────────────────────────────────────────────────────

    def test_two_teams(self):
        """2 teams → 1 round, 1 match."""
        teams = [1, 2]
        rounds = _round_robin_pairs(teams)
        assert len(rounds) == 1
        real = self._all_real_pairs(rounds)
        assert len(real) == 1
        assert frozenset(real[0]) == frozenset([1, 2])

    def test_three_teams(self):
        """3 teams → 3 rounds, 3 real matches total."""
        teams = [1, 2, 3]
        rounds = _round_robin_pairs(teams)
        assert len(rounds) == 3
        real = self._all_real_pairs(rounds)
        assert len(real) == 3
        normalized = {frozenset(p) for p in real}
        assert normalized == {frozenset([1, 2]), frozenset([1, 3]), frozenset([2, 3])}


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers for integration tests
# ═══════════════════════════════════════════════════════════════════════════════

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
    return t.id  # type: ignore[return-value]


async def _add_teams(client: AsyncClient, tournament_id: int, count: int) -> List[int]:
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
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return ids


# ═══════════════════════════════════════════════════════════════════════════════
# Integration tests – HTTP endpoints
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_generate_fixture_even_teams(client: AsyncClient, session: AsyncSession):
    """Generate fixture for 4 teams → 3 rounds, 6 matches."""
    tid = await _setup_tournament(session, "Even Teams Cup")
    await _add_teams(client, tid, 4)

    r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r.status_code == 201
    matches = r.json()
    # 4 teams → C(4,2) = 6 matches
    assert len(matches) == 6
    # All matchdays between 1 and 3
    matchdays = {m["matchday"] for m in matches}
    assert matchdays == {1, 2, 3}


@pytest.mark.asyncio
async def test_generate_fixture_odd_teams(client: AsyncClient, session: AsyncSession):
    """Generate fixture for 5 teams → 5 rounds, 10 real matches."""
    tid = await _setup_tournament(session, "Odd Teams Cup")
    await _add_teams(client, tid, 5)

    r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r.status_code == 201
    matches = r.json()
    # 5 teams → C(5,2) = 10 matches
    assert len(matches) == 10
    matchdays = {m["matchday"] for m in matches}
    assert matchdays == {1, 2, 3, 4, 5}


@pytest.mark.asyncio
async def test_generate_fixture_no_duplicate_pairs(client: AsyncClient, session: AsyncSession):
    """No pair of teams faces each other more than once."""
    tid = await _setup_tournament(session, "No Dup Cup")
    await _add_teams(client, tid, 6)

    r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r.status_code == 201
    matches = r.json()

    pairs = [frozenset([m["home_team_id"], m["away_team_id"]]) for m in matches]
    assert len(pairs) == len(set(pairs)), "Duplicate pair found!"


@pytest.mark.asyncio
async def test_generate_fixture_conflict(client: AsyncClient, session: AsyncSession):
    """Generating a fixture twice returns HTTP 409."""
    tid = await _setup_tournament(session, "Conflict Cup")
    await _add_teams(client, tid, 4)

    r1 = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r1.status_code == 201

    r2 = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_generate_fixture_too_few_teams(client: AsyncClient, session: AsyncSession):
    """Generating with only 1 team returns HTTP 400."""
    tid = await _setup_tournament(session, "Solo Cup")
    await _add_teams(client, tid, 1)

    r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_generate_fixture_tournament_not_found(client: AsyncClient):
    r = await client.post("/api/v1/tournaments/99999/fixture/generate")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_fixture_grouped_by_matchday(client: AsyncClient, session: AsyncSession):
    """GET fixture returns rounds grouped correctly."""
    tid = await _setup_tournament(session, "Get Fixture Cup")
    await _add_teams(client, tid, 4)
    await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")

    r = await client.get(f"/api/v1/tournaments/{tid}/fixture")
    assert r.status_code == 200
    data = r.json()

    assert data["tournament_id"] == tid
    assert data["total_matchdays"] == 3
    assert len(data["rounds"]) == 3

    # Each round must have 2 matches (4 teams / 2)
    for rnd in data["rounds"]:
        assert len(rnd["matches"]) == 2


@pytest.mark.asyncio
async def test_get_fixture_empty(client: AsyncClient, session: AsyncSession):
    """GET fixture for tournament with no matches returns 0 rounds."""
    tid = await _setup_tournament(session, "Empty Fixture Cup")

    r = await client.get(f"/api/v1/tournaments/{tid}/fixture")
    assert r.status_code == 200
    data = r.json()
    assert data["total_matchdays"] == 0
    assert data["rounds"] == []


@pytest.mark.asyncio
async def test_schedule_match(client: AsyncClient, session: AsyncSession):
    """PATCH /matches/{id}/schedule assigns date and venue correctly."""
    tid = await _setup_tournament(session, "Schedule Cup")
    await _add_teams(client, tid, 4)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    first_match_id = gen_r.json()[0]["id"]

    scheduled_dt = "2025-09-15T18:00:00"
    r = await client.patch(
        f"/api/v1/matches/{first_match_id}/schedule",
        json={"scheduled_at": scheduled_dt, "venue": "Estadio Central"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == first_match_id
    assert data["venue"] == "Estadio Central"
    assert scheduled_dt in data["scheduled_at"]


@pytest.mark.asyncio
async def test_schedule_match_not_found(client: AsyncClient):
    r = await client.patch(
        "/api/v1/matches/99999/schedule",
        json={"scheduled_at": "2025-09-15T18:00:00"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_all_teams_appear_in_fixture(client: AsyncClient, session: AsyncSession):
    """Every team appears as home OR away in at least one match."""
    tid = await _setup_tournament(session, "All Teams Cup")
    team_ids = await _add_teams(client, tid, 6)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    matches = gen_r.json()

    teams_in_fixture = set()
    for m in matches:
        teams_in_fixture.add(m["home_team_id"])
        teams_in_fixture.add(m["away_team_id"])

    assert teams_in_fixture == set(team_ids)


@pytest.mark.asyncio
async def test_no_team_plays_twice_same_matchday(client: AsyncClient, session: AsyncSession):
    """In each matchday, no team appears more than once."""
    tid = await _setup_tournament(session, "No Double Cup")
    await _add_teams(client, tid, 6)

    gen_r = await client.post(f"/api/v1/tournaments/{tid}/fixture/generate")
    matches = gen_r.json()

    from collections import defaultdict
    by_day: dict = defaultdict(list)
    for m in matches:
        by_day[m["matchday"]].append(m)

    for day, day_matches in by_day.items():
        participants = []
        for m in day_matches:
            participants.extend([m["home_team_id"], m["away_team_id"]])
        assert len(participants) == len(set(participants)), (
            f"Matchday {day}: team plays twice!"
        )
