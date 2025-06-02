from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FlightBase(BaseModel):
	departure_airport: str
	arrival_airport: str
	departure_datetime: datetime
	arrival_datetime: datetime
	aircraft_serial_number: Optional[str] = None


class FlightCreate(FlightBase):
	pass

class Flight(FlightBase):
	id: int
	created_at: datetime
	updated_at: datetime

	class Config:
		orm_mode = True