"""
Models package

This file imports all SQLAlchemy models so they can be easily imported elsewhere.
It also ensures all models are loaded before Alembic tries to detect them.

Usage:
    from app.models import Driver, Team, Circuit, Session, SessionResult
    from app.models import Race, RaceResult  # Legacy models
"""

from app.models.driver import Driver
from app.models.team import Team
from app.models.circuit import Circuit
from app.models.session import Session
from app.models.session_result import SessionResult
from app.models.race import Race
from app.models.race_result import RaceResult

# Export all models
__all__ = [
    "Driver",
    "Team",
    "Circuit",
    "Session",
    "SessionResult",
    "Race",
    "RaceResult",
]
