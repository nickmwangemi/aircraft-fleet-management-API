"""
Unit tests for the database seeding functionality.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, call

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from seed_database import create_sample_aircraft, create_sample_flights, seed_database
from app.models.aircraft import Aircraft
from app.models.flight import Flight


class TestCreateSampleAircraft:
    """Test cases for create_sample_aircraft function."""

    def test_creates_expected_number_of_aircraft(self):
        """Test that the function creates the expected number of aircraft."""
        aircraft = create_sample_aircraft()
        assert len(aircraft) == 10

    def test_aircraft_have_required_fields(self):
        """Test that all aircraft have the required fields."""
        aircraft = create_sample_aircraft()

        for plane in aircraft:
            assert isinstance(plane, Aircraft)
            assert plane.serial_number is not None
            assert plane.manufacturer is not None
            assert len(plane.serial_number) > 0
            assert len(plane.manufacturer) > 0

    def test_aircraft_serial_numbers_are_unique(self):
        """Test that all aircraft serial numbers are unique."""
        aircraft = create_sample_aircraft()
        serial_numbers = [plane.serial_number for plane in aircraft]
        assert len(serial_numbers) == len(set(serial_numbers))

    def test_aircraft_serial_numbers_format(self):
        """Test that serial numbers follow expected format."""
        aircraft = create_sample_aircraft()

        for plane in aircraft:
            # Should start with 'N' and contain letters/numbers
            assert plane.serial_number.startswith("N")
            assert len(plane.serial_number) == 6
            assert plane.serial_number[1:].isalnum()

    def test_aircraft_manufacturers_are_realistic(self):
        """Test that manufacturers are realistic aircraft manufacturers."""
        aircraft = create_sample_aircraft()
        manufacturers = set(plane.manufacturer for plane in aircraft)

        expected_manufacturers = {"Boeing", "Airbus", "Bombardier", "Embraer"}
        assert manufacturers.issubset(expected_manufacturers)

    def test_aircraft_manufacturers_diversity(self):
        """Test that we have a good mix of manufacturers."""
        aircraft = create_sample_aircraft()
        manufacturers = [plane.manufacturer for plane in aircraft]

        # Should have at least 2 different manufacturers
        assert len(set(manufacturers)) >= 2


class TestCreateSampleFlights:
    """Test cases for create_sample_flights function."""

    def test_creates_flights_for_all_aircraft(self):
        """Test that flights are created for all aircraft."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        # Each aircraft should have at least 3 flights
        aircraft_serial_numbers = set(plane.serial_number for plane in aircraft)
        flight_aircraft_serial_numbers = set(
            flight.aircraft_serial_number for flight in flights
        )

        assert aircraft_serial_numbers == flight_aircraft_serial_numbers

    def test_flights_have_required_fields(self):
        """Test that all flights have the required fields."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        for flight in flights:
            assert isinstance(flight, Flight)
            assert flight.departure_airport is not None
            assert flight.arrival_airport is not None
            assert flight.departure_datetime is not None
            assert flight.arrival_datetime is not None
            assert flight.aircraft_serial_number is not None

    def test_flights_have_realistic_airports(self):
        """Test that flights use realistic airport codes."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        expected_airports = {
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
        }

        for flight in flights:
            assert flight.departure_airport in expected_airports
            assert flight.arrival_airport in expected_airports

    def test_flights_departure_different_from_arrival(self):
        """Test that departure and arrival airports are different."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        for flight in flights:
            assert flight.departure_airport != flight.arrival_airport

    def test_flights_have_realistic_durations(self):
        """Test that flights have realistic durations."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        for flight in flights:
            duration = flight.arrival_datetime - flight.departure_datetime
            # Flights should be between 1 and 8 hours
            assert timedelta(hours=1) <= duration <= timedelta(hours=8)

    def test_flights_have_sequential_ids(self):
        """Test that flights have sequential IDs."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        flight_ids = [flight.id for flight in flights]
        assert flight_ids == list(range(1, len(flights) + 1))

    def test_flights_use_existing_aircraft_serial_numbers(self):
        """Test that flights reference existing aircraft serial numbers."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        aircraft_serial_numbers = set(plane.serial_number for plane in aircraft)

        for flight in flights:
            assert flight.aircraft_serial_number in aircraft_serial_numbers


