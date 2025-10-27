from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, desc
from typing import List

from app.database import get_db
from app.models import Race, RaceResult, Driver, Team
from app.schemas.race import RaceWinnerResponse

router = APIRouter()


@router.get("/seasons", response_model=List[int])
async def get_available_seasons(db: AsyncSession = Depends(get_db)):
    """
    Return a List[int] with all the seasons for which we currently have complete (or partial for current season) data for in the db.
    Example: [2024, 2023, 2022]
    """

    query = select(Race.season).distinct().order_by(Race.season.desc())

    result = await db.execute(query)
    seasons = result.scalars().all()

    return seasons


@router.get("/{season}", response_model=List[RaceWinnerResponse])
async def get_races_with_winners(season: int, db: AsyncSession = Depends(get_db)):
    """
    Get all races for a season with winner information.

    Example. GET /api/races/2024
    """

    # Query: Get all races for the season, joined with results to find winners
    # We need to join Race -> RaceResult (position=1) -> Driver, Team

    query = (
        select(
            Race.round,
            Race.name,
            Race.date,
            Driver.full_name,  # winner's name
            Team.name,  # winner's team
            RaceResult.fastest_lap,
            RaceResult.headshot_url,
        )
        .join(RaceResult, Race.id == RaceResult.race_id)
        .join(Driver, RaceResult.driver_id == Driver.id)
        .join(Team, RaceResult.team_id == Team.id)
        .where(Race.season == season)
        .where(RaceResult.position == 1)  # only winners
        .order_by(Race.round)
    )

    result = await db.execute(query)
    races = result.all()

    # Convert to response format
    return [
        RaceWinnerResponse(
            round=race.round,
            race_name=race.name,
            date=race.date,
            winner_name=race.full_name,
            winner_team=race.name_1,
            winner_had_fastest_lap=race.fastest_lap,
            driver_photo_url=race.headshot_url,
        )
        for race in races
    ]
