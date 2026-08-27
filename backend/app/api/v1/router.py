from fastapi import APIRouter

from app.api.v1.endpoints import fixtures, health, teams, matches, standings

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(teams.router)
api_router.include_router(fixtures.router)
api_router.include_router(matches.router)
api_router.include_router(standings.router)

# Future routers – uncomment as you implement them:
# from app.api.v1.endpoints import tournaments, players
# api_router.include_router(tournaments.router)
# api_router.include_router(players.router)

