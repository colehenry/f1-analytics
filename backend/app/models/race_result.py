"""
RaceResult Model

Represents a single driver's result in a specific race.
This is the "join table" that connects races, drivers, and teams with performance data.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Interval
from sqlalchemy.orm import relationship

from app.database import Base


class RaceResult(Base):
    """
    Represents a driver's performance in a specific race.

    This is the core table that connects:
    - A race (which race was it?)
    - A driver (who drove?)
    - A team (for which team?)
    - Performance data (how did they do?)
    """

    __tablename__ = "race_results"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys - these create the relationships
    race_id = Column(
        Integer,
        ForeignKey("races.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    driver_id = Column(
        Integer,
        ForeignKey("drivers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    team_id = Column(
        Integer,
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    # Race performance data
    position = Column(Integer, nullable=True)  # Finishing position (1, 2, 3, ..., or NULL if DNF)
    grid_position = Column(Integer, nullable=True)  # Starting position
    points = Column(Float, nullable=False, default=0.0)  # Championship points earned

    # Status: "Finished", "+1 Lap", "Accident", "Engine", "Gearbox", etc.
    status = Column(String, nullable=False, default="Finished")

    # Time/gap information
    # For winner: total race time (e.g., "1:32:15.123")
    # For others: gap to winner (e.g., "+5.234")
    time = Column(String, nullable=True)

    # Fastest lap
    fastest_lap = Column(Boolean, nullable=False, default=False)  # Did they get fastest lap bonus?
    fastest_lap_time = Column(String, nullable=True)  # Lap time as string (e.g., "1:32.234")
    fastest_lap_number = Column(Integer, nullable=True)  # Which lap was their fastest?

    # Headshot URL - override for mid-season team changes
    # If NULL, frontend should fall back to driver.default_headshot_url
    headshot_url = Column(String, nullable=True)

    # Relationships - these allow easy access to related data
    race = relationship("Race", back_populates="race_results")
    driver = relationship("Driver", back_populates="race_results")
    team = relationship("Team", back_populates="race_results")

    def __repr__(self):
        """String representation for debugging"""
        return f"<RaceResult P{self.position} - Driver:{self.driver_id} Race:{self.race_id}>"
