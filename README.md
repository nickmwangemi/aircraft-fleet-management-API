# Aircraft Fleet Management API

This is a FastAPI-based application for managing a fleet of aircraft and their associated flights.

## Features

-   **Aircraft Management**: CRUD operations for aircraft.
-   **Flight Management**: CRUD operations for flights.
-   **Flight Search**: Search for flights based on departure/arrival airports and time ranges.
-   **Async Reporting**: Generate reports as a background task using Celery.
-   **Dockerized**: Fully containerized for easy setup and deployment.

## Tech Stack

-   **Backend**: FastAPI, Python 3.11
-   **Database**: PostgreSQL
-   **Async Tasks**: Celery, Redis
-   **ORM**: SQLAlchemy
-   **Data Validation**: Pydantic
-   **Containerization**: Docker, Docker Compose

## Setup and Running the Project

### Prerequisites

-   Docker
-   Docker Compose

### Instructions

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:nickmwangemi/aircraft-fleet-management-API.git
    cd aircraft-fleet-management-API
    ```

2.  **Environment Variables:**
    Create a `.env` file by copying the example file. The default values are suitable for local development.
    ```bash
    cp .env.example .env
    ```

3.  **Build and Run with Docker Compose:**
    From the root of the project directory, run:
    ```bash
    docker-compose up --build
    ```
    This will build the Docker images and start all services: the FastAPI web server, PostgreSQL database, Redis message broker, and the Celery worker.

4.  **Seed the Database (Optional):**
    To populate the database with sample data for testing and development:
    ```bash
    # For Docker environment:
    docker-compose run --rm web python seed_database.py
    docker-compose run --rm web python -m app.cli seed
    
    # For local development (if running outside Docker):
    python seed_database.py
    python -m app.cli seed
    ```
    
    You can also use other CLI commands:
    ```bash
    # Check database status
    docker-compose run --rm web python -m app.cli status
    
    # Clear all data
    docker-compose run --rm web python -m app.cli clear
    
    # Force reseed (overwrites existing data)
    docker-compose run --rm web python -m app.cli seed --force
    ```

5.  **Access the API:**
    The API will be available at `http://localhost:8000`.
    Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.
    The Celery monitoring dashboard is available at `http://localhost:5555`.


## Database Seeding

The seed script populates the database with realistic sample data:

-   **10 Aircraft**: Mix of Boeing, Airbus, Bombardier, and Embraer aircraft with realistic serial numbers
-   **30-50 Flights**: 3-5 flights per aircraft with realistic routes between major US airports
-   **Realistic Data**: Flights include proper departure/arrival times, airports (JFK, LAX, ORD, etc.), and durations

This sample data is perfect for:
-   Testing API endpoints
-   Development and debugging
-   Demonstrating the system capabilities
-   Performance testing

## Testing

The project includes a comprehensive test suite with **77 tests** covering all functionality including unit tests, integration tests, and CLI command testing.

### Test Suite Overview

- **77 Total Tests** ✅
- **Unit Tests**: 34 tests - Individual function and method testing
- **Integration Tests**: 10 tests - Real database operations and seeding
- **CLI Tests**: 15 tests - Command-line interface functionality
- **Model Tests**: 18 tests - Database models and relationships

### Running Tests

#### Basic Test Commands

```bash
# Run all tests (recommended to run in Docker)
python3 run_tests.py

# Run specific test categories
python3 run_tests.py --unit          # Unit tests only
python3 run_tests.py --integration   # Integration tests only
python3 run_tests.py --seed          # Seeding functionality tests
python3 run_tests.py --models        # Database model tests

# Run with coverage report
python3 run_tests.py --coverage

# Run with verbose output
python3 run_tests.py --verbose

# Skip slow tests
python3 run_tests.py --fast
```

#### Direct Pytest Commands

```bash
# Run all tests with pytest directly
python3 -m pytest tests/

# Run specific test files
python3 -m pytest tests/test_aircraft.py
python3 -m pytest tests/test_flights.py
python3 -m pytest tests/test_seed_database.py
python3 -m pytest tests/test_cli.py
python3 -m pytest tests/test_seeding_integration.py

# Run specific test classes
python3 -m pytest tests/test_aircraft.py::TestAircraftModel
python3 -m pytest tests/test_cli.py::TestCLICommands

# Run with coverage
python3 -m pytest tests/ --cov=app --cov=seed_database --cov-report=html

# Run with verbose output
python3 -m pytest tests/ -v

# Run specific test by name
python3 -m pytest tests/test_seed_database.py::TestCreateSampleAircraft::test_creates_expected_number_of_aircraft -v
```

