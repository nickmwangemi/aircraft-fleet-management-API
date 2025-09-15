"""
CLI commands for the Aircraft Fleet Management API.
"""

"""
This module provides command-line interface (CLI) commands for managing the Aircraft Fleet Management API.
It includes commands for initializing the database, seeding sample data, and other administrative tasks.
All functions and classes in this module are documented with docstrings for clarity and maintainability.
"""

import click
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import SessionLocal, engine
from app.models.aircraft import Aircraft
from app.models.flight import Flight
from app.models import aircraft as aircraft_module, flight as flight_module
from app.database import Base


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


@click.group()
def cli():
    """Aircraft Fleet Management API CLI."""
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Force reseed even if data exists")
def seed(force: bool):
    """Seed the database with sample data."""
    click.echo("🌱 Starting database seeding...")

    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    click.echo("✅ Database tables created/verified")

    # Create database session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_aircraft = db.query(Aircraft).count()
        if existing_aircraft > 0 and not force:
            click.echo(
                f"⚠️  Database already contains {existing_aircraft} aircraft records"
            )
            if not click.confirm("Do you want to clear existing data and reseed?"):
                click.echo("❌ Seeding cancelled")
                return

        if existing_aircraft > 0:
            # Clear existing data
            db.query(Flight).delete()
            db.query(Aircraft).delete()
            db.commit()
            click.echo("🗑️  Cleared existing data")

        # Create sample data
        click.echo("✈️  Creating sample aircraft...")
        aircraft = create_sample_aircraft()
        db.add_all(aircraft)
        db.commit()
        click.echo(f"✅ Created {len(aircraft)} aircraft records")

        click.echo("🛫 Creating sample flights...")
        flights = create_sample_flights(aircraft)
        db.add_all(flights)
        db.commit()
        click.echo(f"✅ Created {len(flights)} flight records")

        # Display summary
        click.echo("\n📊 Database Seeding Summary:")
        click.echo(f"   • Aircraft: {len(aircraft)}")
        click.echo(f"   • Flights: {len(flights)}")
        click.echo(f"   • Manufacturers: {len(set(a.manufacturer for a in aircraft))}")
        click.echo(f"   • Airports: {len(set(f.departure_airport for f in flights))}")

        click.echo("\n🎉 Database seeding completed successfully!")

    except Exception as e:
        click.echo(f"❌ Error during seeding: {e}", err=True)
        db.rollback()
        raise
    finally:
        db.close()


@cli.command()
def clear():
    """Clear all data from the database."""
    if not click.confirm("Are you sure you want to clear all data?"):
        click.echo("❌ Operation cancelled")
        return

    db = SessionLocal()
    try:
        db.query(Flight).delete()
        db.query(Aircraft).delete()
        db.commit()
        click.echo("🗑️  All data cleared successfully!")
    except Exception as e:
        click.echo(f"❌ Error clearing data: {e}", err=True)
        db.rollback()
        raise
    finally:
        db.close()


@cli.command()
def status():
    """Show database status and record counts."""
    db = SessionLocal()
    try:
        aircraft_count = db.query(Aircraft).count()
        flight_count = db.query(Flight).count()

        click.echo("📊 Database Status:")
        click.echo(f"   • Aircraft: {aircraft_count}")
        click.echo(f"   • Flights: {flight_count}")

        if aircraft_count > 0:
            manufacturers = db.query(Aircraft.manufacturer).distinct().all()
            click.echo(
                f"   • Manufacturers: {', '.join([m[0] for m in manufacturers])}"
            )

        if flight_count > 0:
            airports = db.query(Flight.departure_airport).distinct().all()
            click.echo(f"   • Airports: {len(airports)} unique")

    except Exception as e:
        click.echo(f"❌ Error checking status: {e}", err=True)
    finally:
        db.close()


if __name__ == "__main__":
    cli()
