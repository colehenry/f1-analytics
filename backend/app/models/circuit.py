"""
Circuit Model

Represents a Formula 1 racing circuit/track.
Circuits can host multiple races across different seasons.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.database import Base


class Circuit(Base):
    """
    Represents a Formula 1 circuit/track.

    A circuit can host multiple races (one-to-many relationship).
    """

    __tablename__ = "circuits"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Circuit information
    name = Column(String, nullable=False)  # "Bahrain International Circuit"
    location = Column(String, nullable=False)  # "Sakhir"
    country = Column(String, nullable=False)  # "Bahrain"

    # Optional: Geographic coordinates for mapping
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relationships
    races = relationship("Race", back_populates="circuit")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Circuit {self.name} - {self.location}, {self.country}>"
