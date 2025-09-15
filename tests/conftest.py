"""
Test configuration and fixtures for the Aircraft Fleet Management API.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models.aircraft import Aircraft
from app.models.flight import Flight


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine using SQLite in memory."""
    # Use SQLite in-memory database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session and tables for each test."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()

    yield session

    # Clean up
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_aircraft():
    """Create sample aircraft data for testing."""
    return [
        Aircraft(serial_number="N123AB", manufacturer="Boeing"),
        Aircraft(serial_number="N456CD", manufacturer="Airbus"),
        Aircraft(serial_number="N789EF", manufacturer="Bombardier"),
    ]


@pytest.fixture
def sample_flights(sample_aircraft):
    """Create sample flight data for testing."""
    from datetime import datetime, timedelta

    flights = []
    flight_id = 1

    for aircraft in sample_aircraft:
        for i in range(2):  # 2 flights per aircraft
            departure_time = datetime.now() - timedelta(days=i)
            arrival_time = departure_time + timedelta(hours=2)

            flight = Flight(
                id=flight_id,
                departure_airport="JFK",
                arrival_airport="LAX",
                departure_datetime=departure_time,
                arrival_datetime=arrival_time,
                aircraft_serial_number=aircraft.serial_number,
            )
            flights.append(flight)
            flight_id += 1

    return flights


@pytest.fixture
def populated_test_db(test_db, sample_aircraft, sample_flights):
    """Create a test database with sample data."""
    # Add aircraft
    for aircraft in sample_aircraft:
        test_db.add(aircraft)

    # Add flights
    for flight in sample_flights:
        test_db.add(flight)

    test_db.commit()
    return test_db


@pytest.fixture
def mock_db_session(monkeypatch):
    """Mock database session for testing CLI commands."""
    import app.cli

    class MockSession:
        def __init__(self):
            self.aircraft = []
            self.flights = []
            self._committed = False

        def query(self, model):
            class MockQuery:
                def __init__(self, items):
                    self.items = items

                def count(self):
                    return len(self.items)

                def delete(self):
                    self.items.clear()
                    return self

                def distinct(self):
                    return self

                def all(self):
                    return self.items

            if model == Aircraft:
                return MockQuery(self.aircraft)
            elif model == Flight:
                return MockQuery(self.flights)
            return MockQuery([])

        def add_all(self, items):
            for item in items:
                if isinstance(item, Aircraft):
                    self.aircraft.append(item)
                elif isinstance(item, Flight):
                    self.flights.append(item)

        def add(self, item):
            if isinstance(item, Aircraft):
                self.aircraft.append(item)
            elif isinstance(item, Flight):
                self.flights.append(item)

        def commit(self):
            self._committed = True

        def rollback(self):
            pass

        def close(self):
            pass

    mock_session = MockSession()

    def mock_session_local():
        return mock_session

    monkeypatch.setattr(app.cli, "SessionLocal", mock_session_local)
    return mock_session
