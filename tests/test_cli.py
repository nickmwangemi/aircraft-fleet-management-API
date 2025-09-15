"""
Unit tests for the CLI commands.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock, call
from click.testing import CliRunner

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.cli import (
    cli,
    seed,
    clear,
    status,
    create_sample_aircraft,
    create_sample_flights,
)
from app.models.aircraft import Aircraft
from app.models.flight import Flight


class TestCLICommands:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Setup for each test method."""
        self.runner = CliRunner()

    @patch("app.cli.SessionLocal")
    @patch("app.cli.create_sample_aircraft")
    @patch("app.cli.create_sample_flights")
    @patch("app.cli.Base.metadata.create_all")
    def test_seed_command_success(
        self,
        mock_create_all,
        mock_create_flights,
        mock_create_aircraft,
        mock_session_local,
    ):
        """Test successful seed command."""
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
                departure_datetime=None,
                arrival_datetime=None,
                aircraft_serial_number="N123AB",
            )
        ]

        mock_create_aircraft.return_value = sample_aircraft
        mock_create_flights.return_value = sample_flights

        # Run the command
        result = self.runner.invoke(seed)

        # Verify
        assert result.exit_code == 0
        assert "Starting database seeding..." in result.output
        assert "Database tables created/verified" in result.output
        assert "Created 1 aircraft records" in result.output
        assert "Created 1 flight records" in result.output
        assert "Database seeding completed successfully!" in result.output

    @patch("app.cli.SessionLocal")
    @patch("app.cli.Base.metadata.create_all")
    def test_seed_command_with_existing_data_confirms(
        self, mock_create_all, mock_session_local
    ):
        """Test seed command with existing data and user confirmation."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5  # Existing data

        # Run the command with input
        result = self.runner.invoke(seed, input="y")

        # Verify
        assert result.exit_code == 0
        assert "Database already contains 5 aircraft records" in result.output
        assert "Cleared existing data" in result.output

    @patch("app.cli.SessionLocal")
    @patch("app.cli.Base.metadata.create_all")
    def test_seed_command_with_existing_data_cancels(
        self, mock_create_all, mock_session_local
    ):
        """Test seed command with existing data and user cancellation."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5  # Existing data

        # Run the command with input
        result = self.runner.invoke(seed, input="n")

        # Verify
        assert result.exit_code == 0
        assert "Database already contains 5 aircraft records" in result.output
        assert "Seeding cancelled" in result.output

    @patch("app.cli.SessionLocal")
    @patch("app.cli.create_sample_aircraft")
    @patch("app.cli.create_sample_flights")
    @patch("app.cli.Base.metadata.create_all")
    def test_seed_command_with_force_flag(
        self,
        mock_create_all,
        mock_create_flights,
        mock_create_aircraft,
        mock_session_local,
    ):
        """Test seed command with --force flag."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5  # Existing data

        sample_aircraft = [Aircraft(serial_number="N123AB", manufacturer="Boeing")]
        sample_flights = []

        mock_create_aircraft.return_value = sample_aircraft
        mock_create_flights.return_value = sample_flights

        # Run the command with --force flag
        result = self.runner.invoke(seed, ["--force"])

        # Verify
        assert result.exit_code == 0
        assert "Cleared existing data" in result.output
        assert "Database seeding completed successfully!" in result.output

    @patch("app.cli.SessionLocal")
    def test_clear_command_success(self, mock_session_local):
        """Test successful clear command."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Run the command with confirmation
        result = self.runner.invoke(clear, input="y")

        # Verify
        assert result.exit_code == 0
        assert "Are you sure you want to clear all data?" in result.output
        assert "All data cleared successfully!" in result.output
        mock_db.query.return_value.delete.assert_called()
        mock_db.commit.assert_called()

    @patch("app.cli.SessionLocal")
    def test_clear_command_cancels(self, mock_session_local):
        """Test clear command cancellation."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Run the command without confirmation
        result = self.runner.invoke(clear, input="n")

        # Verify
        assert result.exit_code == 0
        assert "Operation cancelled" in result.output
        mock_db.query.return_value.delete.assert_not_called()

    @patch("app.cli.SessionLocal")
    def test_status_command_with_data(self, mock_session_local):
        """Test status command with existing data."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        # Create separate mock queries for different calls
        mock_aircraft_query = MagicMock()
        mock_aircraft_query.count.return_value = 5

        mock_flight_query = MagicMock()
        mock_flight_query.count.return_value = 20

        mock_manufacturer_query = MagicMock()
        mock_manufacturer_query.distinct.return_value.all.return_value = [
            ("Boeing",),
            ("Airbus",),
        ]

        # Set up the query chain - need to handle the specific query calls
        call_count = [0]  # Use list to make it mutable in nested function

        def mock_query_side_effect(model):
            call_count[0] += 1

            # First call: Aircraft count
            if call_count[0] == 1:
                return mock_aircraft_query
            # Second call: Flight count
            elif call_count[0] == 2:
                return mock_flight_query
            # Third call: Aircraft.manufacturer
            elif call_count[0] == 3:
                return mock_manufacturer_query
            # Fourth call: Flight.departure_airport
            elif call_count[0] == 4:
                mock_airport_query = MagicMock()
                mock_airport_query.distinct.return_value.all.return_value = [
                    ("JFK",),
                    ("LAX",),
                ]
                return mock_airport_query
            else:
                return mock_aircraft_query

        mock_db.query.side_effect = mock_query_side_effect

        # Run the command
        result = self.runner.invoke(status)

        # Verify
        assert result.exit_code == 0
        assert "Aircraft: 5" in result.output
        assert "Flights: 20" in result.output
        assert "Boeing, Airbus" in result.output

    @patch("app.cli.SessionLocal")
    def test_status_command_empty_database(self, mock_session_local):
        """Test status command with empty database."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 0

        # Run the command
        result = self.runner.invoke(status)

        # Verify
        assert result.exit_code == 0
        assert "Aircraft: 0" in result.output
        assert "Flights: 0" in result.output

    @patch("app.cli.SessionLocal")
    def test_seed_command_handles_exception(self, mock_session_local):
        """Test seed command handles exceptions properly."""
        # Setup mocks to raise exception during seeding
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.count.return_value = 0  # No existing data
        mock_db.add_all.side_effect = Exception("Database connection error")

        # Run the command
        result = self.runner.invoke(seed)

        # Verify
        assert result.exit_code == 1
        assert "Error during seeding: Database connection error" in result.output


class TestCLISampleDataFunctions:
    """Test cases for CLI sample data creation functions."""

    def test_create_sample_aircraft_cli(self):
        """Test create_sample_aircraft function in CLI module."""
        aircraft = create_sample_aircraft()

        assert len(aircraft) == 10
        assert all(isinstance(plane, Aircraft) for plane in aircraft)
        assert all(plane.serial_number.startswith("N") for plane in aircraft)

    def test_create_sample_flights_cli(self):
        """Test create_sample_flights function in CLI module."""
        aircraft = [
            Aircraft(serial_number="N123AB", manufacturer="Boeing"),
            Aircraft(serial_number="N456CD", manufacturer="Airbus"),
        ]

        flights = create_sample_flights(aircraft)

        assert len(flights) > 0
        assert all(isinstance(flight, Flight) for flight in flights)

        # Verify all flights reference valid aircraft
        aircraft_serial_numbers = {plane.serial_number for plane in aircraft}
        for flight in flights:
            assert flight.aircraft_serial_number in aircraft_serial_numbers


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.runner = CliRunner()

    def test_cli_group_works(self):
        """Test that the CLI group is properly configured."""
        result = self.runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Aircraft Fleet Management API CLI" in result.output
        assert "seed" in result.output
        assert "clear" in result.output
        assert "status" in result.output

    def test_seed_command_help(self):
        """Test seed command help."""
        result = self.runner.invoke(seed, ["--help"])

        assert result.exit_code == 0
        assert "Seed the database with sample data" in result.output
        assert "--force" in result.output

    def test_clear_command_help(self):
        """Test clear command help."""
        result = self.runner.invoke(clear, ["--help"])

        assert result.exit_code == 0
        assert "Clear all data from the database" in result.output

    def test_status_command_help(self):
        """Test status command help."""
        result = self.runner.invoke(status, ["--help"])

        assert result.exit_code == 0
        assert "Show database status and record counts" in result.output


class TestCLIErrorHandling:
    """Test error handling in CLI commands."""

    def setup_method(self):
        """Setup for each test method."""
        self.runner = CliRunner()

    @patch("app.cli.SessionLocal")
    def test_clear_command_handles_exception(self, mock_session_local):
        """Test clear command handles exceptions."""
        # Setup mocks
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.delete.side_effect = Exception("Database error")

        # Run the command
        result = self.runner.invoke(clear, input="y")

        # Verify
        assert result.exit_code == 1
        assert "Error clearing data: Database error" in result.output
        mock_db.rollback.assert_called()

    @patch("app.cli.SessionLocal")
    def test_status_command_handles_exception(self, mock_session_local):
        """Test status command handles exceptions."""
        # Setup mocks to raise exception during query
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("Connection error")

        # Run the command
        result = self.runner.invoke(status)

        # Verify - CLI catches exceptions and continues with exit code 0
        assert result.exit_code == 0
        assert "Error checking status: Connection error" in result.output
