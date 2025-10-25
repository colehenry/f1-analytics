"""
Team (Constructor) Model

Represents a Formula 1 team/constructor.
Teams can change names over time (e.g., Racing Point → Aston Martin),
but we'll handle each as a separate entity for simplicity.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    """
    Represents a Formula 1 team/constructor.

    A team can have multiple drivers and participate in multiple races.
    """

    __tablename__ = "teams"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Team information
    name = Column(String, nullable=False, unique=True)  # "Red Bull Racing"
    team_color = Column(String(7), nullable=True)  # Hex color code: "#1E41FF"
    country = Column(String(3), nullable=True)  # Team nationality (AUT, ITA, GBR, etc.)

    # Relationships
    race_results = relationship("RaceResult", back_populates="team")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Team {self.name}>"
