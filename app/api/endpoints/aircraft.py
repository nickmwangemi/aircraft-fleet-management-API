from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.api.crud import aircraft as crud_aircraft
from app.schemas.aircraft import Aircraft, AircraftCreate

router = APIRouter()


@router.post("/", response_model=Aircraft, status_code=status.HTTP_201_CREATED)
def create_aircraft(aircraft: AircraftCreate, db: Session = Depends(deps.get_db)):
    db_aircraft = crud_aircraft.get_aircraft(db, serial_number=aircraft.serial_number)
    if db_aircraft:
        raise HTTPException(
            status_code=400, detail="Aircraft with this serial number already exists"
        )
    return crud_aircraft.create_aircraft(db=db, aircraft=aircraft)


@router.get("/", response_model=List[Aircraft])
def read_aircrafts(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    aircrafts = crud_aircraft.get_aircrafts(db, skip=skip, limit=limit)
    return aircrafts


@router.get("/{serial_number}", response_model=Aircraft)
def read_aircraft(serial_number: str, db: Session = Depends(deps.get_db)):
    db_aircraft = crud_aircraft.get_aircraft(db, serial_number=serial_number)
    if db_aircraft is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return db_aircraft


@router.put("/{serial_number}", response_model=Aircraft)
def update_aircraft(
    serial_number: str, aircraft: AircraftCreate, db: Session = Depends(deps.get_db)
):
    db_aircraft = crud_aircraft.update_aircraft(
        db, serial_number=serial_number, aircraft=aircraft
    )
    if db_aircraft is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return db_aircraft


@router.delete("/{serial_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aircraft(serial_number: str, db: Session = Depends(deps.get_db)):
    db_aircraft = crud_aircraft.get_aircraft(db, serial_number=serial_number)
    if db_aircraft is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    crud_aircraft.delete_aircraft(db, serial_number=serial_number)
    return
