from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class RacePodiumResponse(BaseModel):
    """
    Represents one snapshot of race results:
    - Drivers on podium of a specific race
    """

    # Full season info
    year: int  # Example: 2024
    round: int  # Example: 1
    race_name: str  # Example: "Bahrain Grand Prix"
    date: date  # Example: "2024-03-02"

    # Winner Info
    podium_drivers: List[str]
    podium_teams: List[str]
    podium_colors: List[str]
    podium_fastest_laps: List[bool]  # [False, False, True]
    headshot_urls: List[Optional[str]]

    class Config:
        from_attributes = True
