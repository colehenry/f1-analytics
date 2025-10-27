from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, between
from typing import List
from itertools import groupby

from app.database import get_db
from app.models import Race, RaceResult, Driver, Team
from app.schemas.podium import RacePodiumResponse

router = APIRouter()


@router.get("/{season}", response_model=List[RacePodiumResponse])
async def get_podium_finishers(season: int, db: AsyncSession = Depends(get_db)):
    """
    Get podium finishers and their info for a given season.
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
        .where(Race.season == season)
        .where(between(RaceResult.position, 1, 3))
        .order_by(
            Race.round,
            RaceResult.position,
        )
    )

    result = await db.execute(query)
    podiums = result.all()

    grouped_races = []
    for race_key, race_group in groupby(podiums, key=lambda x: (x.round)):
        race_rows = list(race_group)

        # Now race_rows = [1st place row, 2nd place row, 3rd place row]
        # Extract the first row for race info (all rows have same race data)
        first_row = race_rows[0]

        # Build lists by extracting from each row
        grouped_races.append(
            RacePodiumResponse(
                year=first_row.season,
                round=first_row.round,
                race_name=first_row.name,
                date=first_row.date,
                podium_drivers=[row.full_name for row in race_rows],
                podium_teams=[row.name_1 for row in race_rows],  # Check this field name
                podium_colors=[row.team_color for row in race_rows],
                podium_fastest_laps=[row.fastest_lap for row in race_rows],
                headshot_urls=[row.default_headshot_url for row in race_rows],
            )
        )

    return grouped_races
