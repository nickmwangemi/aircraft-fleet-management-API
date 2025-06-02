from datetime import datetime

from pydantic import BaseModel


class AircraftBase(BaseModel):
    serial_number: str
    manufacturer: str


class AircraftCreate(BaseModel):
    pass


class Aircraft(AircraftBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
