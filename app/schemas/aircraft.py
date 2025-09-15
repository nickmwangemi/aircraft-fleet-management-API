from datetime import datetime
from pydantic import BaseModel


class AircraftBase(BaseModel):
    """Base schema for Aircraft, containing shared fields."""

    serial_number: str
    manufacturer: str


class AircraftCreate(AircraftBase):
    """Schema for creating a new Aircraft."""

    pass


class Aircraft(AircraftBase):
    """Schema for Aircraft, including timestamps."""

    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
