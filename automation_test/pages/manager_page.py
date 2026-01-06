from automation_lib.core import BasePage

from automation_test.utils.date_utils import to_choose_date_string


class ManagerPage(BasePage):

    def __init__(self, page):
        super().__init__(page, page_name="ManagerPage")

    @property
    def date_range_dropdown(self):
        return self.page.get_by_role("combobox")

    @property
    def from_date_text(self):
        return self.page.get_by_text("From")

    @property
    def from_date_button(self):
        return self.page.locator(".react-datepicker__input-container button").nth(0)

    @property
    def to_date_text(self):
        return self.page.get_by_text("To", exact=True)

    @property
    def to_date_button(self):
        return self.page.locator(".react-datepicker__input-container button").nth(1)

    @property
    def departments_text(self):
        return self.page.get_by_text("Departments", exact=True)

    @property
    def department_dropdown(self):
        return self.page.get_by_text("All Departments", exact=True)

    @property
    def roles_text(self):
        return self.page.get_by_text("Roles", exact=True)

    @property
    def role_dropdown(self):
        return self.page.get_by_text("All Roles", exact=True)

    @property
    def managers_text(self):
        return self.page.locator("#main-section").get_by_text("Managers", exact=True)

    @property
    def manager_dropdown(self):
        return self.page.get_by_text("All Managers", exact=True)

    @property
    def employees_text(self):
        return self.page.locator("#main-section").get_by_text("Employees", exact=True)

    @property
    def employee_dropdown(self):
        return self.page.get_by_text("All Employees", exact=True)

    @property
    def apply_button(self):
        return self.page.get_by_role("button", name="Apply")

    @property
    def reset_button(self):
        return self.page.get_by_role("button", name="Reset")

    @property
    def team_prodoscore_heading(self):
        return self.page.get_by_role("heading", name="Team Prodoscore")

    @property
    def manager_name_columnheader(self):
        return self.page.get_by_role("columnheader", name="Manager name")

    @property
    def manager_name_sort_button_up(self):
        return self.manager_name_columnheader.locator(".svg-inline--fa.fa-caret-up")

    @property
    def manager_name_sort_button_down(self):
        return self.manager_name_columnheader.locator(".svg-inline--fa.fa-caret-down")

    @property
    def prodoscore_columnheader(self):
        return self.page.get_by_role("columnheader", name="Prodoscore", exact=True)

    @property
    def prodoscore_sort_button_up(self):
        return self.prodoscore_columnheader.locator(".svg-inline--fa.fa-caret-up")

    @property
    def prodoscore_sort_button_down(self):
        return self.prodoscore_columnheader.locator(".svg-inline--fa.fa-caret-down")

    @property
    def team_distribution_columnheader(self):
        return self.page.get_by_role("columnheader", name="Team Distribution")

    @property
    def team_distribution_sort_button_up(self):
        return self.team_distribution_columnheader.locator(
            ".svg-inline--fa.fa-caret-up"
        )

    @property
    def team_distribution_sort_button_down(self):
        return self.team_distribution_columnheader.locator(
            ".svg-inline--fa.fa-caret-down"
        )

    @property
    def direct_team_prodoscore_columnheader(self):
        return self.page.get_by_role("columnheader", name="Direct Team Prodoscore")

    @property
    def direct_team_prodoscore_sort_button_up(self):
        return self.direct_team_prodoscore_columnheader.locator(
            ".svg-inline--fa.fa-caret-up"
        )

    @property
    def direct_team_prodoscore_sort_button_down(self):
        return self.direct_team_prodoscore_columnheader.locator(
            ".svg-inline--fa.fa-caret-down"
        )

    @property
    def percent_change_columnheader(self):
        return self.page.get_by_role("columnheader", name="% change")

    @property
    def percent_change_sort_button_up(self):
        return self.percent_change_columnheader.locator(
            ".svg-inline--fa.fa-caret-up > path"
        )

    @property
    def percent_change_sort_button_down(self):
        return self.percent_change_columnheader.locator(".svg-inline--fa.fa-caret-down")

    @property
    def no_data_found_heading(self):
        return self.page.get_by_role("heading", name="No Data Found At This Time.")

    @property
    def no_data_for_selected_time(self):
        return self.page.get_by_role("heading", name="No data for selected time")

    @property
    def no_data_found_image(self):
        return self.page.get_by_role("img", name="No Data")

    @property
    def manager_table_first_row(self):
        return self.page.locator("table tbody tr").nth(1)

    @property
    def manager_page_next_button(self):
        return self.page.get_by_role("button", name="Next page")

    @property
    def manager_page_last_button(self):
        return self.page.get_by_role("button", name="Last page")

    @property
    def manager_page_previous_button(self):
        return self.page.get_by_role("button", name="Previous page")

    @property
    def manager_page_first_button(self):
        return self.page.get_by_role("button", name="First page")

    def get_button_by_number(self, page_number: int):
        return self.page.get_by_role("button", name=str(page_number), exact=True)

    def click_button_by_number(self, number):
        """Click on the pagination button by number."""
        self.get_button_by_number(number).click()

    def scroll_to_manager_table_bottom(self) -> None:
        """Scroll to the bottom of the manager table."""
        self.scroll_into_view_locator(
            self.manager_page_last_button, "Manager Page Last Button"
        )

    def click_next_page_button(self) -> None:
        """Click the next page button in the pagination."""
        self.click_locator(self.manager_page_next_button, "Manager Page Next Button")

    def click_previous_page_button(self) -> None:
        """Click the previous page button in the pagination."""
        self.click_locator(
            self.manager_page_previous_button, "Manager Page Previous Button"
        )

    def click_first_page_button(self) -> None:
        """Click the first page button in the pagination."""
        self.click_locator(self.manager_page_first_button, "Manager Page First Button")

    def click_last_page_button(self) -> None:
        """Click the last page button in the pagination."""
        self.click_locator(self.manager_page_last_button, "Manager Page Last Button")

    def change_date_range(self, date_range: str) -> None:
        """Change the date range from the dropdown."""
        self.date_range_dropdown.select_option(date_range)

    def change_from_date(self, from_date: str) -> None:
        """
        Change the 'From' date in the date picker.
        :param from_date: Date String
        """
        new_from_date_str: str = to_choose_date_string(from_date)
        self.from_date_button.click()
        self.page.get_by_role("option", name=new_from_date_str).click()

    def change_to_date(self, to_date: str) -> None:
        """
        Change the 'To' date in the date picker.
        :param to_date: Date String
        """
        new_to_date_str: str = to_choose_date_string(to_date)
        self.to_date_button.click()
        self.page.get_by_role("option", name=new_to_date_str).click()

    def get_from_date_value(self) -> str:
        """Get the current value of the 'From' date."""
        return self.get_text(self.from_date_button, "From Date Button")

    def get_to_date_value(self) -> str:
        """Get the current value of the 'To' date."""
        return self.get_text(self.to_date_button, "To Date Button")

    def wait_for_manager_table_load(self) -> None:
        """Wait for the manager table to load."""
        self.wait_for(
            self.manager_table_first_row,
            state="visible",
            timeout=10000,
            description="Manager Table First Row",
        )

    def wait_for_no_data_found(self) -> None:
        """Wait for the no data found message to appear."""
        self.wait_for(
            self.no_data_found_heading,
            state="visible",
            timeout=10000,
            description="No Data Found Heading",
        )

    def wait_for_no_data_for_selected_time(self) -> None:
        """Wait for the no data for selected time message to appear."""
        self.wait_for(
            self.no_data_for_selected_time,
            state="visible",
            timeout=10000,
            description="No Data For Selected Time Heading",
        )

    def get_number_of_rows_in_manager_table(self) -> int:
        """Get the number of rows in the manager table."""
        return self.page.locator("table tbody tr").count()

    def get_manager_name_by_row(self, row_index: int) -> str:
        """Get the manager name from a specific row in the manager table."""
        return (
            self.page.locator("tbody tr")
            .nth(row_index)
            .locator("td")
            .first.locator("p")
            .inner_text()
        )

    def _get_manager_row(self, manager_name: str):
        """Get the row locator for a specific manager by name."""
        return self.page.locator(
            f'tbody tr:has(td:first-child p:text-is("{manager_name}"))'
        )

    def get_manager_data(self, manager_name: str):
        """Get the manager data from the table for a specific manager."""
        row = self._get_manager_row(manager_name)
        tds = row.locator("td")
        prodoscore = tds.nth(1).locator("p").inner_text()
        team_distribution_div = tds.nth(2).locator("div.bg-primary-red")
        team_distribution = team_distribution_div.inner_text()
        team_distribution_color = team_distribution_div.evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
        direct_team_prodoscore = tds.nth(3).locator("p").inner_text()
        percent_change = tds.nth(4).locator("p").inner_text()
        return {
            "prodoscore": prodoscore,
            "team_distribution": team_distribution,
            "team_distribution_color": team_distribution_color,
            "direct_team_prodoscore": direct_team_prodoscore,
            "percent_change": percent_change,
        }

    def sort_manager_table_by_manager_name(self) -> None:
        """Sort the manager table by manager name."""
        self.click_locator(self.manager_name_columnheader, "Manager Name Column Header")

    def sort_manager_table_by_prodoscore(self) -> None:
        """Sort the manager table by prodoscore."""
        self.click_locator(self.prodoscore_columnheader, "Prodoscore Column Header")

    def sort_manager_table_by_team_distribution(self) -> None:
        """Sort the manager table by team distribution."""
        self.click_locator(
            self.team_distribution_columnheader, "Team Distribution Column Header"
        )

    def sort_manager_table_by_direct_team_prodoscore(self) -> None:
        """Sort the manager table by direct team prodoscore."""
        self.click_locator(
            self.direct_team_prodoscore_columnheader,
            "Direct Team Prodoscore Column Header",
        )

    def sort_manager_table_by_percent_change(self) -> None:
        """Sort the manager table by percent change."""
        self.click_locator(
            self.percent_change_columnheader, "Percent Change Column Header"
        )
