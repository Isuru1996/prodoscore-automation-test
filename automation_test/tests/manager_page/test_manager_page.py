"""Test cases for the manager page using pytest framework."""

import pytest
from automation_lib.config import TestDataLoader
from playwright.sync_api import expect

from automation_test.constants.enums import IsAppUser, Role, TestUser, ViewStatus
from automation_test.constants.enums.employee_status import EmployeeStatus
from automation_test.constants.enums.status import Status
from automation_test.db.employee_prodoscore_utils import (
    bulk_insert_employee_prodoscores,
)
from automation_test.db.employee_utils import (
    add_test_employees,
    delete_employees,
    get_employees,
    set_manager_chain_for_employees,
)
from automation_test.db.organization_prodoscore_utils import (
    insert_organization_prodoscore,
)
from automation_test.helpers.manager_page_test_utils import (
    assert_hover_and_distribution_bars,
    assert_manager_prodoscore_and_team_prodoscore,
    assert_manager_prodoscore_team_prodoscore_and_team_distributions,
    assert_manager_prodoscore_team_scores_and_percentage_change,
    assert_manager_prodoscore_with_no_score,
    assert_manager_table_sorted_and_row_count,
    assert_percentage_change,
)
from automation_test.models import Employee, EmployeeProdoscore, OrganizationProdoscore
from automation_test.utils.date_utils import add_days_to_date
from automation_test.utils.testdata_utils import (
    insert_employee_holidays_from_testdata,
    insert_employee_prodoscores_from_testdata,
    insert_organization_prodoscores_from_testdata,
    map_day_keys_to_dates,
)


@pytest.fixture(scope="class", name="manager_page")
def go_to_manager_page(dashboard_page, logger):
    """Navigates to the manager page from the dashboard."""
    logger.info("Navigating to manager page")
    manager_page = dashboard_page.go_to_manager_page()
    yield manager_page


@pytest.fixture(scope="class", name="manager_page_testdata")
def manager_page_testdata(config, logger):
    """Loads test data for manager page tests."""
    logger.info("Loading manager page test data")
    data_file = config.get("test_data.manager_page.test_data_file")
    return TestDataLoader(data_file)


@pytest.fixture(scope="function", name="pagination_users")
def add_users_for_pagination(db_client, config, logger):
    """Adds users required for pagination tests."""
    logger.info(f"Setting up pagination users")
    inserted_ids = add_test_employees(
        db_client=db_client,
        config=config,
        role=10000,
        view_status=2,
        status=1,
        source="Test",
        number_of_employees=105,
    )
    employees: list[Employee] = get_employees(db_client, inserted_ids)
    yield employees
    logger.info(f"Tearing down pagination users")
    delete_employees(db_client, inserted_ids)


