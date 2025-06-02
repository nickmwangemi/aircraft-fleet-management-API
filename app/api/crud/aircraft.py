from sqlalchemy.orm import Session

from app.models.aircraft import Aircraft
from app.schemas.aircraft import AircraftCreate


def get_aircraft(db: Session, serial_number: str):
    return db.query(Aircraft).filter(Aircraft.serial_number == serial_number).first()


def get_aircrafts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Aircraft).offset(skip).limit(limit).all()


def create_aircraft(db: Session, aircraft: AircraftCreate):
    db_aircraft = Aircraft.create(**aircraft.model_dump())
    db.add(db_aircraft)
    db.commit()
    db.refresh(db_aircraft)
    return db_aircraft


def update_aircraft(db: Session, serial_number: str, aircraft: AircraftCreate):
    db_aircraft = get_aircraft(db, serial_number)
    if db_aircraft:
        for key, value in aircraft.model_dump().items():
            setattr(db_aircraft, key, value)
        db.commit()
        db.refresh(db_aircraft)
    return db_aircraft
