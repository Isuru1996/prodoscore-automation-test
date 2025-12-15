"""Pytest configuration and fixtures for tests."""

# Import all fixtures from the fixtures module
from automation_test.fixtures.app_fixtures import fake_employee, test_domain
from automation_test.fixtures.common_fixtures import (
    browser,
    browser_manager,
    config,
    context,
    db_client,
    logger,
    page,
    test_settings,
)

__all__ = [
    "fake_employee",
    "test_domain",
    "logger",
    "config",
    "test_settings",
    "browser_manager",
    "browser",
    "context",
    "page",
    "db_client",
]
