from fastapi import FastAPI
from app.api.endpoints import aircraft, flights, reports
from app.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Aircraft Fleet Management API",
    description="API for managing a fleet of aircraft and their flights.",
    version="1.0.0",
)

app.include_router(aircraft.router, prefix="/api/v1/aircraft", tags=["aircraft"])
app.include_router(flights.router, prefix="/api/v1/flights", tags=["flights"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Aircraft Fleet Management API"}
