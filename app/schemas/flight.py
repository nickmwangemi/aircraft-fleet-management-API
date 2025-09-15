from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FlightBase(BaseModel):
    """Base schema for Flight, containing shared fields."""

    departure_airport: str
    arrival_airport: str
    departure_datetime: datetime
    arrival_datetime: datetime
    aircraft_serial_number: Optional[str] = None


class FlightCreate(FlightBase):
    """Schema for creating a new Flight."""

    pass


class Flight(FlightBase):
    """Schema for Flight, including timestamps."""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