### Docker Testing (Recommended)

```bash
# Run all tests in Docker environment
docker-compose run --rm web python3 run_tests.py

# Run specific test categories in Docker
docker-compose run --rm web python3 run_tests.py --unit
docker-compose run --rm web python3 run_tests.py --integration
docker-compose run --rm web python3 run_tests.py --seed

# Run with coverage in Docker
docker-compose run --rm web python3 run_tests.py --coverage

# Run specific pytest commands in Docker
docker-compose run --rm web python3 -m pytest tests/test_seed_database.py -v
```

### Test Categories Details

#### Unit Tests (34 tests)
- **Aircraft Model Tests** (14 tests)
  - Model creation and validation
  - Database operations (CRUD)
  - Timestamp handling
  - String representation
  - Primary key constraints
  - Manufacturer queries

- **Flight Model Tests** (9 tests)
  - Model creation and validation
  - Database operations (CRUD)
  - Relationship testing with aircraft
  - Airport queries and date ranges
  - Timestamp handling

- **Seeding Function Tests** (13 tests)
  - `create_sample_aircraft()` function
  - `create_sample_flights()` function
  - Data quality validation
  - Realistic data generation
  - Integration between functions

- **CLI Sample Data Tests** (2 tests)
  - CLI module sample data functions
  - Data consistency validation

#### Integration Tests (10 tests)
- **Database Seeding Integration**
  - Full seeding process with real SQLite database
  - Data integrity and relationship validation
  - Performance testing with large datasets
  - Edge cases (empty data, single records)

- **Data Quality Tests**
  - Manufacturer diversity validation
  - Airport usage validation
  - Flight duration realism
  - Data consistency across multiple runs

#### CLI Tests (15 tests)
- **Seed Command Tests** (5 tests)
  - Successful seeding with new data
  - Seeding with existing data (user confirmation)
  - Force reseed with `--force` flag
  - User cancellation scenarios
  - Exception handling

- **Status Command Tests** (3 tests)
  - Database status with existing data
  - Empty database status
  - Exception handling

- **Clear Command Tests** (2 tests)
  - Successful data clearing with confirmation
  - User cancellation

- **Integration Tests** (5 tests)
  - CLI group functionality
  - Help command testing
  - Error handling across commands

#### Model Tests (18 tests)
- **Aircraft Database Operations** (9 tests)
  - Query by manufacturer
  - Count operations
  - Delete operations
  - Update operations
  - Uniqueness constraints

- **Flight Database Operations** (9 tests)
  - Query by airport
  - Query by aircraft
  - Date range queries
  - Count operations
  - Delete and update operations
  - Data validation (departure before arrival)

### Test Configuration

#### Test Database
- Uses **SQLite in-memory database** for fast, isolated testing
- Each test gets a fresh database instance
- No external dependencies required for testing

#### Test Fixtures
- **Sample Aircraft Data**: Pre-configured aircraft for testing
- **Sample Flight Data**: Pre-configured flights with realistic data
- **Mock Database Sessions**: For CLI command testing
- **Populated Test Database**: Database with sample data for integration tests

#### Coverage Reporting
```bash
# Generate HTML coverage report
python3 run_tests.py --coverage

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Results Example

```
🧪 Running Tests
Running: python3 -m pytest tests/
=========================================== test session starts ============================================
platform linux -- Python 3.11.13, pytest-8.4.0, pluggy-1.6.0
collected 77 items

tests/test_aircraft.py ..............                                                                [ 18%]
tests/test_cli.py .................                                                                  [ 40%]
tests/test_flights.py .................                                                              [ 62%]
tests/test_seed_database.py ...................                                                      [ 87%]
tests/test_seeding_integration.py ..........                                                         [100%]

====================================== 77 passed, 1 warning in 0.35s =======================================
🎉 All tests passed!
```

### Continuous Integration

The test suite is designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    docker-compose run --rm web python3 run_tests.py --coverage
    
- name: Run Specific Test Categories
  run: |
    docker-compose run --rm web python3 run_tests.py --unit
    docker-compose run --rm web python3 run_tests.py --integration
```

## API Endpoints

-   `GET /`: Welcome message.
-   `POST /api/v1/aircraft/`: Create a new aircraft.
-   `GET /api/v1/aircraft/`: Get a list of all aircraft.
-   `GET /api/v1/flights/`: Get a list of all flights.
-   `GET /api/v1/flights/search/`: Search for flights.
-   `POST /api/v1/reports/generate`: Trigger an async report generation task.
-   `GET /api/v1/reports/status/{task_id}`: Check the status of a report generation task.