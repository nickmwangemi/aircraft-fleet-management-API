from datetime import datetime

from sqlalchemy.orm import Session

from app.models.flight import Flight
from app.schemas.aircraft import AircraftCreate
from app.schemas.flight import FlightCreate


def get_flight(db: Session, flight_id: int):
    return db.query(Flight).filter(Flight.id == flight_id).first()


def get_flights(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Flight).offset(skip).limit(limit).all()


def create_flight(db: Session, flight: FlightCreate):
    flight_data = flight.model_dump(exclude_unset=True, exclude={"id"})
    db_flight = Flight(**flight_data)
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight


def update_flight(db: Session, flight_id: int, flight: FlightCreate):
    db_flight = get_flight(db, flight_id)
    if db_flight:
        for key, value in flight.model_dump().items():
            setattr(db_flight, key, value)
        db.commit()
        db.refresh(db_flight)
    return db_flight


def delete_flight(db: Session, flight_id: int):
    db_flight = get_flight(db, flight_id)
    if db_flight:
        db.delete(db_flight)
        db.commit()
    return db_flight


def search_flights(
    db: Session,
    departure_airport: str = None,
    arrival_airport: str = None,
    start_datetime: datetime = None,
    end_datetime: datetime = None,
):
    query = db.query(Flight)
    if departure_airport:
        query = query.filter(Flight.departure_airport == departure_airport)
    if arrival_airport:
        query = query.filter(Flight.arrival_airport == arrival_airport)
    if start_datetime and end_datetime:
        query = query.filter(
            Flight.departure_datetime.between(start_datetime, end_datetime)
        )
    elif start_datetime:
        query = query.filter(Flight.departure_datetime >= start_datetime)
    elif end_datetime:
        query = query.filter(Flight.departure_datetime <= end_datetime)
    return query.all()
