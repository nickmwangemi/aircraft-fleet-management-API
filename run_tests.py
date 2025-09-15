#!/usr/bin/env python3
"""
Test runner script for the Aircraft Fleet Management API.

This script provides an easy way to run all tests or specific test categories.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --seed             # Run only seeding tests
    python run_tests.py --models           # Run only model tests
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --coverage         # Run with coverage report
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n🧪 {description}")
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run tests for Aircraft Fleet Management API"
    )
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--seed", action="store_true", help="Run only seeding tests")
    parser.add_argument("--models", action="store_true", help="Run only model tests")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Run with verbose output"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage report"
    )
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")

    args = parser.parse_args()

    # Base pytest command
    pytest_cmd = ["python3", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")

    # Add coverage
    if args.coverage:
        pytest_cmd.extend(
            [
                "--cov=app",
                "--cov=seed_database",
                "--cov-report=html",
                "--cov-report=term",
            ]
        )

    # Determine which tests to run
    test_patterns = []

    if args.unit:
        test_patterns.extend(
            [
                "tests/test_aircraft.py::TestAircraftModel",
                "tests/test_flights.py::TestFlightModel",
                "tests/test_seed_database.py::TestCreateSampleAircraft",
                "tests/test_seed_database.py::TestCreateSampleFlights",
                "tests/test_cli.py::TestCLISampleDataFunctions",
            ]
        )
    elif args.integration:
        test_patterns.extend(
            [
                "tests/test_seeding_integration.py",
                "tests/test_aircraft.py::TestAircraftDatabaseOperations",
                "tests/test_flights.py::TestFlightDatabaseOperations",
            ]
        )
    elif args.seed:
        test_patterns.extend(
            [
                "tests/test_seed_database.py",
                "tests/test_seeding_integration.py",
                "tests/test_cli.py::TestCLICommands",
            ]
        )
    elif args.models:
        test_patterns.extend(
            [
                "tests/test_aircraft.py",
                "tests/test_flights.py",
            ]
        )
    else:
        # Run all tests
        test_patterns = ["tests/"]

    # Skip slow tests if requested
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])

    # Add test patterns
    pytest_cmd.extend(test_patterns)

    # Run the tests
    success = run_command(pytest_cmd, "Running Tests")

    # Print results
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
