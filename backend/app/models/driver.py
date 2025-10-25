"""
Driver Model

Represents a Formula 1 driver across their entire career.
Each driver has a unique ID and core information that doesn't change often.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Driver(Base):
    """
    Represents a Formula 1 driver.

    A driver can participate in multiple races (one-to-many relationship).
    """

    __tablename__ = "drivers"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Core driver information
    full_name = Column(String, nullable=False)
    abbreviation = Column(String(3), nullable=False, unique=True)  # VER, HAM, LEC, etc.
    driver_number = Column(Integer, nullable=True)  # Permanent number (e.g., 1, 44, 16)
    country_code = Column(String(3), nullable=True)  # NED, GBR, MON, etc.

    # Default headshot URL (most recent / current team)
    # This is the fallback if race_results.headshot_url is NULL
    default_headshot_url = Column(String, nullable=True)

    # Relationships
    # This creates a "virtual" attribute: driver.race_results
    # It allows you to do: driver.race_results to get all results for this driver
    race_results = relationship("RaceResult", back_populates="driver")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Driver {self.abbreviation} - {self.full_name}>"