class TestManagerPage:
    """Test cases for the manager page."""

    @pytest.mark.order(1)
    @pytest.mark.manager_page
    def test_default_manager_page_view_filters_and_sorting(
        self,
        domain,
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

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

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

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, main_user])

    @pytest.mark.order(2)
    @pytest.mark.manager_page
    def test_only_company_or_team_view_with_subordinates_are_listed_as_managers(
        self,
        domain,
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

        # Get user_3 and user_4
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [user_3, user_4])

    @pytest.mark.order(3)
    @pytest.mark.manager_page
    def test_app_users_are_not_listed_as_managers(
        self,
        domain,
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
        main_user.change_status(EmployeeStatus.INACTIVE.val)
        main_user.commit(db_client)

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change manager and role of user_1
        user_1.change_manager(main_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_no_data_for_selected_time()

        # Verify no data message and image is shown when there is no data
        expect(manager_page.no_data_for_selected_time).to_be_visible()
        expect(manager_page.no_data_found_image).to_be_visible()

    @pytest.mark.order(4)
    @pytest.mark.manager_page
    def test_date_range_change_updates_dates_and_resets_pagination(
        self,
        domain,
        pagination_users,
        manager_page,
        db_client,
        from_date,
        current_date,
        request,
        manager_page_testdata,
    ):
        # Get test data for this test case
        test_data = manager_page_testdata.get(request.node.name)

        # Add same employee prodoscore for all pagination users
        prodoscore_data = test_data.get("employee_prodoscores")
        if prodoscore_data:
            score_item = prodoscore_data[0]
            employee_prodoscores = [
                EmployeeProdoscore(
                    domain_id=user.domain_id,
                    employee_id=user.id,
                    date=current_date,
                    role=user.role,
                    score=score_item.get("score"),
                )
                for user in pagination_users
                if user.id is not None
            ]
            bulk_insert_employee_prodoscores(db_client, employee_prodoscores)

        # Insert organization prodoscore for the domain
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        if organization_prodoscore_data is not None:
            insert_organization_prodoscore(
                db_client,
                OrganizationProdoscore(
                    domain_id=domain.id,
                    date=current_date,
                    score=organization_prodoscore_data["score"],
                ),
            )

        # Update manager IDs for pagination users to ensure they are listed as managers
        set_manager_chain_for_employees(db_client, pagination_users)

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Scroll to bottom of the manager table
        manager_page.scroll_to_manager_table_bottom()

        # Assert pagination buttons
        expect(manager_page.get_button_by_number(1)).to_have_attribute(
            "aria-current", "page"
        )
        expect(manager_page.manager_page_first_button).to_be_disabled()
        expect(manager_page.manager_page_previous_button).to_be_disabled()
        expect(manager_page.manager_page_next_button).to_be_enabled()
        expect(manager_page.manager_page_last_button).to_be_enabled()

        # Click the last page button
        manager_page.click_last_page_button()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Assert pagination buttons
        expect(manager_page.get_button_by_number(1)).not_to_have_attribute(
            "aria-current", "page"
        )
        expect(manager_page.manager_page_first_button).to_be_enabled()
        expect(manager_page.manager_page_previous_button).to_be_enabled()
        expect(manager_page.manager_page_next_button).to_be_disabled()
        expect(manager_page.manager_page_last_button).to_be_disabled()

        # Changes date range to "This Month"
        manager_page.change_date_range("this-month")

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Assert from date is changed correctly
        changed_from_date: str = manager_page.get_from_date_value()
        assert from_date != changed_from_date, (
            f"From date not matched.\n"
            f"Actual: {changed_from_date}\n"
            f"Expected: {from_date}",
        )

        # Scroll to bottom of the manager table
        manager_page.scroll_to_manager_table_bottom()

        # Assert pagination buttons
        expect(manager_page.get_button_by_number(1)).to_have_attribute(
            "aria-current", "page"
        )
        expect(manager_page.manager_page_first_button).to_be_disabled()
        expect(manager_page.manager_page_previous_button).to_be_disabled()
        expect(manager_page.manager_page_next_button).to_be_enabled()
        expect(manager_page.manager_page_last_button).to_be_enabled()

    @pytest.mark.order(5)
    @pytest.mark.manager_page
    def test_custom_range_invalid_shows_warning_and_blocks_apply_when_to_date_before_from_date(
        self,
        manager_page,
        from_date,
    ):
        # Change to_date to less than current from_date
        current_from_date_minus_1_day: str = add_days_to_date(from_date, -1)
        manager_page.change_to_date(current_from_date_minus_1_day)

        # Validate notification message
        expect(manager_page.notification_row).to_contain_text(
            "Please set a To date after the From date."
        )

        # Validate notification type is warning
        expected_type = "warning"
        actual_type = manager_page.get_notification_type()
        assert actual_type == expected_type, (
            f"Notification type mismatch.\n"
            f"Actual: {actual_type}\n"
            f"Expected: {expected_type}"
        )

        # Wait for notification to disappear
        manager_page.wait_for_hidden_notification_row()

        # Verify to date is reset to from_date
        actual_to_date = manager_page.get_to_date_value()
        assert actual_to_date == from_date, (
            f"To date not reset to from date.\n"
            f"Actual: {actual_to_date}\n"
            f"Expected: {from_date}"
        )

    @pytest.mark.order(6)
    @pytest.mark.manager_page
    def test_manager_names_are_displayed_correctly(
        self,
        domain,
        employees,
        manager_page,
        db_client,
        manager_page_testdata,
        current_date,
        request,
    ):
        # Get test data for this test case
        test_data = manager_page_testdata.get(request.node.name)

        # Get main user, user_1 and user_2
        main_user = employees.get(TestUser.MAIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        for user in [main_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

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

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(
            manager_page, [main_user, user_1, user_2]
        )

    @pytest.mark.order(7)
    @pytest.mark.manager_page
    def test_manager_prodoscore_team_distribution_single_day(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Assert overall manager prodoscore and team distributions
        assert_manager_prodoscore_team_prodoscore_and_team_distributions(
            manager_page, employees, employee_prodoscore_data, day_map
        )

    @pytest.mark.order(8)
    @pytest.mark.manager_page
    def test_manager_prodoscore_team_distribution_seven_days(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Assert overall manager prodoscore and team distributions
        assert_manager_prodoscore_team_prodoscore_and_team_distributions(
            manager_page, employees, employee_prodoscore_data, day_map
        )

        # # Iterate through each manager and verify their data
        # for key, employee in employees.items():
        #     # Aggregate self scores for all 7 days for this manager
        #     self_scores = [
        #         employee_prodoscore_data[day].get(key, {}).get("self", {}).get("score")
        #         for day in day_map.keys()
        #         if key in employee_prodoscore_data[day]
        #         and "self" in employee_prodoscore_data[day][key]
        #     ]

        #     if self_scores:
        #         # Get data from manager table
        #         manager_data = manager_page.get_manager_data(employee.full_name)

        #         # Manager's prodoscore (average over 7 days)
        #         expected_prodoscore = get_average_score(self_scores)
        #         expected_prodoscore_color = score_to_color(expected_prodoscore)
        #         actual_prodoscore = manager_data.get("prodoscore").get("score")
        #         actual_prodoscore_color = manager_data.get("prodoscore").get("color")
        #         assert actual_prodoscore == expected_prodoscore, (
        #             f"Prodoscore mismatch for {employee.full_name}.\n"
        #             f"Actual: {actual_prodoscore}\n"
        #             f"Expected: {expected_prodoscore}"
        #         )
        #         assert actual_prodoscore_color == expected_prodoscore_color, (
        #             f"Prodoscore color mismatch for {employee.full_name}.\n"
        #             f"Actual: {actual_prodoscore_color}\n"
        #             f"Expected: {expected_prodoscore_color}"
        #         )

        #         # Aggregate subordinate scores for all 7 days
        #         # For each day, calculate the average subordinate score, then average those for 7 days
        #         daily_team_scores = []
        #         # Collect each subordinate's scores for the whole week
        #         subordinate_weekly_scores = {}
        #         for day in day_map.keys():
        #             if key in employee_prodoscore_data[day]:
        #                 subordinates = employee_prodoscore_data[day][key].get(
        #                     "subordinates", {}
        #                 )
        #                 for sub_key, sub in subordinates.items():
        #                     if sub_key not in subordinate_weekly_scores:
        #                         subordinate_weekly_scores[sub_key] = []
        #                     subordinate_weekly_scores[sub_key].append(sub["score"])
        #                 scores = [sub["score"] for sub in subordinates.values()]
        #                 if scores:
        #                     daily_team_scores.append(
        #                         get_average_score_without_rounding(scores)
        #                     )

        #         # Sum of scores for each subordinate for the whole week as a list
        #         subordinate_total_scores_list = [
        #             get_average_score_without_rounding(scores)
        #             for scores in subordinate_weekly_scores.values()
        #         ]

        #         # Team Prodoscore
        #         expected_team_prodoscore = get_average_score(daily_team_scores)
        #         expected_team_prodoscore_color = score_to_color(
        #             expected_team_prodoscore
        #         )
        #         actual_team_prodoscore = manager_data.get("direct_team_prodoscore").get(
        #             "score"
        #         )
        #         actual_team_prodoscore_color = manager_data.get(
        #             "direct_team_prodoscore"
        #         ).get("color")
        #         assert actual_team_prodoscore == expected_team_prodoscore, (
        #             f"Team Prodoscore mismatch for {employee.full_name}.\n"
        #             f"Actual: {actual_team_prodoscore}\n"
        #             f"Expected: {expected_team_prodoscore}"
        #         )
        #         assert actual_team_prodoscore_color == expected_team_prodoscore_color, (
        #             f"Team Prodoscore color mismatch for {employee.full_name}.\n"
        #             f"Actual: {actual_team_prodoscore_color}\n"
        #             f"Expected: {expected_team_prodoscore_color}"
        #         )

        #         # Team distribution bars (all subordinate scores for the week)
        #         expected_team_distribution_bars: list[dict] = (
        #             get_team_distribution_bars(subordinate_total_scores_list)
        #         )
        #         actual_team_distribution_bars: list[dict] = manager_data.get(
        #             "team_distribution"
        #         )
        #         assert (
        #             actual_team_distribution_bars == expected_team_distribution_bars
        #         ), (
        #             f"Team distribution bars mismatch for {employee.full_name}.\n"
        #             f"Actual: {actual_team_distribution_bars}\n"
        #             f"Expected: {expected_team_distribution_bars}"
        #         )

        #         # Hover the team distribution bar
        #         manager_page.hover_team_distribution_bar_by_manager_name(
        #             employee.full_name
        #         )

        #         # Verify tooltip visibility
        #         expect(manager_page.team_distribution_tooltip).to_be_visible()

        #         # Verify tooltip values
        #         tooltip_data = manager_page.get_team_distribution_tooltip_values()
        #         expected_tooltip_data = get_expected_team_distribution_tooltip(
        #             subordinate_total_scores_list
        #         )
        #         assert tooltip_data == expected_tooltip_data, (
        #             f"Team distribution tooltip data mismatch for {employee.full_name}.\n"
        #             f"Actual: {tooltip_data}\n"
        #             f"Expected: {expected_tooltip_data}"
        #         )

    @pytest.mark.order(9)
    @pytest.mark.manager_page
    def test_team_distribution_single_band_all_subordinates_and_no_subordinates_for_some_band(
        self,
        domain,
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

        # Get users for subordinates
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Todo: Need to change view status
        # Change manager and role of user_1
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(main_user)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after change date
        manager_page.wait_for_manager_table_load()

        # Verify team distribution for each manager
        assert_hover_and_distribution_bars(
            manager_page, employees, employee_prodoscore_data, day_map
        )

    @pytest.mark.order(10)
    @pytest.mark.manager_page
    def test_team_distribution_all_bands_subordinates_in_each_band_displayed_correctly(
        self,
        domain,
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
        main_user = employees.get(TestUser.MAIN_USER.val)

        # Change role & view status for main user
        main_user.change_role(Role.ADMINISTRATOR.id)
        main_user.change_view_status(ViewStatus.COMPANY.val)
        main_user.commit(db_client)

        # Get users for subordinates
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change manager and role of user_1
        user_1.change_manager(main_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(main_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after change date
        manager_page.wait_for_manager_table_loading_complete()

        # Verify team distribution for each manager
        assert_hover_and_distribution_bars(
            manager_page, employees, employee_prodoscore_data, day_map
        )

    @pytest.mark.order(11)
    @pytest.mark.manager_page
    def test_manager_and_team_prodoscore_within_below_average_boundaries(
        self,
        domain,
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
        main_user = employees.get(TestUser.MAIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get users for subordinates
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change manager and role of user_1
        user_2.change_manager(main_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after change date
        manager_page.wait_for_manager_table_load()

        # Verify manager and team prodoscore
        assert_manager_prodoscore_and_team_prodoscore(
            manager_page,
            employees,
            employee_prodoscore_data,
            day_map,
        )

    @pytest.mark.order(12)
    @pytest.mark.manager_page
    def test_manager_and_team_prodoscore_within_average_above_boundaries(
        self,
        domain,
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
        main_user = employees.get(TestUser.MAIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get users for subordinates
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change manager and role of user_1
        user_2.change_manager(main_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after change date
        manager_page.wait_for_manager_table_load()

        # Verify manager and team prodoscore
        assert_manager_prodoscore_and_team_prodoscore(
            manager_page,
            employees,
            employee_prodoscore_data,
            day_map,
        )

    @pytest.mark.order(13)
    @pytest.mark.manager_page
    def test_manager_and_team_prodoscore_rounds_down_correctly(
        self,
        domain,
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
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(main_user)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # verify overall manager prodoscore and team prodoscore
        assert_manager_prodoscore_and_team_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map
        )

    @pytest.mark.order(14)
    @pytest.mark.manager_page
    def test_percentage_change_single_day_display(
        self,
        domain,
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
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(main_user)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Use helper for manager/team prodoscore and percent change assertions
        assert_percentage_change(
            manager_page,
            employees,
            employee_prodoscore_data,
            day_map,
        )

    @pytest.mark.order(15)
    @pytest.mark.manager_page
    def test_weekly_percentage_change_display(
        self,
        domain,
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
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(main_user)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_load()

        # Use helper for manager/team prodoscore and percent change assertions
        assert_percentage_change(
            manager_page,
            employees,
            employee_prodoscore_data,
            day_map,
        )

    @pytest.mark.order(16)
    @pytest.mark.manager_page
    def test_hidden_managers_not_displayed_except_logged_user_manager(
        self,
        domain,
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

        # Change role & view status & status for both users
        for user in [login_user, main_user]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.change_status(Status.HIDDEN.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(main_user)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user])

    @pytest.mark.order(17)
    @pytest.mark.manager_page
    def test_manager_not_shown_if_all_subordinates_hidden(
        self,
        domain,
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

        # Change role & view status & status for both users
        for user in [login_user, main_user]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_1.change_manager(login_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_status(Status.HIDDEN.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(main_user)
        user_4.change_role(Role.MANAGER.id)
        user_4.change_status(Status.HIDDEN.val)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(main_user)
        user_5.change_role(Role.MANAGER.id)
        user_5.change_status(Status.HIDDEN.val)
        user_5.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user])

    @pytest.mark.order(18)
    @pytest.mark.manager_page
    def test_manager_and_team_prodoscore_and_percentage_change_display_zero_scores(
        self,
        domain,
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
        main_user = employees.get(TestUser.MAIN_USER.val)

        # Change role & view status & status for both users
        main_user.change_role(Role.ADMINISTRATOR.id)
        main_user.change_view_status(ViewStatus.COMPANY.val)
        main_user.commit(db_client)

        # Get user_1 and user_2
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change manager and role of user_2
        user_1.change_manager(main_user)
        user_1.change_role(Role.MANAGER.id)
        user_1.commit(db_client)

        # Change manager and role of user_2
        user_2.change_manager(main_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for manager/team prodoscore and percent change assertions
        assert_manager_prodoscore_team_scores_and_percentage_change(
            manager_page,
            employees,
            employee_prodoscore_data,
            day_map,
        )

    @pytest.mark.order(19)
    @pytest.mark.manager_page
    def test_only_subordinates_displayed_in_team_view_for_login_user(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.TEAM.val)
            user.commit(db_client)

        # Change main user manager as login user
        main_user.change_manager(login_user)
        main_user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, main_user])

    @pytest.mark.order(20)
    @pytest.mark.manager_page
    def test_manager_excluded_when_all_direct_subordinates_on_holiday(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Insert employee holidays from test data
        holiday_data = test_data.get("employee_holidays")
        insert_employee_holidays_from_testdata(
            holiday_data, day_map, employees, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

    @pytest.mark.order(21)
    @pytest.mark.manager_page
    def test_manager_prodoscore_display_dash_when_manager_on_holiday_and_subordinate_visible(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Insert employee holidays from test data
        holiday_data = test_data.get("employee_holidays")
        insert_employee_holidays_from_testdata(
            holiday_data, day_map, employees, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_prodoscore_with_no_score(
            manager_page, employees, employee_prodoscore_data, holiday_data, day_map
        )

    @pytest.mark.order(22)
    @pytest.mark.manager_page
    def test_manager_and_subordinate_exclusion_when_terminated(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_4
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Terminate main user and user_4
        main_user.change_role(Role.TERMINATED.id)
        main_user.commit(db_client)

        user_4.change_role(Role.TERMINATED.id)
        user_4.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

        # Use helper for row count and sorting assertion
        assert_manager_prodoscore_and_team_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map
        )

    @pytest.mark.order(23)
    @pytest.mark.manager_page
    def test_manager_and_subordinate_exclusion_when_not_activated(
        self,
        domain,
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
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, main_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_1 and user_2
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(main_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_4
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Terminate main user and user_4
        main_user.change_role(Role.NOT_ACTIVATED.id)
        main_user.commit(db_client)

        user_4.change_role(Role.NOT_ACTIVATED.id)
        user_4.commit(db_client)

        # Create a map of days
        employee_prodoscore_data = test_data.get("employee_prodoscores")
        day_map = map_day_keys_to_dates(employee_prodoscore_data, current_date)

        # Insert employee prodoscores from test data
        insert_employee_prodoscores_from_testdata(
            employee_prodoscore_data, day_map, employees, db_client
        )

        # Insert organization prodoscores from test data
        organization_prodoscore_data = test_data.get("organization_prodoscores")
        insert_organization_prodoscores_from_testdata(
            organization_prodoscore_data, day_map, domain, db_client
        )

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

        # Use helper for row count and sorting assertion
        assert_manager_prodoscore_and_team_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map
        )
