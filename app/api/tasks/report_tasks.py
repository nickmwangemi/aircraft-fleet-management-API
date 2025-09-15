from sqlalchemy import func
from app.database import SessionLocal
from app.models import Flight
from celery_worker import celery_app


@celery_app.task
def generate_flight_report():
    """
    Connects to the database to generate a report on flight statistics.
    """
    db = SessionLocal()
    try:
        # 1. Calculate the total number of flights
        total_flights = db.query(Flight).count()

        # 2. Calculate total hours flown
        # This calculates the duration of each flight in seconds (epoch), sums them up, and converts to hours.
        duration_seconds = func.sum(
            func.extract("epoch", Flight.arrival_datetime)
            - func.extract("epoch", Flight.departure_datetime)
        )
        total_seconds = db.query(duration_seconds).scalar() or 0
        total_hours_flown = round(total_seconds / 3600, 2)

        # 3. Find the most frequent destination
        most_frequent = (
            db.query(
                Flight.arrival_airport,
                func.count(Flight.arrival_airport).label("count"),
            )
            .group_by(Flight.arrival_airport)
            .order_by(func.count(Flight.arrival_airport).desc())
            .first()
        )
        most_frequent_destination = most_frequent[0] if most_frequent else "N/A"

        report_data = {
            "total_flights": total_flights,
            "total_hours_flown": total_hours_flown,
            "most_frequent_destination": most_frequent_destination,
        }
        return report_data
    finally:
        # 4. Ensure the database session is always closed
        db.close()
