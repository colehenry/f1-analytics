from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, between
from typing import List
from itertools import groupby

from app.database import get_db
from app.models import Race, RaceResult, Driver, Team
from app.schemas.result import ResultResponse

router = APIRouter()


@router.get("/{year}/{round}/{event_type}", response_model=ResultResponse)
async def get_event_reults(
    year: int, round: int, event_type: str, db: AsyncSession = Depends(get_db)
):
    """
    Given a specific year, round, and event type, returns the results of the session in descending finishing order.
    """

    query = (
        select(
            Race.season,
            Race.round,
            Race.name,
            Race.date,
            Driver.full_name,
            Team.name,
            Team.team_color,
            RaceResult.position,
            RaceResult.fastest_lap,
            Driver.default_headshot_url,
        )
        .join(RaceResult, Race.id == RaceResult.race_id)
        .join(Driver, RaceResult.driver_id == Driver.id)
        .join(Team, RaceResult.team_id == Team.id)
        .where(Race.season == year)
        .where(Race.round == round)
        .order_by(
            Race.round,
            RaceResult.position,
        )
    )
