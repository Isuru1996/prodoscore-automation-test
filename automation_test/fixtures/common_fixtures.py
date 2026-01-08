"""Common test fixtures for Playwright tests."""

import pytest

from automation_test.db.employee_prodoscore_utils import delete_employee_prodoscore
from automation_test.db.organization_holidays_utils import delete_organization_holiday
from automation_test.db.organization_prodoscore_utils import (
    delete_organization_prodoscore,
)
from automation_test.pages import LoginPage


@pytest.fixture(scope="class", autouse=True, name="dashboard_page")
def login_to_prodoscore(page):
    login_page = LoginPage(page)
    dashboard_page = login_page.login_via_microsoft()
    dashboard_page.wait_for_all_loaders_to_disappear()
    yield dashboard_page


@pytest.fixture(scope="class", autouse=True, name="current_date")
def current_date(dashboard_page):
    yield dashboard_page.get_to_date_value()


@pytest.fixture(scope="class", autouse=True, name="from_date")
def from_date(dashboard_page):
    yield dashboard_page.get_from_date_value()


@pytest.fixture(scope="function", autouse=True)
def delete_database_data(from_date, current_date, domain, employees, db_client):
    filter_condition_1 = f"date >= '{from_date}' AND date <= '{current_date}' AND domain_id = '{domain.id}'"
    delete_employee_prodoscore(db_client, filter_condition_1)
    delete_organization_prodoscore(db_client, filter_condition_1)
    delete_organization_holiday(db_client, filter_condition_1)


@pytest.fixture(scope="function", autouse=True)
def enable_tracing(context):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    context.tracing.stop(path="trace.zip")
