"""
Unit tests for Flight model and related functionality.
"""

import pytest
from datetime import datetime, timedelta
from app.models.flight import Flight
from app.models.aircraft import Aircraft


class TestFlightModel:
    """Test cases for Flight model."""

    def test_flight_creation(self):
        """Test creating a flight instance."""
        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number="N123AB",
        )

        assert flight.id == 1
        assert flight.departure_airport == "JFK"
        assert flight.arrival_airport == "LAX"
        assert flight.departure_datetime == departure_time
        assert flight.arrival_datetime == arrival_time
        assert flight.aircraft_serial_number == "N123AB"

    def test_flight_table_name(self):
        """Test that the table name is correct."""
        assert Flight.__tablename__ == "flight"

    def test_flight_fields(self):
        """Test that all required fields are present."""
        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number="N123AB",
        )

        # Check that fields exist
        assert hasattr(flight, "id")
        assert hasattr(flight, "departure_airport")
        assert hasattr(flight, "arrival_airport")
        assert hasattr(flight, "departure_datetime")
        assert hasattr(flight, "arrival_datetime")
        assert hasattr(flight, "aircraft_serial_number")
        assert hasattr(flight, "created_at")
        assert hasattr(flight, "updated_at")

    def test_flight_id_primary_key(self):
        """Test that id is the primary key."""
        # The id column should be marked as primary_key
        id_column = Flight.__table__.columns["id"]
        assert id_column.primary_key is True

    def test_flight_created_at_timestamp(self, test_db, sample_aircraft):
        """Test that created_at is automatically set."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number=sample_aircraft[0].serial_number,
        )

        test_db.add(flight)
        test_db.commit()

        # Refresh to get the database-generated timestamp
        test_db.refresh(flight)

        assert flight.created_at is not None
        assert isinstance(flight.created_at, datetime)

    def test_flight_updated_at_timestamp(self, test_db, sample_aircraft):
        """Test that updated_at is set on updates."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number=sample_aircraft[0].serial_number,
        )

        test_db.add(flight)
        test_db.commit()

        # Update the flight
        flight.departure_airport = "ORD"
        test_db.commit()

        # Refresh to get the updated timestamp
        test_db.refresh(flight)

        assert flight.updated_at is not None
        assert isinstance(flight.updated_at, datetime)
        # For SQLite, timestamps might be the same due to precision limitations
        assert flight.updated_at >= flight.created_at

    def test_flight_can_be_retrieved(self, test_db, sample_aircraft):
        """Test that flights can be stored and retrieved."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number=sample_aircraft[0].serial_number,
        )

        test_db.add(flight)
        test_db.commit()

        # Retrieve the flight
        retrieved_flight = test_db.query(Flight).filter(Flight.id == 1).first()

        assert retrieved_flight is not None
        assert retrieved_flight.departure_airport == "JFK"
        assert retrieved_flight.arrival_airport == "LAX"
        assert (
            retrieved_flight.aircraft_serial_number == sample_aircraft[0].serial_number
        )

    def test_flight_aircraft_relationship(self, test_db, sample_aircraft):
        """Test the relationship between Flight and Aircraft."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number=sample_aircraft[0].serial_number,
        )

        test_db.add(flight)
        test_db.commit()

        # Test the relationship
        retrieved_flight = test_db.query(Flight).filter(Flight.id == 1).first()
        assert retrieved_flight.aircraft is not None
        assert (
            retrieved_flight.aircraft.serial_number == sample_aircraft[0].serial_number
        )

    def test_flight_string_representation(self):
        """Test flight string representation."""
        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number="N123AB",
        )

        # The string representation should contain key information
        flight_str = str(flight)
        assert "JFK" in flight_str
        assert "LAX" in flight_str
        assert "N123AB" in flight_str


