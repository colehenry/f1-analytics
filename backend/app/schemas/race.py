from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class RaceWinnerResponse(BaseModel):
    # Race Info
    round: int  # Example: 1
    race_name: str  # Example: "Bahrain Grand Prix"
    date: date  # Example: "2024-03-02"

    # Winner Info
    winner_name: str
    winner_team: str
    winner_had_fastest_lap: bool
    driver_photo_url: Optional[str] = None

    class Config:
        from_attributes = True
