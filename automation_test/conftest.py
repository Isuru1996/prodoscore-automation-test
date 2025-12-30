"""Pytest configuration and fixtures for tests."""

# Import all fixtures from the fixtures module
from automation_lib.fixtures import (
    browser,
    browser_manager,
    config,
    context,
    db_client,
    logger,
    page,
    test_settings,
)

from automation_test.fixtures import (
    add_employees,
    domain_config,
    employee_config,
    enable_tracing,
    login_to_prodoscore,
)
from automation_test.plugins import slack_reporter

__all__ = [
    "logger",
    "config",
    "test_settings",
    "browser_manager",
    "browser",
    "context",
    "page",
    "db_client",
    "domain_config",
    "employee_config",
    "login_to_prodoscore",
    "enable_tracing",
    "add_employees",
]
