from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.tournament import Tournament
from app.schemas.tournament import TournamentRead, TournamentUpdate

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])

@router.get("/{tournament_id}", response_model=TournamentRead)
async def get_tournament(tournament_id: int, db: AsyncSession = Depends(get_session)):
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament

@router.patch("/{tournament_id}", response_model=TournamentRead)
async def update_tournament(tournament_id: int, tournament_in: TournamentUpdate, db: AsyncSession = Depends(get_session)):
    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    update_data = tournament_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tournament, key, value)
        
    db.add(tournament)
    await db.commit()
    await db.refresh(tournament)
    return tournament
