"""Sample test cases for the manager page using pytest framework."""

import pytest
from playwright.sync_api import expect

from automation_test.db.employee_prodoscore_utils import insert_employee_prodoscore
from automation_test.models.employee_prodoscore import EmployeeProdoscore


@pytest.fixture(scope="class", name="manager_page")
def go_to_manager_page(dashboard_page):
    manager_page = dashboard_page.go_to_manager_page()
    yield manager_page


class TestManagerPage:
    """Test cases for the manager page."""

    @pytest.mark.order(1)
    @pytest.mark.manager_page
    def test_sample1(self, domain, employees, manager_page, db_client):
        # Get login user and main user
        login_user = employees.get("login_user")
        main_user = employees.get("main_user")

        # Change role & view status of login user
        login_user.change_role(15000)
        login_user.change_view_status(3)
        login_user.commit(db_client)

        # Change role & view status of main user
        main_user.change_role(15000)
        main_user.change_view_status(3)
        main_user.commit(db_client)

        # Get user_1 and user_2
        user_1 = employees.get("user_1")
        user_2 = employees.get("user_2")

        # Change manager and role of user_1
        user_1.change_manager(login_user)
        user_1.change_role(10000)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(main_user)
        user_2.change_role(10000)
        user_2.commit(db_client)

        # Insert employee prodoscore data for user_1
        prodoscore_for_user_1 = EmployeeProdoscore(
            domain_id=user_1.domain_id,
            employee_id=user_1.id,
            date="2025-12-28",
            role=user_1.role,
            score=2,
            ip_int_ext=1,
            total_gap_time=210,
            total_active_time=1,
            gap_times="[[0,210]]",
            first_last_activity_times="[-1,-1]",
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_1)

        # Insert employee prodoscore data for user_2
        prodoscore_for_user_2 = EmployeeProdoscore(
            domain_id=user_2.domain_id,
            employee_id=user_2.id,
            date="2025-12-28",
            role=user_2.role,
            score=2,
            ip_int_ext=1,
            total_gap_time=210,
            total_active_time=1,
            gap_times="[[0,210]]",
            first_last_activity_times="[-1,-1]",
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_2)

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Verify default values on date filters
        expect(manager_page.date_range_dropdown).to_have_value("last-7-days")
        expect(manager_page.from_date_text).to_be_visible()
        expect(manager_page.from_date_button).not_to_have_text("")
        expect(manager_page.to_date_text).to_be_visible()
        expect(manager_page.to_date_button).not_to_have_text("")

        # Verify presence of department, role, manager, and employee filters
        expect(manager_page.departments_text).to_be_visible()
        expect(manager_page.department_dropdown).to_be_visible()
        expect(manager_page.roles_text).to_be_visible()
        expect(manager_page.role_dropdown).to_be_visible()
        expect(manager_page.managers_text).to_be_visible()
        expect(manager_page.manager_dropdown).to_be_visible()
        expect(manager_page.employees_text).to_be_visible()
        expect(manager_page.employee_dropdown).to_be_visible()

        # Verify presence of Apply and Reset buttons
        expect(manager_page.apply_button).to_be_visible()
        expect(manager_page.reset_button).to_be_visible()

        # Verify presence of team Prodoscore headings
        expect(manager_page.team_prodoscore_heading).to_be_visible()

        # Verify presence of table column headers
        expect(manager_page.manager_name_columnheader).to_be_visible()
        expect(manager_page.prodoscore_columnheader).to_be_visible()
        expect(manager_page.team_distribution_columnheader).to_be_visible()
        expect(manager_page.direct_team_prodoscore_columnheader).to_be_visible()
        expect(manager_page.percent_change_columnheader).to_be_visible()

        # Verify number of rows in the manager table
        num_rows = manager_page.get_number_of_rows_in_manager_table()
        assert num_rows == 2, f"Expected 2 rows in manager table, found {num_rows}"

        # Verify the manager table is sorted by manager name (full_name)
        manager_names_in_table = [
            manager_page.get_manager_name_by_row(i) for i in range(num_rows)
        ]
        # Get the expected sorted names from the test data
        expected_names = sorted([login_user.full_name, main_user.full_name])
        assert (
            manager_names_in_table == expected_names
        ), f"Manager table not sorted by name. Table: {manager_names_in_table}, Expected: {expected_names}"

    def test_sample2(self, domain, employees, manager_page, db_client):
        # Get main user, user_1 and user_2
        main_user = employees.get("main_user")
        user_1 = employees.get("user_1")
        user_2 = employees.get("user_2")

        # Change role & view status of main user
        main_user.change_role(15000)
        main_user.change_view_status(3)
        main_user.commit(db_client)

        # Change role & view status of user_1
        user_1.change_role(10000)
        user_1.change_view_status(2)
        user_1.commit(db_client)

        # Change role & view status of user_2
        user_2.change_role(10000)
        user_2.change_view_status(1)
        user_2.commit(db_client)

        # Get user_3, user_4 and user_5
        user_3 = employees.get("user_3")
        user_4 = employees.get("user_4")
        user_5 = employees.get("user_5")

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(10000)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(10000)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_2)
        user_5.change_role(10000)
        user_5.commit(db_client)

        # Insert employee prodoscore data for user_3
        prodoscore_for_user_3 = EmployeeProdoscore(
            domain_id=user_3.domain_id,
            employee_id=user_3.id,
            date="2025-12-28",
            role=user_3.role,
            score=2,
            ip_int_ext=1,
            total_gap_time=210,
            total_active_time=1,
            gap_times="[[0,210]]",
            first_last_activity_times="[-1,-1]",
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_3)

        # Insert employee prodoscore data for user_4
        prodoscore_for_user_4 = EmployeeProdoscore(
            domain_id=user_4.domain_id,
            employee_id=user_4.id,
            date="2025-12-28",
            role=user_4.role,
            score=2,
            ip_int_ext=1,
            total_gap_time=210,
            total_active_time=1,
            gap_times="[[0,210]]",
            first_last_activity_times="[-1,-1]",
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_4)

        # Insert employee prodoscore data for user_5
        prodoscore_for_user_5 = EmployeeProdoscore(
            domain_id=user_5.domain_id,
            employee_id=user_5.id,
            date="2025-12-28",
            role=user_5.role,
            score=2,
            ip_int_ext=1,
            total_gap_time=210,
            total_active_time=1,
            gap_times="[[0,210]]",
            first_last_activity_times="[-1,-1]",
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_5)

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Verify number of rows in the manager table
        num_rows = manager_page.get_number_of_rows_in_manager_table()
        assert num_rows == 2, f"Expected 2 rows in manager table, found {num_rows}"

        # Verify the manager table is sorted by manager name (full_name)
        manager_names_in_table = [
            manager_page.get_manager_name_by_row(i) for i in range(num_rows)
        ]
        # Get the expected sorted names from the test data
        expected_names = sorted([main_user.full_name, user_1.full_name])
        assert (
            manager_names_in_table == expected_names
        ), f"Manager table not sorted by name. Table: {manager_names_in_table}, Expected: {expected_names}"

    def test_sample3(self, domain, employees, manager_page, db_client):
        # Get main user
        main_user = employees.get("main_user")

        # Change role & view status of main user
        main_user.change_role(15000)
        main_user.change_view_status(3)
        main_user.change_is_app_user(1)
        main_user.commit(db_client)

        # Get user_1
        user_1 = employees.get("user_1")

        # Change manager and role of user_1
        user_1.change_manager(main_user)
        user_1.change_role(10000)
        user_1.commit(db_client)

        # Insert employee prodoscore data for user_1
        prodoscore_for_user_1 = EmployeeProdoscore(
            domain_id=user_1.domain_id,
            employee_id=user_1.id,
            date="2025-12-28",
            role=user_1.role,
            score=2,
            ip_int_ext=1,
            total_gap_time=210,
            total_active_time=1,
            gap_times="[[0,210]]",
            first_last_activity_times="[-1,-1]",
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_1)

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_no_data_found()

        # Verify no data message and image is shown when there is no data
        expect(manager_page.no_data_found_heading).to_be_visible()
        expect(manager_page.no_data_found_image).to_be_visible()
