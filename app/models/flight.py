from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Flight(Base):
	__tablename__ = 'flight'

	id = Column(Integer, primary_key=True, index=True)
	departure_airport = Column(String)
	arrival_airport = Column(String)
	departure_datetime = Column(DateTime(timezone=True))
	arrival_datetime = Column(DateTime(timezone=True))
	aircraft_serial_number = Column(String, ForeignKey('aircraft.serial_number'))
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), onupdate=func.now())

	aircraft = relationship('Aircraft', backref='flights')