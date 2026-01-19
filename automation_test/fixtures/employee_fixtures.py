import pytest

from ..db.employee_utils import (
    add_test_employees,
    create_employees,
    delete_employees,
    update_employees_default,
)


@pytest.fixture(scope="function", autouse=True, name="employees")
def employee_config(db_client, config, test_employees, logger):
    """
    Sets up a domain with default values in the database for the given domain ID.
    Runs once per test function, before and after each test.
    Returns a dictionary mapping login_user, user_1, user_2, user_3, ... to Employee objects.
    """
    login_user_id = config.get("user.login_user.id")
    domain_id = config.get("domain.id")
    logger.info(f"Setting up employees")
    update_employees_default(db_client, domain_id, login_user_id)

    # Create employees and yield the mapping
    employees = create_employees(db_client, login_user_id, test_employees)

    yield employees

    logger.info(f"Tearing down employees")
    update_employees_default(db_client, domain_id, login_user_id)


@pytest.fixture(scope="session", autouse=True, name="test_employees")
def add_employees(db_client, config, logger):
    """
    Sets up a domain with default values in the database for the given domain ID.
    Runs once per test function, before and after each test.
    Returns a list of Employee objects for fake employees.
    """
    logger.info(f"Setting up test employees")
    inserted_ids = add_test_employees(db_client, config, 0, 1, 1, "Base", 6)

    yield inserted_ids

    logger.info(f"Tearing down test employees")
    delete_employees(db_client, inserted_ids)
