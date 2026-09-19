from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.tournament import Tournament
from app.schemas.tournament import TournamentRead, TournamentUpdate, TournamentCreate

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])

import uuid
from sqlalchemy.exc import IntegrityError

@router.post("", response_model=TournamentRead, status_code=201)
async def create_tournament(tournament_in: TournamentCreate, db: AsyncSession = Depends(get_session)):
    # Verificar si el torneo 1 ya existe
    existing = await db.get(Tournament, 1)
    if existing:
        return existing

    tournament = Tournament.model_validate(tournament_in)
    tournament.id = 1 # Forzar ID 1 porque el frontend lo tiene hardcodeado
    # Asegurar un slug único si llegara a chocar
    tournament.slug = f"{tournament_in.slug}-{uuid.uuid4().hex[:6]}"
    
    db.add(tournament)
    try:
        await db.commit()
        await db.refresh(tournament)
        return tournament
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al crear el torneo. Verifica los datos.")

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
