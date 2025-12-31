"""Sample test cases for the manager page using pytest framework."""

import pytest
from automation_lib.config import TestDataLoader
from playwright.sync_api import expect

from automation_test.constants.enums import IsAppUser, Role, TestUser, ViewStatus
from automation_test.db.employee_prodoscore_utils import (
    bulk_insert_employee_prodoscores,
    insert_employee_prodoscore,
)
from automation_test.models.employee_prodoscore import EmployeeProdoscore


@pytest.fixture(scope="class", name="manager_page")
def go_to_manager_page(dashboard_page):
    manager_page = dashboard_page.go_to_manager_page()
    yield manager_page


@pytest.fixture(scope="class", name="manager_page_testdata")
def manager_page_testdata(config):
    data_file = config.get("test_data.manager_page.test_data_file")
    return TestDataLoader(data_file)


class TestManagerPage:
    """Test cases for the manager page."""

    @pytest.mark.order(1)
    @pytest.mark.manager_page
    def test_sample1(
        self,
        employees,
        manager_page,
        db_client,
        manager_page_testdata,
        current_date,
        request,
    ):
        # Get test data for this test case
        test_data = manager_page_testdata.get(request.node.name)

        # Get login user and main user
        login_user = employees.get(TestUser.LOGIN_USER.val)
        main_user = employees.get(TestUser.MAIN_USER.val)

        # Change role & view status for both users
        for user in [login_user, main_user]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change manager and role of user_1
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(main_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Insert employee prodoscore data for user_1 and user_2 using bulk insert
        prodoscore_data = test_data.get("employee_prodoscores")
        employee_prodoscores = [
            EmployeeProdoscore(
                domain_id=user.domain_id,
                employee_id=user.id,
                date=current_date,
                role=user.role,
                score=item.get("score"),
                ip_int_ext=item.get("ip_int_ext"),
                total_gap_time=item.get("total_gap_time"),
                total_active_time=item.get("total_active_time"),
                gap_times=item.get("gap_times"),
                first_last_activity_times=item.get("first_last_activity_times"),
            )
            for user, item in zip([user_1, user_2], prodoscore_data)
        ]
        bulk_insert_employee_prodoscores(db_client, employee_prodoscores)

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
        expected_num_rows = len([user_1, user_2])
        # "{what failed}. Actual: {actual}, Expected: {expected}"
        assert num_rows == expected_num_rows, (
            f"Row count mismatch.\n"
            f"Actual: {num_rows}\n"
            f"Expected: {expected_num_rows}",
        )

        # Verify the manager table is sorted by manager name (full_name)
        manager_names_in_table = [
            manager_page.get_manager_name_by_row(i) for i in range(num_rows)
        ]
        # Get the expected sorted names from the test data
        expected_names = sorted([login_user.full_name, main_user.full_name])
        assert manager_names_in_table == expected_names, (
            f"Manager table not sorted by name.\n"
            f"Actual: {manager_names_in_table}\n"
            f"Expected: {expected_names}"
        )

    @pytest.mark.order(3)
    @pytest.mark.manager_page
    def test_sample2(
        self,
        employees,
        manager_page,
        db_client,
        current_date,
        request,
        manager_page_testdata,
    ):
        # Get test data for this test case
        test_data = manager_page_testdata.get(request.node.name)

        # Get main user, user_1 and user_2
        main_user = employees.get(TestUser.MAIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status of main user
        main_user.change_role(Role.ADMINISTRATOR.id)
        main_user.change_view_status(ViewStatus.COMPANY.val)
        main_user.commit(db_client)

        # Change role & view status of user_1
        user_1.change_role(Role.MANAGER.id)
        user_1.change_view_status(ViewStatus.TEAM.val)
        user_1.commit(db_client)

        # Change role & view status of user_2
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.SELF.val)
        user_2.commit(db_client)

        # Get user_3, user_4 and user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_2)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Insert employee prodoscores data for user_3, user_4 and user_5
        prodoscore_data = test_data.get("employee_prodoscores")
        employee_prodoscores = [
            EmployeeProdoscore(
                domain_id=user.domain_id,
                employee_id=user.id,
                date=current_date,
                role=user.role,
                score=item.get("score"),
                ip_int_ext=item.get("ip_int_ext"),
                total_gap_time=item.get("total_gap_time"),
                total_active_time=item.get("total_active_time"),
                gap_times=item.get("gap_times"),
                first_last_activity_times=item.get("first_last_activity_times"),
            )
            for user, item in zip([user_3, user_4, user_5], prodoscore_data)
        ]
        bulk_insert_employee_prodoscores(db_client, employee_prodoscores)

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Verify number of rows in the manager table
        num_rows = manager_page.get_number_of_rows_in_manager_table()
        expected_num_rows = len([user_3, user_4])
        # "{what failed}. Actual: {actual}, Expected: {expected}"
        assert num_rows == expected_num_rows, (
            f"Row count mismatch.\n"
            f"Actual: {num_rows}\n"
            f"Expected: {expected_num_rows}",
        )

        # Verify the manager table is sorted by manager name (full_name)
        manager_names_in_table = [
            manager_page.get_manager_name_by_row(i) for i in range(num_rows)
        ]
        # Get the expected sorted names from the test data
        expected_names = sorted([main_user.full_name, user_1.full_name])
        assert manager_names_in_table == expected_names, (
            f"Manager table not sorted by name.\n"
            f"Actual: {manager_names_in_table}\n"
            f"Expected: {expected_names}"
        )

    @pytest.mark.order(2)
    @pytest.mark.manager_page
    def test_sample3(
        self,
        employees,
        manager_page,
        db_client,
        current_date,
        request,
        manager_page_testdata,
    ):
        # Get test data for this test case
        test_data = manager_page_testdata.get(request.node.name)

        # Get main user
        main_user = employees.get(TestUser.MAIN_USER.val)

        # Change role & view status of main user
        main_user.change_role(Role.ADMINISTRATOR.id)
        main_user.change_view_status(ViewStatus.COMPANY.val)
        main_user.change_is_app_user(IsAppUser.ACTIVATE.val)
        main_user.commit(db_client)

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change manager and role of user_1
        user_1.change_manager(main_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Insert employee prodoscore data for user_1
        prodoscore_data = test_data.get("employee_prodoscores")
        prodoscore_for_user_1 = EmployeeProdoscore(
            domain_id=user_1.domain_id,
            employee_id=user_1.id,
            date=current_date,
            role=user_1.role,
            score=prodoscore_data[0].get("score"),
            ip_int_ext=prodoscore_data[0].get("ip_int_ext"),
            total_gap_time=prodoscore_data[0].get("total_gap_time"),
            total_active_time=prodoscore_data[0].get("total_active_time"),
            gap_times=prodoscore_data[0].get("gap_times"),
            first_last_activity_times=prodoscore_data[0].get(
                "first_last_activity_times"
            ),
        )
        insert_employee_prodoscore(db_client, prodoscore_for_user_1)

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_no_data_found()

        # Verify no data message and image is shown when there is no data
        expect(manager_page.no_data_found_heading).to_be_visible()
        expect(manager_page.no_data_found_image).to_be_visible()