class TestSeedDatabase:
    """Test cases for seed_database function."""

    @patch("seed_database.SessionLocal")
    @patch("seed_database.create_sample_aircraft")
    @patch("seed_database.create_sample_flights")
    @patch("seed_database.engine")
    def test_seed_database_success(
        self, mock_engine, mock_create_flights, mock_create_aircraft, mock_session_local
    ):
        """Test successful database seeding."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 0  # No existing data

        sample_aircraft = [Aircraft(serial_number="N123AB", manufacturer="Boeing")]
        sample_flights = [
            Flight(
                id=1,
                departure_airport="JFK",
                arrival_airport="LAX",
                departure_datetime=datetime.now(),
                arrival_datetime=datetime.now() + timedelta(hours=2),
                aircraft_serial_number="N123AB",
            )
        ]

        mock_create_aircraft.return_value = sample_aircraft
        mock_create_flights.return_value = sample_flights

        # Run the function
        seed_database()

        # Verify calls
        mock_create_aircraft.assert_called_once()
        mock_create_flights.assert_called_once_with(sample_aircraft)
        mock_db.add_all.assert_has_calls([call(sample_aircraft), call(sample_flights)])
        mock_db.commit.assert_called()
        mock_db.close.assert_called()

    @patch("seed_database.SessionLocal")
    def test_seed_database_with_existing_data_user_confirms(self, mock_session_local):
        """Test seeding when data already exists and user confirms."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5  # Existing data

        # Mock user input to confirm
        with patch("builtins.input", return_value="y"):
            with patch("seed_database.create_sample_aircraft") as mock_create_aircraft:
                with patch(
                    "seed_database.create_sample_flights"
                ) as mock_create_flights:
                    sample_aircraft = [
                        Aircraft(serial_number="N123AB", manufacturer="Boeing")
                    ]
                    sample_flights = []

                    mock_create_aircraft.return_value = sample_aircraft
                    mock_create_flights.return_value = sample_flights

                    seed_database()

        # Verify that existing data was cleared
        mock_db.query.return_value.delete.assert_called()
        mock_db.commit.assert_called()

    @patch("seed_database.SessionLocal")
    def test_seed_database_with_existing_data_user_cancels(self, mock_session_local):
        """Test seeding when data already exists and user cancels."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5  # Existing data

        # Mock user input to cancel
        with patch("builtins.input", return_value="n"):
            seed_database()

        # Verify that no data was added
        mock_db.add_all.assert_not_called()
        mock_db.close.assert_called()

    @patch("seed_database.SessionLocal")
    def test_seed_database_handles_exception(self, mock_session_local):
        """Test that seeding handles exceptions properly."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 0  # No existing data
        mock_db.add_all.side_effect = Exception("Database error")

        # Run the function and expect exception
        with pytest.raises(Exception, match="Database error"):
            seed_database()

        # Verify rollback was called
        mock_db.rollback.assert_called()
        mock_db.close.assert_called()


class TestIntegration:
    """Integration tests for the seeding functionality."""

    def test_create_sample_data_integration(self):
        """Test that the sample data creation functions work together."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        # Verify data integrity
        assert len(aircraft) > 0
        assert len(flights) > 0

        # Verify all flights reference valid aircraft
        aircraft_serial_numbers = set(plane.serial_number for plane in aircraft)
        for flight in flights:
            assert flight.aircraft_serial_number in aircraft_serial_numbers

        # Verify flight IDs are unique
        flight_ids = [flight.id for flight in flights]
        assert len(flight_ids) == len(set(flight_ids))

    def test_sample_data_realism(self):
        """Test that the generated data is realistic."""
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        # Check aircraft data realism
        manufacturers = set(plane.manufacturer for plane in aircraft)
        assert "Boeing" in manufacturers  # Should have Boeing aircraft
        assert "Airbus" in manufacturers  # Should have Airbus aircraft

        # Check flight data realism
        airports_used = set()
        for flight in flights:
            airports_used.add(flight.departure_airport)
            airports_used.add(flight.arrival_airport)

        # Should use multiple airports
        assert len(airports_used) > 5

        # Should include major airports
        major_airports = {"JFK", "LAX", "ORD", "DFW", "ATL"}
        assert major_airports.intersection(airports_used)
