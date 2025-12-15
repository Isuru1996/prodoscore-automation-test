"""Application-specific fixtures for Prodoscore tests."""

import pytest


@pytest.fixture(scope="session")
def test_domain(config, logger):
    """Setup test domain configuration."""
    logger.info("Setting up test domain...")
    domain = config.get("test_domain", "https://test.prodoscore.com")
    logger.info(f"Test domain: {domain}")
    return domain


@pytest.fixture(scope="function")
def fake_employee(db_client, test_domain, logger):
    """Create a fake employee for testing and cleanup after."""
    logger.info("Creating fake employee...")

    # Insert fake employee
    employee_data = {
        "name": "Test Employee",
        "email": f"test.employee.{id(object())}@example.com",
        "department": "Engineering",
    }

    # Example: Insert into database
    # db_client.execute_update(
    #     "INSERT INTO employees (name, email, department) VALUES (%s, %s, %s)",
    #     (employee_data["name"], employee_data["email"], employee_data["department"])
    # )

    logger.info(f"Fake employee created: {employee_data['email']}")

    yield employee_data

    # Cleanup
    logger.info(f"Cleaning up fake employee: {employee_data['email']}")
    # db_client.execute_update(
    #     "DELETE FROM employees WHERE email = %s",
    #     (employee_data["email"],)
    # )
