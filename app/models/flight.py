from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Flight(Base):
    """SQLAlchemy model for the Flight table.

    Represents a flight, including its departure and arrival airports and times,
    and the associated aircraft by serial number. Tracks creation and update timestamps.
    """

    __tablename__ = "flight"

    id = Column(Integer, primary_key=True, index=True)
    departure_airport = Column(String)
    arrival_airport = Column(String)
    departure_datetime = Column(DateTime(timezone=True))
    arrival_datetime = Column(DateTime(timezone=True))
    aircraft_serial_number = Column(String, ForeignKey("aircraft.serial_number"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    aircraft = relationship("Aircraft", backref="flights")

    def __str__(self):
        return f"Flight(id={self.id}, {self.departure_airport}->{self.arrival_airport}, aircraft={self.aircraft_serial_number})"

    def __repr__(self):
        return self.__str__()
