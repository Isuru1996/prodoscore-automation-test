"""Common test fixtures for Playwright tests."""

from pathlib import Path

import pytest

from automation_test.db.employee_holiday_utils import delete_employee_holiday
from automation_test.db.employee_prodoscore_utils import delete_employee_prodoscore
from automation_test.db.organization_holidays_utils import delete_organization_holiday
from automation_test.db.organization_prodoscore_utils import (
    delete_organization_prodoscore,
)
from automation_test.pages import DashboardPage, LoginPage
from automation_test.utils.date_utils import add_days_to_date


def _create_auth_state(auth_state_file, browser, logger, base_url):
    """Helper function to create authentication state."""
    logger.info("Creating authentication state...")
    # Create a temporary context for login
    context = browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    # Perform login
    login_page = LoginPage(page, base_url=base_url)
    dashboard_page = login_page.login_via_microsoft()
    dashboard_page.wait_for_all_loaders_to_disappear()

    # Save authentication state
    context.storage_state(path=auth_state_file)
    logger.info(f"Authentication state saved to {auth_state_file}")

    # Cleanup
    page.close()
    context.close()


def _validate_auth_state(auth_state_file, browser, logger, base_url):
    """Validate if the authentication state is still valid."""
    try:
        logger.info("Validating authentication state...")
        context = browser.new_context(
            storage_state=auth_state_file, viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # Try to navigate to dashboard
        page.goto(f"{base_url}/dashboard", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)

        # Check if we're redirected to login (invalid auth)
        current_url = page.url
        # Valid if URL contains /dashboard and NOT callbackUrl (login redirect)
        is_valid = "/dashboard" in current_url and "callbackUrl" not in current_url

        page.close()
        context.close()

        if is_valid:
            logger.info(f"Authentication state is valid (URL: {current_url})")
        else:
            logger.warning(
                f"Authentication state is invalid or expired (redirected to: {current_url})"
            )

        return is_valid
    except Exception as e:
        logger.warning(f"Auth validation failed: {e}")
        return False


@pytest.fixture(scope="session", autouse=True)
def setup_authentication(config, browser, logger, request):
    """Setup authentication once per test session."""
    auth_state_file = config.get("auth.auth_state_file")
    base_url = config.get("base_url")
    auth_state_path = Path(auth_state_file)

    # Check if auth state exists and is valid
    if auth_state_path.exists():
        logger.info(f"Authentication state file found at {auth_state_file}")

        if _validate_auth_state(auth_state_file, browser, logger, base_url):
            request.config._auth_state_file = auth_state_file
            return

        # Invalid auth state - delete and recreate
        logger.info("Deleting invalid authentication state...")
        auth_state_path.unlink()

    # Create new auth state
    _create_auth_state(auth_state_file, browser, logger, base_url)
    request.config._auth_state_file = auth_state_file


@pytest.fixture(scope="function", name="dashboard_page")
def get_dashboard_page(page, config):
    """Get dashboard page with pre-authenticated state."""
    # Navigate to dashboard (already authenticated via storage_state)
    base_url = config.get("base_url")
    dashboard_page = DashboardPage(page, base_url=base_url)
    dashboard_page.navigate_to(dashboard_page.page_url)
    dashboard_page.wait_for_all_loaders_to_disappear()
    yield dashboard_page


@pytest.fixture(scope="function", name="current_date")
def current_date(dashboard_page):
    yield dashboard_page.get_to_date_value()


@pytest.fixture(scope="function", name="from_date")
def from_date(dashboard_page):
    yield dashboard_page.get_from_date_value()


@pytest.fixture(scope="function", autouse=True)
def delete_database_data(
    request, logger, from_date, current_date, domain, employees, db_client
):
    # Skip if test is marked with @pytest.mark.skip_db_cleanup
    if request.node.get_closest_marker("skip_db_cleanup"):
        return

    logger.info("Deleting test data from database")
    filter_condition_1 = f"date >= '{add_days_to_date(from_date, -8)}' AND date <= '{current_date}' AND domain_id = '{domain.id}'"
    delete_employee_prodoscore(db_client, filter_condition_1)
    delete_organization_prodoscore(db_client, filter_condition_1)
    delete_organization_holiday(db_client, filter_condition_1)
    delete_employee_holiday(db_client, filter_condition_1)


@pytest.fixture(scope="function", autouse=True)
def enable_tracing(context):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    context.tracing.stop(path="trace.zip")
