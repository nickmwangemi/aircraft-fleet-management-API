from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.database import Base


class Aircraft(Base):
    """SQLAlchemy model for the Aircraft table.

    Represents an aircraft in the fleet, identified by its serial number and manufacturer.
    Tracks creation and update timestamps.
    """

    __tablename__ = "aircraft"

    serial_number = Column(String, primary_key=True, index=True)
    manufacturer = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __str__(self):
        return f"Aircraft(serial_number='{self.serial_number}', manufacturer='{self.manufacturer}')"

    def __repr__(self):
        return self.__str__()
