from automation_lib.core import BasePage

from .manager_page import ManagerPage


class DashboardPage(BasePage):

    def __init__(self, page):
        super().__init__(page, page_name="DashboardPage")

    @property
    def chart_loading_bars(self):
        return self.page.get_by_test_id("loader")

    @property
    def from_date_button(self):
        return self.page.locator(".react-datepicker__input-container button").nth(0)

    @property
    def to_date_button(self):
        return self.page.locator(".react-datepicker__input-container button").nth(1)

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

    def get_from_date_value(self) -> str:
        return self.get_text(self.from_date_button, "From Date Button")

    def get_to_date_value(self) -> str:
        return self.get_text(self.to_date_button, "To Date Button")

    def wait_for_all_loaders_to_disappear(self):
        # Wait for all loader elements to be hidden (handles multiple loaders)
        loaders = self.chart_loading_bars
        count = loaders.count()
        for i in range(count):
            self.wait_for(
                loaders.nth(i), state="hidden", description=f"Chart Loading Bar {i+1}"
            )
