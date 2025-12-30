from automation_lib.core import BasePage

from .manager_page import ManagerPage


class DashboardPage(BasePage):

    def __init__(self, page):
        super().__init__(page, page_name="DashboardPage")

    @property
    def toggle_button(self):
        return self.page.locator("#toggle-button")

    @property
    def manager_link(self):
        return self.page.get_by_role("link", name="/_next/static/media/managers.")

    def go_to_manager_page(self) -> ManagerPage:
        self.click_locator(self.toggle_button, "Toggle Button")
        self.click_locator(self.manager_link, "Manager Link")
        self.wait_for_url("**/managers")
        return ManagerPage(self.page)
