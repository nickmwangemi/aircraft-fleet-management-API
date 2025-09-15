from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.api.crud import flight as crud_flight
from app.schemas.flight import Flight, FlightCreate

router = APIRouter()


@router.post("/", response_model=Flight, status_code=status.HTTP_201_CREATED)
def create_flight(flight: FlightCreate, db: Session = Depends(deps.get_db)):
    return crud_flight.create_flight(db=db, flight=flight)


@router.get("/", response_model=List[Flight])
def read_flights(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    flights = crud_flight.get_flights(db, skip=skip, limit=limit)
    return flights


@router.get("/search/", response_model=List[Flight])
def search_flights(
    departure_airport: str | None = None,
    arrival_airport: str | None = None,
    start_datetime: datetime | None = None,
    end_datetime: datetime | None = None,
    db: Session = Depends(deps.get_db),
):
    flights = crud_flight.search_flights(
        db, departure_airport, arrival_airport, start_datetime, end_datetime
    )
    return flights


@router.get("/{flight_id}", response_model=Flight)
def read_flight(flight_id: int, db: Session = Depends(deps.get_db)):
    db_flight = crud_flight.get_flight(db, flight_id=flight_id)
    if db_flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return db_flight
