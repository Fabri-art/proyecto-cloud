"""
app/models/__init__.py

Import all models here so that SQLModel.metadata is populated when Alembic
generates migrations. The order matters: parent tables before child tables.
"""

from app.models.tournament import Tournament, TournamentFormat, TournamentStatus  # noqa: F401
from app.models.team import Team  # noqa: F401
from app.models.player import Player, PlayerPosition  # noqa: F401
from app.models.match import Match, MatchStatus  # noqa: F401
from app.models.standing import Standing  # noqa: F401

__all__ = [
    "Tournament",
    "TournamentFormat",
    "TournamentStatus",
    "Team",
    "Player",
    "PlayerPosition",
    "Match",
    "MatchStatus",
    "Standing",
]
