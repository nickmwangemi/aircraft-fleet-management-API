"""
Unit tests for Aircraft model and related functionality.
"""

import pytest
from datetime import datetime
from app.models.aircraft import Aircraft


class TestAircraftModel:
    """Test cases for Aircraft model."""

    def test_aircraft_creation(self):
        """Test creating an aircraft instance."""
        aircraft = Aircraft(serial_number="N123AB", manufacturer="Boeing")

        assert aircraft.serial_number == "N123AB"
        assert aircraft.manufacturer == "Boeing"

    def test_aircraft_table_name(self):
        """Test that the table name is correct."""
        assert Aircraft.__tablename__ == "aircraft"

    def test_aircraft_fields(self):
        """Test that all required fields are present."""
        aircraft = Aircraft(serial_number="N456CD", manufacturer="Airbus")

        # Check that fields exist
        assert hasattr(aircraft, "serial_number")
        assert hasattr(aircraft, "manufacturer")
        assert hasattr(aircraft, "created_at")
        assert hasattr(aircraft, "updated_at")

    def test_aircraft_serial_number_primary_key(self):
        """Test that serial_number is the primary key."""
        # The serial_number column should be marked as primary_key
        serial_number_column = Aircraft.__table__.columns["serial_number"]
        assert serial_number_column.primary_key is True

    def test_aircraft_created_at_timestamp(self, test_db):
        """Test that created_at is automatically set."""
        aircraft = Aircraft(serial_number="N789EF", manufacturer="Bombardier")

        test_db.add(aircraft)
        test_db.commit()

        # Refresh to get the database-generated timestamp
        test_db.refresh(aircraft)

        assert aircraft.created_at is not None
        assert isinstance(aircraft.created_at, datetime)

    def test_aircraft_updated_at_timestamp(self, test_db):
        """Test that updated_at is set on updates."""
        aircraft = Aircraft(serial_number="N321GH", manufacturer="Embraer")

        test_db.add(aircraft)
        test_db.commit()

        # Update the aircraft
        aircraft.manufacturer = "Boeing"
        test_db.commit()

        # Refresh to get the updated timestamp
        test_db.refresh(aircraft)

        assert aircraft.updated_at is not None
        assert isinstance(aircraft.updated_at, datetime)
        # For SQLite, timestamps might be the same due to precision limitations
        assert aircraft.updated_at >= aircraft.created_at

    def test_aircraft_can_be_retrieved(self, test_db):
        """Test that aircraft can be stored and retrieved."""
        aircraft = Aircraft(serial_number="N654IJ", manufacturer="Boeing")

        test_db.add(aircraft)
        test_db.commit()

        # Retrieve the aircraft
        retrieved_aircraft = (
            test_db.query(Aircraft).filter(Aircraft.serial_number == "N654IJ").first()
        )

        assert retrieved_aircraft is not None
        assert retrieved_aircraft.serial_number == "N654IJ"
        assert retrieved_aircraft.manufacturer == "Boeing"

    def test_multiple_aircraft_storage(self, test_db):
        """Test storing multiple aircraft."""
        aircraft_list = [
            Aircraft(serial_number="N111AA", manufacturer="Boeing"),
            Aircraft(serial_number="N222BB", manufacturer="Airbus"),
            Aircraft(serial_number="N333CC", manufacturer="Bombardier"),
        ]

        for aircraft in aircraft_list:
            test_db.add(aircraft)
        test_db.commit()

        # Retrieve all aircraft
        all_aircraft = test_db.query(Aircraft).all()

        assert len(all_aircraft) == 3

        serial_numbers = {aircraft.serial_number for aircraft in all_aircraft}
        expected_serials = {"N111AA", "N222BB", "N333CC"}
        assert serial_numbers == expected_serials

    def test_aircraft_serial_number_uniqueness(self, test_db):
        """Test that aircraft serial numbers must be unique."""
        aircraft1 = Aircraft(serial_number="N999ZZ", manufacturer="Boeing")
        aircraft2 = Aircraft(
            serial_number="N999ZZ",  # Same serial number
            manufacturer="Airbus",
        )

        test_db.add(aircraft1)
        test_db.commit()

        # Adding a second aircraft with the same serial number should fail
        test_db.add(aircraft2)

        with pytest.raises(Exception):  # Should raise integrity error
            test_db.commit()

    def test_aircraft_string_representation(self):
        """Test aircraft string representation."""
        aircraft = Aircraft(serial_number="N123AB", manufacturer="Boeing")

        # The string representation should contain key information
        aircraft_str = str(aircraft)
        assert "N123AB" in aircraft_str
        assert "Boeing" in aircraft_str


class TestAircraftDatabaseOperations:
    """Test database operations with Aircraft model."""

    def test_aircraft_query_by_manufacturer(self, test_db, sample_aircraft):
        """Test querying aircraft by manufacturer."""
        # Add sample aircraft to database
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        # Query Boeing aircraft
        boeing_aircraft = (
            test_db.query(Aircraft).filter(Aircraft.manufacturer == "Boeing").all()
        )

        assert len(boeing_aircraft) >= 1
        assert all(aircraft.manufacturer == "Boeing" for aircraft in boeing_aircraft)

    def test_aircraft_count_query(self, test_db, sample_aircraft):
        """Test counting aircraft."""
        # Add sample aircraft to database
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        # Count all aircraft
        total_count = test_db.query(Aircraft).count()
        assert total_count == len(sample_aircraft)

        # Count by manufacturer
        boeing_count = (
            test_db.query(Aircraft).filter(Aircraft.manufacturer == "Boeing").count()
        )
        assert boeing_count >= 1

    def test_aircraft_delete(self, test_db, sample_aircraft):
        """Test deleting aircraft."""
        # Add sample aircraft to database
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        initial_count = test_db.query(Aircraft).count()

        # Delete one aircraft
        aircraft_to_delete = test_db.query(Aircraft).first()
        test_db.delete(aircraft_to_delete)
        test_db.commit()

        final_count = test_db.query(Aircraft).count()
        assert final_count == initial_count - 1

    def test_aircraft_update(self, test_db, sample_aircraft):
        """Test updating aircraft information."""
        # Add sample aircraft to database
        for aircraft in sample_aircraft:
            test_db.add(aircraft)
        test_db.commit()

        # Update manufacturer
        aircraft = test_db.query(Aircraft).first()
        original_manufacturer = aircraft.manufacturer
        aircraft.manufacturer = "UpdatedManufacturer"
        test_db.commit()

        # Verify update
        test_db.refresh(aircraft)
        assert aircraft.manufacturer == "UpdatedManufacturer"
        assert aircraft.manufacturer != original_manufacturer
