#!/usr/bin/env python3
"""
Database seeding script for Aircraft Fleet Management API.

This script populates the database with sample aircraft and flight data
for development and testing purposes.

Usage:
    python seed_database.py
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.aircraft import Aircraft
from app.models.flight import Flight


def create_sample_aircraft() -> List[Aircraft]:
    """Create sample aircraft data."""
    aircraft_data = [
        {"serial_number": "N123AB", "manufacturer": "Boeing"},
        {"serial_number": "N456CD", "manufacturer": "Boeing"},
        {"serial_number": "N789EF", "manufacturer": "Airbus"},
        {"serial_number": "N321GH", "manufacturer": "Airbus"},
        {"serial_number": "N654IJ", "manufacturer": "Boeing"},
        {"serial_number": "N987KL", "manufacturer": "Bombardier"},
        {"serial_number": "N147MN", "manufacturer": "Embraer"},
        {"serial_number": "N258OP", "manufacturer": "Boeing"},
        {"serial_number": "N369QR", "manufacturer": "Airbus"},
        {"serial_number": "N741ST", "manufacturer": "Boeing"},
    ]

    aircraft = []
    for data in aircraft_data:
        aircraft.append(Aircraft(**data))

    return aircraft


def create_sample_flights(aircraft: List[Aircraft]) -> List[Flight]:
    """Create sample flight data."""
    airports = [
        "JFK",
        "LAX",
        "ORD",
        "DFW",
        "DEN",
        "ATL",
        "LAS",
        "SEA",
        "MIA",
        "BOS",
        "PHX",
        "IAH",
        "MCO",
        "CLT",
        "DTW",
        "MSP",
        "PHL",
        "SLC",
        "SAN",
        "TPA",
    ]

    flights = []
    flight_id = 1

    # Generate flights for each aircraft
    for aircraft_obj in aircraft:
        # Create 3-5 flights per aircraft
        num_flights = 3 + (flight_id % 3)  # 3-5 flights per aircraft

        for i in range(num_flights):
            departure_airport = airports[flight_id % len(airports)]
            arrival_airport = airports[(flight_id + 1) % len(airports)]

            # Ensure departure and arrival airports are different
            while arrival_airport == departure_airport:
                arrival_airport = airports[(flight_id + 2 + i) % len(airports)]

            # Generate realistic flight times
            departure_time = (
                datetime.now() - timedelta(days=flight_id * 2) + timedelta(hours=i * 4)
            )
            flight_duration = timedelta(hours=2 + (flight_id % 6))  # 2-7 hour flights
            arrival_time = departure_time + flight_duration

            flight = Flight(
                id=flight_id,
                departure_airport=departure_airport,
                arrival_airport=arrival_airport,
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                aircraft_serial_number=aircraft_obj.serial_number,
            )

            flights.append(flight)
            flight_id += 1

    return flights


def seed_database():
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")

    # Create database tables if they don't exist
    from app.models import aircraft, flight
    from app.database import Base

    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    # Create database session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_aircraft = db.query(Aircraft).count()
        if existing_aircraft > 0:
            print(f"⚠️  Database already contains {existing_aircraft} aircraft records")
            response = input("Do you want to clear existing data and reseed? (y/N): ")
            if response.lower() in ["y", "yes"]:
                # Clear existing data
                db.query(Flight).delete()
                db.query(Aircraft).delete()
                db.commit()
                print("🗑️  Cleared existing data")
            else:
                print("❌ Seeding cancelled")
                return

        # Create sample data
        print("✈️  Creating sample aircraft...")
        aircraft = create_sample_aircraft()
        db.add_all(aircraft)
        db.commit()
        print(f"✅ Created {len(aircraft)} aircraft records")

        print("🛫 Creating sample flights...")
        flights = create_sample_flights(aircraft)
        db.add_all(flights)
        db.commit()
        print(f"✅ Created {len(flights)} flight records")

        # Display summary
        print("\n📊 Database Seeding Summary:")
        print(f"   • Aircraft: {len(aircraft)}")
        print(f"   • Flights: {len(flights)}")
        print(f"   • Manufacturers: {len(set(a.manufacturer for a in aircraft))}")
        print(f"   • Airports: {len(set(f.departure_airport for f in flights))}")

        print("\n🎉 Database seeding completed successfully!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main entry point for the seeding script."""
    try:
        seed_database()
    except KeyboardInterrupt:
        print("\n❌ Seeding interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
