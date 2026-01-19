"""Test fixtures module."""

from .common_fixtures import (
    current_date,
    delete_database_data,
    enable_tracing,
    from_date,
    get_dashboard_page,
    setup_authentication,
)
from .domain_fixtures import domain_config
from .employee_fixtures import add_employees, employee_config

__all__ = [
    "get_dashboard_page",
    "setup_authentication",
    "domain_config",
    "enable_tracing",
    "employee_config",
    "add_employees",
    "from_date",
    "current_date",
    "delete_database_data",
]
