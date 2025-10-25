"""
Race Model

Represents a single Formula 1 race event.
A race belongs to a specific season, occurs at a circuit, and has multiple results.
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Race(Base):
    """
    Represents a Formula 1 race event.

    Each race:
    - Belongs to a season (year)
    - Has a round number (1-24 typically)
    - Takes place at a circuit
    - Has multiple race results (one per driver)
    """

    __tablename__ = "races"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Race identification
    season = Column(Integer, nullable=False, index=True)  # 2024, 2023, etc.
    round = Column(Integer, nullable=False)  # 1, 2, 3, ... 24

    # Race details
    name = Column(String, nullable=False)  # "Bahrain Grand Prix"
    date = Column(Date, nullable=False)  # Race date

    # Optional: Full event date (includes time)
    event_date = Column(DateTime, nullable=True)

    # Foreign key to circuits table
    circuit_id = Column(Integer, ForeignKey("circuits.id", ondelete="RESTRICT"), nullable=False)

    # Relationships
    circuit = relationship("Circuit", back_populates="races")
    race_results = relationship("RaceResult", back_populates="race")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Race {self.season} R{self.round} - {self.name}>"
