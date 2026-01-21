from datetime import datetime

from automation_lib.core import BasePage

from automation_test.utils.css_utils import class_to_color_name
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
    def next_month_button(self):
        return self.page.get_by_role("button", name="Next Month")

    @property
    def previous_month_button(self):
        return self.page.get_by_role("button", name="Previous Month")

    @property
    def notification_row(self):
        return self.page.get_by_test_id("message-row")

    @property
    def departments_text(self):
        return self.page.get_by_text("Departments", exact=True)

    @property
    def department_dropdown(self):
        return self.page.get_by_text("All Departments", exact=True)

    @property
    def department_dropdown_options(self):
        """Locate department dropdown options."""
        return (
            self.page.locator('label:has-text("Departments")')
            .locator("..")
            .locator("button")
        )

    @property
    def department_dropdown_placeholder(self):
        """Locate department dropdown button placeholder text."""
        return self.department_dropdown_options.locator("span.truncate")

    def get_department_dropdown_placeholder_text(self) -> str:
        """Get the text of the department dropdown placeholder."""
        return self.get_text(
            self.department_dropdown_placeholder, "Department Dropdown Placeholder"
        )

    @property
    def department_dropdown_arrow(self):
        """Locate department dropdown arrow icon (SVG)."""
        return self.department_dropdown_options.locator('svg[data-icon="angle-down"]')

    @property
    def department_dropdown_menu(self):
        """Locate department dropdown menu container."""
        return (
            self.page.locator('label:has-text("Departments")')
            .locator("..")
            .locator("div.absolute.z-20")
        )

    @property
    def department_search_input(self):
        """Locate department dropdown search input."""
        return self.department_dropdown_menu.locator(
            '> div > input[placeholder="Search"]'
        )

    def search_department(self, search_text: str) -> None:
        """Type text into department search input."""
        self.type_characters_sequentially(
            self.department_search_input,
            search_text,
            delay=500,
            description="Department Search Input",
        )

    def clear_department_search(self) -> None:
        """Clear all characters from department search input."""
        self.fill_locator(self.department_search_input, "", "Department Search Input")

    @property
    def department_search_loading_spinner(self):
        """Locate department search loading spinner."""
        return self.department_dropdown_menu.locator("div.loader__spinner")

    def wait_for_department_search_complete(self) -> None:
        """Wait for department search loading spinner to disappear."""
        self.wait_for(
            self.department_search_loading_spinner,
            state="hidden",
            timeout=10000,
            description="Department Search Loading Spinner",
        )

    @property
    def department_select_all_option(self):
        """Locate department 'Select All' checkbox option."""
        return self.department_dropdown_menu.locator("ul > li").first

    @property
    def department_results_list(self):
        """Locate department dropdown results list container."""
        return self.department_dropdown_menu.locator("div.max-h-32.overflow-y-auto")

    def get_department_result_names(self) -> list[str]:
        """Get all department names from results list."""
        items = self.department_results_list.locator("li span[title]")
        return [
            self.get_attribute(
                items.nth(i), "title", description="Department Result Name"
            )
            for i in range(items.count())
        ]

    def select_department_by_name(self, department_name: str) -> None:
        """Select a department by name from the results list."""
        label_locator = self.department_results_list.locator(
            f'label:has(span[title="{department_name}"])'
        )
        self.click_locator(label_locator, f"Department: {department_name}")

    def click_department_select_all(self) -> None:
        """Click the 'Select All' checkbox for departments."""
        self.click_locator(
            self.department_select_all_option,
            "Department Select All Checkbox",
        )

    @property
    def roles_text(self):
        return self.page.get_by_text("Roles", exact=True)

    @property
    def role_dropdown(self):
        return self.page.get_by_text("All Roles", exact=True)

    @property
    def role_dropdown_options(self):
        """Locate role dropdown options."""
        return (
            self.page.locator('label:has-text("Roles")').locator("..").locator("button")
        )

    @property
    def role_dropdown_placeholder(self):
        """Locate role dropdown button placeholder text."""
        return self.role_dropdown_options.locator("span.truncate")

    def get_role_dropdown_placeholder_text(self) -> str:
        """Get the text of the role dropdown placeholder."""
        return self.get_text(
            self.role_dropdown_placeholder, "Role Dropdown Placeholder"
        )

    @property
    def role_dropdown_arrow(self):
        """Locate role dropdown arrow icon (SVG)."""
        return self.role_dropdown_options.locator('svg[data-icon="angle-down"]')

    @property
    def role_dropdown_menu(self):
        """Locate role dropdown menu container."""
        return (
            self.page.locator('label:has-text("Roles")')
            .locator("..")
            .locator("div.absolute.z-20")
        )

    @property
    def role_search_input(self):
        """Locate role dropdown search input."""
        return self.role_dropdown_menu.locator('> div > input[placeholder="Search"]')

    def search_role(self, search_text: str) -> None:
        """Type text into role search input."""
        self.type_characters_sequentially(
            self.role_search_input,
            search_text,
            delay=500,
            description="Role Search Input",
        )

    def clear_role_search(self) -> None:
        """Clear all characters from role search input."""
        self.fill_locator(self.role_search_input, "", "Role Search Input")

    @property
    def role_search_loading_spinner(self):
        """Locate role search loading spinner."""
        return self.role_dropdown_menu.locator("div.loader__spinner")

    def wait_for_role_search_complete(self) -> None:
        """Wait for role search loading spinner to disappear."""
        self.wait_for(
            self.role_search_loading_spinner,
            state="hidden",
            timeout=10000,
            description="Role Search Loading Spinner",
        )

    @property
    def role_select_all_option(self):
        """Locate role 'Select All' checkbox option."""
        return self.role_dropdown_menu.locator("ul > li").first

    @property
    def role_results_list(self):
        """Locate role dropdown results list container."""
        return self.role_dropdown_menu.locator("div.max-h-32.overflow-y-auto")

    def get_role_result_names(self) -> list[str]:
        """Get all role names from results list."""
        items = self.role_results_list.locator("li span[title]")
        return [self.get_attribute(items.nth(i), "title") for i in range(items.count())]

    def select_role_by_name(self, role_name: str) -> None:
        """Select a role by name from the results list."""
        label_locator = self.role_results_list.locator(
            f'label:has(span[title="{role_name}"])'
        )
        self.click_locator(label_locator, f"Role: {role_name}")

    def click_role_select_all(self) -> None:
        """Click the 'Select All' checkbox for roles."""
        self.click_locator(
            self.role_select_all_option,
            "Role Select All Checkbox",
        )

    @property
    def managers_text(self):
        return self.page.locator("#main-section").get_by_text("Managers", exact=True)

    @property
    def manager_dropdown(self):
        return self.page.get_by_text("All Managers", exact=True)

    @property
    def manager_dropdown_options(self):
        """Locate manager dropdown options."""
        return (
            self.page.locator('label:has-text("Managers")')
            .locator("..")
            .locator("button")
        )

    @property
    def manager_dropdown_placeholder(self):
        """Locate manager dropdown button placeholder text."""
        return self.manager_dropdown_options.locator("span.truncate")

    def get_manager_dropdown_placeholder_text(self) -> str:
        """Get the text of the manager dropdown placeholder."""
        return self.get_text(
            self.manager_dropdown_placeholder, "Manager Dropdown Placeholder"
        )

    @property
    def manager_dropdown_arrow(self):
        """Locate manager dropdown arrow icon (SVG)."""
        return self.manager_dropdown_options.locator('svg[data-icon="angle-down"]')

    @property
    def manager_dropdown_menu(self):
        """Locate manager dropdown menu container."""
        return (
            self.page.locator('label:has-text("Managers")')
            .locator("..")
            .locator("div.absolute.z-20")
        )

    @property
    def manager_search_input(self):
        """Locate manager dropdown search input."""
        return self.manager_dropdown_menu.locator('> div > input[placeholder="Search"]')

    def search_manager(self, search_text: str) -> None:
        """Type text into manager search input."""
        self.type_characters_sequentially(
            self.manager_search_input,
            search_text,
            delay=500,
            description="Manager Search Input",
        )

    def clear_manager_search(self) -> None:
        """Clear all characters from manager search input."""
        self.fill_locator(self.manager_search_input, "", "Manager Search Input")

    @property
    def manager_search_loading_spinner(self):
        """Locate manager search loading spinner."""
        return self.manager_dropdown_menu.locator("div.loader__spinner")

    def wait_for_manager_search_complete(self) -> None:
        """Wait for manager search loading spinner to disappear."""
        self.wait_for(
            self.manager_search_loading_spinner,
            state="hidden",
            timeout=10000,
            description="Manager Search Loading Spinner",
        )

    @property
    def manager_select_all_option(self):
        """Locate manager 'Select All' checkbox option."""
        return self.manager_dropdown_menu.locator("ul > li").first

    @property
    def manager_results_list(self):
        """Locate manager dropdown results list container."""
        return self.manager_dropdown_menu.locator("div.max-h-32.overflow-y-auto")

    def get_manager_result_names(self) -> list[str]:
        """Get all manager names from results list."""
        items = self.manager_results_list.locator("li span[title]")
        return [self.get_attribute(items.nth(i), "title") for i in range(items.count())]

    def select_manager_by_name(self, manager_name: str) -> None:
        """Select a manager by name from the results list."""
        label_locator = self.manager_results_list.locator(
            f'label:has(span[title="{manager_name}"])'
        )
        self.click_locator(label_locator, f"Manager: {manager_name}")

    def click_manager_select_all(self) -> None:
        """Click the 'Select All' checkbox for managers."""
        self.click_locator(
            self.manager_select_all_option,
            "Manager Select All Checkbox",
        )

    @property
    def employees_text(self):
        return self.page.locator("#main-section").get_by_text("Employees", exact=True)

    @property
    def employee_dropdown(self):
        return self.page.get_by_text("All Employees", exact=True)

    @property
    def employee_dropdown_options(self):
        """Locate employee dropdown options."""
        return (
            self.page.locator('label:has-text("Employees")')
            .locator("..")
            .locator("button")
        )

    @property
    def employee_dropdown_placeholder(self):
        """Locate employee dropdown button placeholder text."""
        return self.employee_dropdown_options.locator("span.truncate")

    def get_employee_dropdown_placeholder_text(self) -> str:
        """Get the text of the employee dropdown placeholder."""
        return self.get_text(
            self.employee_dropdown_placeholder, "Employee Dropdown Placeholder"
        )

    @property
    def employee_dropdown_arrow(self):
        """Locate employee dropdown arrow icon (SVG)."""
        return self.employee_dropdown_options.locator('svg[data-icon="angle-down"]')

    @property
    def employee_dropdown_menu(self):
        """Locate employee dropdown menu container."""
        return (
            self.page.locator('label:has-text("Employees")')
            .locator("..")
            .locator("div.absolute.z-20")
        )

    @property
    def employee_search_input(self):
        """Locate employee dropdown search input."""
        return self.employee_dropdown_menu.locator(
            '> div > input[placeholder="Search"]'
        )

    def search_employee(self, search_text: str) -> None:
        """Type text into employee search input."""
        self.type_characters_sequentially(
            self.employee_search_input,
            search_text,
            delay=500,
            description="Employee Search Input",
        )

    def clear_employee_search(self) -> None:
        """Clear all characters from employee search input."""
        self.fill_locator(self.employee_search_input, "", "Employee Search Input")

    @property
    def employee_search_loading_spinner(self):
        """Locate employee search loading spinner."""
        return self.employee_dropdown_menu.locator("div.loader__spinner")

    def wait_for_employee_search_complete(self) -> None:
        """Wait for employee search loading spinner to disappear."""
        self.wait_for(
            self.employee_search_loading_spinner,
            state="hidden",
            timeout=10000,
            description="Employee Search Loading Spinner",
        )

    @property
    def employee_select_all_option(self):
        """Locate employee 'Select All' checkbox option."""
        return self.employee_dropdown_menu.locator("ul > li").first

    @property
    def employee_results_list(self):
        """Locate employee dropdown results list container."""
        return self.employee_dropdown_menu.locator("div.max-h-32.overflow-y-auto")

    def get_employee_result_names(self) -> list[str]:
        """Get all employee names from results list."""
        items = self.employee_results_list.locator("li span[title]")
        return [self.get_attribute(items.nth(i), "title") for i in range(items.count())]

    def select_employee_by_name(self, employee_name: str) -> None:
        """Select an employee by name from the results list."""
        label_locator = self.employee_results_list.locator(
            f'label:has(span[title="{employee_name}"])'
        )
        self.click_locator(label_locator, f"Employee: {employee_name}")

    def click_employee_select_all(self) -> None:
        """Click the 'Select All' checkbox for employees."""
        self.click_locator(
            self.employee_select_all_option,
            "Employee Select All Checkbox",
        )

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

    @property
    def team_distribution_tooltip(self):
        return self.page.locator('div[role="tooltip"].tooltip-shadow')

    @property
    def manager_table_loading_bar(self):
        return self.page.locator(".flex.space-x-2")

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

        # Get current from date value
        current_from_date_str = self.get_from_date_value()
        try:
            # Try parsing as 'MMM D, YYYY' (e.g., 'Jan 6, 2026')
            current_date = datetime.strptime(current_from_date_str, "%b %d, %Y")
            target_date = datetime.strptime(from_date, "%b %d, %Y")
        except Exception:
            # Fallback: try ISO format
            current_date = datetime.fromisoformat(current_from_date_str)
            target_date = datetime.fromisoformat(from_date)

        if (
            current_date.month < target_date.month
            or current_date.year < target_date.year
        ):
            self.next_month_button.click()
        elif (
            current_date.month > target_date.month
            or current_date.year > target_date.year
        ):
            self.previous_month_button.click()

        # Now select the day
        self.page.get_by_role("option", name=new_from_date_str).click()

    def change_to_date(self, to_date: str) -> None:
        """
        Change the 'To' date in the date picker.
        :param to_date: Date String
        """
        new_to_date_str: str = to_choose_date_string(to_date)
        self.to_date_button.click()

        # Get current to date value
        current_to_date_str = self.get_to_date_value()
        try:
            # Try parsing as 'MMM D, YYYY' (e.g., 'Jan 6, 2026')
            current_date = datetime.strptime(current_to_date_str, "%b %d, %Y")
            target_date = datetime.strptime(to_date, "%b %d, %Y")
        except Exception:
            # Fallback: try ISO format
            current_date = datetime.fromisoformat(current_to_date_str)
            target_date = datetime.fromisoformat(to_date)

        if (
            current_date.month > target_date.month
            or current_date.year > target_date.year
        ):
            self.previous_month_button.click()
        elif (
            current_date.month < target_date.month
            or current_date.year < target_date.year
        ):
            self.next_month_button.click()

        # Now select the day
        self.page.get_by_role("option", name=new_to_date_str).click()

    def get_from_date_value(self) -> str:
        """Get the current value of the 'From' date."""
        return self.get_text(self.from_date_button, "From Date Button")

    def get_to_date_value(self) -> str:
        """Get the current value of the 'To' date."""
        return self.get_text(self.to_date_button, "To Date Button")

    def wait_for_hidden_notification_row(self) -> None:
        """Wait for the notification row to be hidden."""
        self.wait_for(
            self.notification_row,
            state="hidden",
            timeout=10000,
            description="Notification Row",
        )

    def get_notification_type(self) -> str:
        """Get the notification type from the notification row."""
        notification_type: str = ""
        notification_class = self.get_attribute(
            self.notification_row, "class", "Notification Row"
        )
        if (
            "bg-warning-100" in notification_class
            and "border-warning-b" in notification_class
        ):
            notification_type = "warning"

        return notification_type

    def wait_for_manager_table_load(self) -> None:
        """Wait for the manager table to load."""
        self.wait_for(
            self.manager_table_first_row,
            state="visible",
            timeout=10000,
            description="Manager Table First Row",
        )

    def wait_for_manager_table_loading_complete(self) -> None:
        """Wait for the manager table loading bar to disappear."""
        self.wait_for(
            self.manager_table_loading_bar,
            state="hidden",
            timeout=30000,
            description="Manager Table Loading Bar",
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

    def get_prodoscore_by_row(self, row_index: int) -> str:
        """Get the prodoscore from a specific row in the manager table."""
        return (
            self.page.locator("tbody tr")
            .nth(row_index)
            .locator("td")
            .nth(1)
            .locator("p")
            .inner_text()
        )

    def get_direct_team_prodoscore_by_row(self, row_index: int) -> str:
        """Get the direct team prodoscore from a specific row in the manager table."""
        return (
            self.page.locator("tbody tr")
            .nth(row_index)
            .locator("td")
            .nth(3)
            .locator("p")
            .inner_text()
        )

    def get_percent_change_by_row(self, row_index: int) -> str:
        """Get the percent change from a specific row in the manager table."""
        return (
            self.page.locator("tbody tr")
            .nth(row_index)
            .locator("td")
            .nth(4)
            .locator("p")
            .inner_text()
        )

    def _get_manager_row(self, manager_name: str):
        """Get the row locator for a specific manager by name."""
        return self.page.locator(
            f'tbody tr:has(td:first-child p:text-is("{manager_name}"))'
        )

    def get_manager_data(self, manager_name: str):
        """Get prodoscore, team distribution, and percent change values and colors for a specific manager, including arrow type in percent change."""
        row = self._get_manager_row(manager_name)
        tds = row.locator("td")

        # Prodoscore value and color (from class)
        prodoscore_p = tds.nth(1).locator("p")
        prodoscore = prodoscore_p.inner_text()
        prodoscore_class = prodoscore_p.get_attribute("class")
        prodoscore_color = class_to_color_name(prodoscore_class)

        # Team distribution: handle multiple bars (segments)
        team_distribution_bars = []
        team_distribution_bar_divs = tds.nth(2).locator("div.flex > div")
        for i in range(team_distribution_bar_divs.count()):
            bar = team_distribution_bar_divs.nth(i)
            value = bar.inner_text()
            bar_class = bar.get_attribute("class")
            color = class_to_color_name(bar_class)
            team_distribution_bars.append({"value": value, "color": color})
        # Sort bars by color order: blue, gray, red
        color_order = {"red": 0, "gray": 1, "blue": 2}
        team_distribution_bars.sort(key=lambda x: color_order.get(x["color"], 99))

        # Percent change value, color, and arrow type (from svg class)
        percent_change_div = tds.nth(4).locator("div:has(p)")
        percent_change_svg = percent_change_div.locator("svg")
        percent_change_arrow_type = None
        if percent_change_svg.count() > 0:
            percent_change_arrow_type = percent_change_svg.get_attribute("data-icon")
        percent_change_p = percent_change_div.locator("p")
        percent_change = percent_change_p.inner_text()
        percent_change_class = percent_change_div.get_attribute("class")
        percent_change_color = class_to_color_name(percent_change_class)

        # Direct team prodoscore value and color (from class)
        direct_team_prodoscore_p = tds.nth(3).locator("p")
        direct_team_prodoscore = direct_team_prodoscore_p.inner_text()
        direct_team_prodoscore_class = direct_team_prodoscore_p.get_attribute("class")
        direct_team_prodoscore_color = class_to_color_name(direct_team_prodoscore_class)

        # Handle dash ('-') for prodoscore and direct_team_prodoscore
        def parse_score(score):
            return score if score == "-" else int(score)

        return {
            "prodoscore": {"score": parse_score(prodoscore), "color": prodoscore_color},
            "team_distribution": team_distribution_bars,
            "direct_team_prodoscore": {
                "score": parse_score(direct_team_prodoscore),
                "color": direct_team_prodoscore_color,
            },
            "percent_change": {
                "value": percent_change,
                "color": percent_change_color,
                "arrow_type": percent_change_arrow_type,
            },
        }

    def go_to_manager_under_page(self, manager_name: str):
        """Click on a manager name to navigate to the Manager Under Page."""
        from .manager_under_page import ManagerUnderPage

        row = self._get_manager_row(manager_name)
        self.click_locator(row, f"Manager Name Link for {manager_name}")
        self.wait_for_url("**/employees/under/**")
        return ManagerUnderPage(self.page)

    def get_team_distribution_bars_locator(self, manager_name: str):
        """
        Return the locator for the team distribution bars for a specific manager row.
        This can be used to hover over the bars.
        """
        row = self._get_manager_row(manager_name)
        return row.locator("td").nth(2).locator("div.flex > div")

    def hover_team_distribution_bar_by_manager_name(
        self, manager_name: str, bar_index: int = 0
    ) -> None:
        """
        Hover over a specific team distribution bar for a given manager.
        Args:
            manager_name: The name of the manager whose bar to hover over.
            bar_index: The index of the bar to hover over (0-based, default 0 for first bar).
        """
        self.hover_locator(
            self.get_team_distribution_bars_locator(manager_name).nth(bar_index),
            f"Team Distribution Bar {bar_index} for {manager_name}",
        )

    def get_team_distribution_tooltip_values(self):
        """
        Extracts the values from the team distribution tooltip after it is shown.
        Returns a dict with keys: 'below_average', 'within_average', 'above_average',
        each containing percentage (value, color) and count (value, color).
        """
        tooltip = self.team_distribution_tooltip
        rows = tooltip.locator("tbody tr")
        result = {}
        label_map = {
            "Below Average": "below_average",
            "Within Average": "within_average",
            "Above Average": "above_average",
        }
        for i in range(rows.count()):
            row = rows.nth(i)
            label = row.locator("td").nth(0).inner_text().strip()
            percent_cell = row.locator("td").nth(1)
            count_cell = row.locator("td").nth(2)
            percent_value = percent_cell.inner_text().strip()
            percent_class = percent_cell.get_attribute("class")
            percent_color = class_to_color_name(percent_class)
            count_value = count_cell.inner_text().strip()
            count_class = count_cell.get_attribute("class")
            count_color = class_to_color_name(count_class)
            result[label_map[label]] = {
                "percentage": {"value": percent_value, "color": percent_color},
                "count": {"value": count_value, "color": count_color},
            }
        return result

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
