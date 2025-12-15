"""Sample test cases to demonstrate automation library usage."""

import pytest
from automation_lib.core import BasePage, ElementNotFoundError


class TestGoogle:
    """Sample tests for Google search."""

    def test_google_homepage_title(self, page, logger, fake_employee):
        """Test navigating to Google and validating the page title."""
        # Create a base page instance
        google_page = BasePage(page)

        # Navigate to Google
        google_page.navigate_to("https://www.google.com")

        # Get the page title
        title = page.title()

        # Assert the title contains "Google"
        assert (
            "Google" in title
        ), f"Expected title to contain 'Google', but got: {title}"

    def test_google_search_box_exists(self, page, logger, fake_employee):
        """Test that Google search box element exists."""
        # Create a base page instance
        google_page = BasePage(page)

        # Navigate to Google
        google_page.navigate_to("https://www.google.com")

        # Wait for search box to be visible
        search_selector = "textarea[name='q'], input[name='q']"
        google_page.wait_for_element(search_selector, timeout=5000)

        # Verify search box is visible
        search_box = page.locator(search_selector)
        assert search_box.is_visible(), "Google search box should be visible"

    def test_google_search_functionality(self, page, logger, fake_employee):
        """Test performing a search on Google."""
        # Create a base page instance
        google_page = BasePage(page)

        # Navigate to Google
        google_page.navigate_to("https://www.google.com")

        # Fill search box
        search_selector = "textarea[name='q'], input[name='q']"
        google_page.fill(search_selector, "Playwright automation")

        # Press Enter to search
        page.keyboard.press("Enter")

        # Wait for results page to load
        page.wait_for_load_state("networkidle")

        # Verify we're on the search results page
        assert "search" in page.url.lower(), "Should be on search results page"
