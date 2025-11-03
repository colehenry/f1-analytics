"""
Result Schemas

Pydantic models for API request/response validation for session results.
These schemas define what data the API endpoints will return to the frontend.
"""

from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class CircuitInfo(BaseModel):
    """Circuit metadata embedded in session response"""
    name: str
    location: str
    country: str
    track_length_km: Optional[float] = None

    class Config:
        from_attributes = True


class SessionInfo(BaseModel):
    """
    Session metadata (race, qualifying, sprint, etc.).
    This is the top-level information about a specific F1 session.
    """
    id: int
    year: int
    round: int
    session_type: str  # 'race', 'sprint_race', 'qualifying', 'sprint_qualifying'
    event_name: str
    date: date
    circuit: CircuitInfo

    class Config:
        from_attributes = True


class DriverInfo(BaseModel):
    """Driver metadata embedded in result"""
    driver_number: Optional[int] = None
    driver_code: str
    full_name: str

    class Config:
        from_attributes = True


class TeamInfo(BaseModel):
    """Team metadata embedded in result"""
    name: str
    team_color: Optional[str] = None  # Hex without #

    class Config:
        from_attributes = True


class SessionResultDetail(BaseModel):
    """
    Individual driver's result in a session.

    Contains universal fields (position, status) plus session-specific fields:
    - Race/Sprint: points, time_seconds, fastest_lap, etc.
    - Qualifying: q1_time_seconds, q2_time_seconds, q3_time_seconds
    """
    # Universal fields
    position: Optional[int] = None
    status: str
    headshot_url: Optional[str] = None

    # Embedded driver/team info (from JOINs)
    driver: DriverInfo
    team: TeamInfo

    # Race/Sprint specific (NULL for qualifying)
    grid_position: Optional[int] = None
    points: Optional[float] = None
    laps_completed: Optional[int] = None
    time_seconds: Optional[float] = None
    fastest_lap: bool = False

    # Qualifying specific (NULL for race/sprint)
    q1_time_seconds: Optional[float] = None
    q2_time_seconds: Optional[float] = None
    q3_time_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class SessionResultsResponse(BaseModel):
    """
    Complete response for GET /api/results endpoint.

    Returns session metadata plus an array of driver results.
    Results are typically sorted by position (P1 first).
    """
    session: SessionInfo
    results: List[SessionResultDetail]

    class Config:
        from_attributes = True
