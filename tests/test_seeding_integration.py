"""
Integration tests for database seeding functionality.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from seed_database import create_sample_aircraft, create_sample_flights, seed_database
from app.models.aircraft import Aircraft
from app.models.flight import Flight


class TestSeedingIntegration:
    """Integration tests for database seeding with real database."""

    def test_create_sample_aircraft_integration(self, test_db):
        """Test creating and storing aircraft in the database."""
        aircraft = create_sample_aircraft()

        # Add to database
        for plane in aircraft:
            test_db.add(plane)
        test_db.commit()

        # Verify data was stored correctly
        stored_aircraft = test_db.query(Aircraft).all()
        assert len(stored_aircraft) == len(aircraft)

        # Verify data integrity
        for plane in stored_aircraft:
            assert plane.serial_number is not None
            assert plane.manufacturer is not None
            assert plane.created_at is not None

    def test_create_sample_flights_integration(self, test_db, sample_aircraft):
        """Test creating and storing flights in the database."""
        # Add aircraft first
        for plane in sample_aircraft:
            test_db.add(plane)
        test_db.commit()

        # Create flights
        flights = create_sample_flights(sample_aircraft)

        # Add flights to database
        for flight in flights:
            test_db.add(flight)
        test_db.commit()

        # Verify data was stored correctly
        stored_flights = test_db.query(Flight).all()
        assert len(stored_flights) == len(flights)

        # Verify data integrity and relationships
        for flight in stored_flights:
            assert flight.departure_airport is not None
            assert flight.arrival_airport is not None
            assert flight.departure_datetime is not None
            assert flight.arrival_datetime is not None
            assert flight.aircraft_serial_number is not None

            # Verify foreign key relationship
            aircraft = (
                test_db.query(Aircraft)
                .filter(Aircraft.serial_number == flight.aircraft_serial_number)
                .first()
            )
            assert aircraft is not None

    def test_full_seeding_integration(self, test_db):
        """Test the complete seeding process with real database."""
        # Mock the SessionLocal to use our test database
        from unittest.mock import patch

        with patch("seed_database.SessionLocal", return_value=test_db):
            # Run the seeding function
            seed_database()

        # Verify aircraft were created
        aircraft_count = test_db.query(Aircraft).count()
        assert aircraft_count > 0

        # Verify flights were created
        flight_count = test_db.query(Flight).count()
        assert flight_count > 0

        # Verify relationships
        flights = test_db.query(Flight).all()
        aircraft_serial_numbers = {
            plane.serial_number for plane in test_db.query(Aircraft).all()
        }

        for flight in flights:
            assert flight.aircraft_serial_number in aircraft_serial_numbers

    def test_seeding_data_quality(self, test_db):
        """Test the quality and realism of seeded data."""
        # Create and seed data
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        # Add to database
        for plane in aircraft:
            test_db.add(plane)
        for flight in flights:
            test_db.add(flight)
        test_db.commit()

        # Test aircraft data quality
        stored_aircraft = test_db.query(Aircraft).all()
        manufacturers = set(plane.manufacturer for plane in stored_aircraft)

        # Should have multiple manufacturers
        assert len(manufacturers) >= 2
        assert "Boeing" in manufacturers
        assert "Airbus" in manufacturers

        # Test flight data quality
        stored_flights = test_db.query(Flight).all()
        airports = set()
        for flight in stored_flights:
            airports.add(flight.departure_airport)
            airports.add(flight.arrival_airport)

        # Should use multiple airports
        assert len(airports) > 5

        # Should include major airports
        major_airports = {"JFK", "LAX", "ORD", "DFW", "ATL"}
        assert major_airports.intersection(airports)

    def test_seeding_with_existing_data(self, populated_test_db):
        """Test seeding behavior when data already exists."""
        # Verify we have existing data
        initial_aircraft_count = populated_test_db.query(Aircraft).count()
        initial_flight_count = populated_test_db.query(Flight).count()
        assert initial_aircraft_count > 0
        assert initial_flight_count > 0

        # Store initial data for comparison
        initial_aircraft_serials = {
            plane.serial_number for plane in populated_test_db.query(Aircraft).all()
        }

        # Mock the seeding function to simulate user confirmation
        from unittest.mock import patch

        with patch("builtins.input", return_value="y"):
            with patch("seed_database.SessionLocal", return_value=populated_test_db):
                # Run the seeding function
                seed_database()

        # Verify data was cleared and new data was added
        final_aircraft_count = populated_test_db.query(Aircraft).count()
        final_flight_count = populated_test_db.query(Flight).count()

        # Should have new data (not necessarily same count due to random generation)
        assert final_aircraft_count > 0
        assert final_flight_count > 0

        # Verify new aircraft serial numbers are different
        final_aircraft_serials = {
            plane.serial_number for plane in populated_test_db.query(Aircraft).all()
        }
        assert final_aircraft_serials != initial_aircraft_serials


class TestSeedingPerformance:
    """Performance tests for seeding functionality."""

    def test_seeding_performance(self, test_db):
        """Test that seeding completes in reasonable time."""
        import time

        start_time = time.time()

        # Create sample data
        aircraft = create_sample_aircraft()
        flights = create_sample_flights(aircraft)

        # Add to database
        for plane in aircraft:
            test_db.add(plane)
        for flight in flights:
            test_db.add(flight)
        test_db.commit()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete within 5 seconds (very generous)
        assert duration < 5.0

        # Verify we actually created data
        assert test_db.query(Aircraft).count() == len(aircraft)
        assert test_db.query(Flight).count() == len(flights)

    def test_large_dataset_seeding(self, test_db):
        """Test seeding with a larger dataset."""
        # Create more aircraft and flights
        aircraft_data = []
        for i in range(50):  # 50 aircraft
            aircraft_data.append(
                {
                    "serial_number": f"N{i:03d}AB",
                    "manufacturer": ["Boeing", "Airbus", "Bombardier"][i % 3],
                }
            )

        aircraft = [Aircraft(**data) for data in aircraft_data]
        flights = create_sample_flights(aircraft)

        # Add to database
        for plane in aircraft:
            test_db.add(plane)
        for flight in flights:
            test_db.add(flight)
        test_db.commit()

        # Verify performance and data integrity
        assert test_db.query(Aircraft).count() == 50
        assert test_db.query(Flight).count() == len(flights)

        # Verify all flights have valid aircraft references
        aircraft_serials = {plane.serial_number for plane in aircraft}
        flights_with_invalid_aircraft = (
            test_db.query(Flight)
            .filter(~Flight.aircraft_serial_number.in_(aircraft_serials))
            .count()
        )
        assert flights_with_invalid_aircraft == 0


class TestSeedingEdgeCases:
    """Test edge cases and error conditions in seeding."""

    def test_seeding_with_empty_aircraft_list(self, test_db):
        """Test seeding with an empty aircraft list."""
        empty_aircraft = []
        flights = create_sample_flights(empty_aircraft)

        # Should create no flights
        assert len(flights) == 0

        # Should handle gracefully
        for flight in flights:
            test_db.add(flight)
        test_db.commit()

        assert test_db.query(Flight).count() == 0

    def test_seeding_with_single_aircraft(self, test_db):
        """Test seeding with a single aircraft."""
        single_aircraft = [Aircraft(serial_number="N999ZZ", manufacturer="Boeing")]
        flights = create_sample_flights(single_aircraft)

        # Should create flights for the single aircraft
        assert len(flights) > 0

        # All flights should reference the single aircraft
        for flight in flights:
            assert flight.aircraft_serial_number == "N999ZZ"

    def test_seeding_data_consistency(self, test_db):
        """Test that seeded data is consistent across multiple runs."""
        # Run seeding multiple times and compare structure
        results = []

        for _ in range(3):
            aircraft = create_sample_aircraft()
            flights = create_sample_flights(aircraft)

            results.append(
                {
                    "aircraft_count": len(aircraft),
                    "flight_count": len(flights),
                    "manufacturers": set(plane.manufacturer for plane in aircraft),
                    "aircraft_serials": set(plane.serial_number for plane in aircraft),
                }
            )

        # Aircraft count should be consistent
        aircraft_counts = [r["aircraft_count"] for r in results]
        assert len(set(aircraft_counts)) == 1  # All should be the same

        # Manufacturer diversity should be consistent
        for result in results:
            assert (
                len(result["manufacturers"]) >= 2
            )  # Should have multiple manufacturers

        # Flight counts should be reasonable (not necessarily identical due to randomness)
        flight_counts = [r["flight_count"] for r in results]
        assert all(count > 0 for count in flight_counts)
