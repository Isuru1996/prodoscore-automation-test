"""Common test fixtures for Playwright tests."""

import logging
from pathlib import Path

import pytest
from automation_lib.core.config import Config
from automation_lib.core.logger import Logger
from automation_lib.db.mysql_client import MySQLClient
from automation_lib.playwright.browser_manager import BrowserManager
from playwright.sync_api import Browser, BrowserContext

from automation_test.config import TestSettings


@pytest.fixture(scope="session")
def logger(request):
    """Setup logger with pytest's log level."""
    # Try to get from command line option, else default to INFO
    log_level_str = request.config.getoption("--log-cli-level", None) or "INFO"
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    logger = Logger.setup_logger("test_automation", level=log_level)
    logger.info(f"Logger level: {log_level_str}")
    return logger


@pytest.fixture(scope="session")
def config(logger):
    """Load test configuration using automation_lib Config."""
    logger.info("Loading test configuration...")
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    if config_path.exists():
        logger.info(f"Config file found: {config_path}")
        return Config(str(config_path))
    logger.warning("Config file not found, using defaults")
    return Config()


@pytest.fixture(scope="session")
def test_settings(config, logger):
    """Load test settings using TestSettings."""
    logger.info("Initializing test settings...")
    return TestSettings()


@pytest.fixture(scope="session")
def browser_manager(test_settings, logger):
    """Create browser manager instance."""
    logger.info(
        f"Creating browser manager (browser: {test_settings.browser_type}, headless: {test_settings.headless})"
    )
    manager = BrowserManager(
        browser_type=test_settings.browser_type, headless=test_settings.headless
    )
    yield manager
    logger.info("Closing browser manager...")
    manager.close()


@pytest.fixture(scope="function")
def browser(browser_manager, logger):
    """Launch browser for each test."""
    logger.info("Launching browser...")
    browser = browser_manager.launch()
    yield browser
    logger.info("Closing browser...")
    browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser, logger):
    """Create browser context for each test."""
    logger.info("Creating browser context...")
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
    )
    yield context
    logger.info("Closing browser context...")
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, logger):
    """Create page for each test."""
    logger.info("Creating new page...")
    page = context.new_page()
    yield page
    logger.info("Closing page...")
    page.close()


@pytest.fixture(scope="session")
def db_client(test_settings, logger):
    """Create database client with connection pooling."""
    logger.info("Setting up database client...")
    db_config = test_settings.get_db_config()
    if not db_config:
        logger.warning("Database configuration not provided, skipping...")
        pytest.skip("Database configuration not provided")

    logger.info(
        f"Connecting to database: {db_config.get('database')} at {db_config.get('host')}"
    )
    # Create client and connect
    client = MySQLClient(
        host=db_config.get("host", "localhost"),
        database=db_config.get("database", ""),
        user=db_config.get("user", "root"),
        password=db_config.get("password", ""),
        port=db_config.get("port", 3306),
        pool_size=10,
    )
    client.connect()
    logger.info("Database connection pool created")
    yield client
    logger.info("Closing database connection pool...")
    client.disconnect()
    logger.info("Database connection pool closed")
