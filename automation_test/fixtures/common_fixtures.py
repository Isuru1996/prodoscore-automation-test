"""Common test fixtures for Playwright tests."""

import pytest

from automation_test.pages import LoginPage


@pytest.fixture(scope="class", autouse=True, name="dashboard_page")
def login_to_prodoscore(page):
    login_page = LoginPage(page)
    dashboard_page = login_page.login_via_microsoft()
    yield dashboard_page


@pytest.fixture(scope="function", autouse=True)
def enable_tracing(context):
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    context.tracing.stop(path="trace.zip")
