from automation_lib.core import BasePage

from .manager_page import ManagerPage


class ManagerUnderPage(BasePage):
    def __init__(self, page):
        super().__init__(page, page_name="ManagerUnderPage")

    @property
    def employee_under_section(self):
        return self.page.locator("#employees-under")

    def go_to_manager_page(self):
        """Navigate back to the previous page."""
        self.page.go_back()
        self.wait_for_url("**/managers")
        return ManagerPage(self.page)
