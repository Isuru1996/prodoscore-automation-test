from automation_lib.core import BasePage

from .dashboard_page import DashboardPage


class LoginPage(BasePage):
    def __init__(self, page, base_url: str = "https://stg02.prv-prodoscore.com"):
        super().__init__(page, page_name="LoginPage")
        self.page_url = f"{base_url}/"

    @property
    def login_page_logo(self):
        return self.page.get_by_role("img", name="logo")

    @property
    def microsoft_sign_in_button(self):
        return self.page.get_by_role("button", name="microsoft Sign in with")

    @property
    def email_input(self):
        return self.page.get_by_role("textbox", name="Enter your email or phone")

    @property
    def next_button(self):
        return self.page.get_by_role("button", name="Next")

    @property
    def password_input(self):
        return self.page.get_by_role("textbox", name="Enter the password for")

    @property
    def sign_in_button(self):
        return self.page.get_by_role("button", name="Sign in")

    @property
    def yes_button(self):
        return self.page.get_by_role("button", name="Yes")

    def login_via_microsoft(self) -> DashboardPage:
        """Perform login via Microsoft authentication."""
        self.navigate_to(self.page_url)
        self.click_locator(self.microsoft_sign_in_button, "Microsoft Sign In Button")
        self.click_locator(self.email_input, "Email Input")
        self.fill_locator(
            self.email_input, "JimJames@Prodoscore904.onmicrosoft.com", "Email Input"
        )
        self.click_locator(self.next_button, "Next Button")
        self.click_locator(self.password_input, "Password Input")
        self.fill_locator(self.password_input, "Prod@123", "Password Input")
        self.click_locator(self.sign_in_button, "Sign In Button")
        self.click_locator(self.yes_button, "Yes Button")
        self.wait_for_url("**/dashboard")
        return DashboardPage(self.page, base_url=self.page_url)