class TestFlightDatabaseOperations:
    """Test database operations with Flight model."""

    def test_flight_query_by_airport(self, test_db, sample_flights):
        """Test querying flights by airport."""
        # Add sample flights to database
        for flight in sample_flights:
            test_db.add(flight)
        test_db.commit()

        # Query flights from JFK
        jfk_flights = (
            test_db.query(Flight).filter(Flight.departure_airport == "JFK").all()
        )

        assert len(jfk_flights) >= 1
        assert all(flight.departure_airport == "JFK" for flight in jfk_flights)

    def test_flight_query_by_aircraft(self, test_db, sample_aircraft, sample_flights):
        """Test querying flights by aircraft."""
        # Add aircraft and flights to database
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        for flight in sample_flights:
            test_db.add(flight)
        test_db.commit()

        # Query flights for a specific aircraft
        aircraft_serial = sample_aircraft[0].serial_number
        aircraft_flights = (
            test_db.query(Flight)
            .filter(Flight.aircraft_serial_number == aircraft_serial)
            .all()
        )

        assert len(aircraft_flights) >= 1
        assert all(
            flight.aircraft_serial_number == aircraft_serial
            for flight in aircraft_flights
        )

    def test_flight_query_by_date_range(self, test_db, sample_aircraft):
        """Test querying flights by date range."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        # Create flights with different dates
        now = datetime.now()
        flights = [
            Flight(
                id=1,
                departure_airport="JFK",
                arrival_airport="LAX",
                departure_datetime=now - timedelta(days=2),
                arrival_datetime=now - timedelta(days=2) + timedelta(hours=2),
                aircraft_serial_number=sample_aircraft[0].serial_number,
            ),
            Flight(
                id=2,
                departure_airport="LAX",
                arrival_airport="JFK",
                departure_datetime=now,
                arrival_datetime=now + timedelta(hours=2),
                aircraft_serial_number=sample_aircraft[0].serial_number,
            ),
            Flight(
                id=3,
                departure_airport="ORD",
                arrival_airport="DFW",
                departure_datetime=now + timedelta(days=2),
                arrival_datetime=now + timedelta(days=2) + timedelta(hours=2),
                aircraft_serial_number=sample_aircraft[0].serial_number,
            ),
        ]

        for flight in flights:
            test_db.add(flight)
        test_db.commit()

        # Query flights within a date range
        start_date = now - timedelta(days=1)
        end_date = now + timedelta(days=1)

        flights_in_range = (
            test_db.query(Flight)
            .filter(
                Flight.departure_datetime >= start_date,
                Flight.departure_datetime <= end_date,
            )
            .all()
        )

        assert len(flights_in_range) == 1
        assert flights_in_range[0].id == 2

    def test_flight_count_query(self, test_db, sample_flights):
        """Test counting flights."""
        # Add sample flights to database
        for flight in sample_flights:
            test_db.add(flight)
        test_db.commit()

        # Count all flights
        total_count = test_db.query(Flight).count()
        assert total_count == len(sample_flights)

        # Count by departure airport
        jfk_count = (
            test_db.query(Flight).filter(Flight.departure_airport == "JFK").count()
        )
        assert jfk_count >= 1

    def test_flight_delete(self, test_db, sample_flights):
        """Test deleting flights."""
        # Add sample flights to database
        for flight in sample_flights:
            test_db.add(flight)
        test_db.commit()

        initial_count = test_db.query(Flight).count()

        # Delete one flight
        flight_to_delete = test_db.query(Flight).first()
        test_db.delete(flight_to_delete)
        test_db.commit()

        final_count = test_db.query(Flight).count()
        assert final_count == initial_count - 1

    def test_flight_update(self, test_db, sample_flights):
        """Test updating flight information."""
        # Add sample flights to database
        for flight in sample_flights:
            test_db.add(flight)
        test_db.commit()

        # Update departure airport
        flight = test_db.query(Flight).first()
        original_airport = flight.departure_airport
        flight.departure_airport = "ORD"
        test_db.commit()

        # Verify update
        test_db.refresh(flight)
        assert flight.departure_airport == "ORD"
        assert flight.departure_airport != original_airport


class TestFlightValidation:
    """Test flight data validation and constraints."""

    def test_flight_departure_before_arrival(self, test_db, sample_aircraft):
        """Test that departure time is before arrival time."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)  # 2 hours later

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number=sample_aircraft[0].serial_number,
        )

        test_db.add(flight)
        test_db.commit()

        # Verify the times are correct
        retrieved_flight = test_db.query(Flight).filter(Flight.id == 1).first()
        assert retrieved_flight.departure_datetime < retrieved_flight.arrival_datetime

    def test_flight_different_airports(self, test_db, sample_aircraft):
        """Test that departure and arrival airports are different."""
        # Add aircraft first
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        departure_time = datetime.now()
        arrival_time = departure_time + timedelta(hours=2)

        flight = Flight(
            id=1,
            departure_airport="JFK",
            arrival_airport="LAX",  # Different airport
            departure_datetime=departure_time,
            arrival_datetime=arrival_time,
            aircraft_serial_number=sample_aircraft[0].serial_number,
        )

        test_db.add(flight)
        test_db.commit()

        # Verify airports are different
        retrieved_flight = test_db.query(Flight).filter(Flight.id == 1).first()
        assert retrieved_flight.departure_airport != retrieved_flight.arrival_airport
