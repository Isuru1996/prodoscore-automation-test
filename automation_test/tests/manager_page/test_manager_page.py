"""Test cases for the manager page using pytest framework."""

import pytest
from automation_lib.config import TestDataLoader
from playwright.sync_api import expect

from automation_test.constants.enums import IsAppUser, Role, TestUser, ViewStatus
from automation_test.constants.enums.department import Department
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
    assert_date_reset_to_from_date,
    assert_filters_placeholder,
    assert_hover_and_distribution_bars,
    assert_manager_prodoscore_and_team_prodoscore,
    assert_manager_prodoscore_team_prodoscore_and_team_distributions,
    assert_manager_prodoscore_team_scores_and_percentage_change,
    assert_manager_prodoscore_with_no_score,
    assert_manager_table_sorted_and_row_count,
    assert_manager_table_sorted_by_direct_team_prodoscore,
    assert_manager_table_sorted_by_percentage_change,
    assert_manager_table_sorted_by_prodoscore,
    assert_manager_under_page_navigation,
    assert_notification_type,
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


@pytest.fixture(scope="function", name="manager_page")
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
        role=Role.ADMINISTRATOR.id,
        view_status=ViewStatus.TEAM.val,
        status=EmployeeStatus.ACTIVE.val,
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2 and user_3
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
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

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

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

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

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

        # Get user_1, user_2 and user_3
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change role & view status of user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Change role & view status of user_2
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.commit(db_client)

        # Change role & view status of user_3
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.SELF.val)
        user_3.commit(db_client)

        # Get user_4 and user_5
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

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
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_1, user_2])

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

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & is_app_user & status of user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_is_app_user(IsAppUser.ACTIVATE.val)
        user_1.change_status(EmployeeStatus.INACTIVE.val)
        user_1.commit(db_client)

        # Get user_2
        user_2 = employees.get(TestUser.USER_2.val)

        # Change manager and role of user_2
        user_2.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

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
        manager_page.wait_for_manager_table_loading_complete()

        # Assert pagination buttons
        expect(manager_page.get_button_by_number(1)).not_to_have_attribute(
            "aria-current", "page"
        )
        expect(manager_page.manager_page_first_button).to_be_enabled()
        expect(manager_page.manager_page_previous_button).to_be_enabled()
        expect(manager_page.manager_page_next_button).to_be_disabled()
        expect(manager_page.manager_page_last_button).to_be_disabled()

        # Change date range to "This Month"
        manager_page.change_date_range("this-month")

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # TODO: Review and update this assertion logic
        # FIXME: Something broken that needs fixing
        # Assert from date is changed correctly
        # changed_from_date: str = manager_page.get_from_date_value()
        # assert from_date != changed_from_date, (
        #     f"From date not matched.\n"
        #     f"Actual: {changed_from_date}\n"
        #     f"Expected: {from_date}",
        # )

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
    @pytest.mark.skip_db_cleanup
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
        assert_notification_type(manager_page, "warning")

        # Wait for notification to disappear
        manager_page.wait_for_hidden_notification_row()

        # Verify to date is reset to from_date
        assert_date_reset_to_from_date(manager_page, from_date)

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

        # Get user_1, user_2 and user_3
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)

        # Change role & view status for all three users
        for user in [user_1, user_2, user_3]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_4, user_5 and user_6
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_2)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_3)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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
        assert_manager_table_sorted_and_row_count(
            manager_page, [user_1, user_2, user_3]
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3, user_4, user_5, and user_6
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_2)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3, user_4, user_5, and user_6
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_2)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Assert overall manager prodoscore and team distributions
        assert_manager_prodoscore_team_prodoscore_and_team_distributions(
            manager_page, employees, employee_prodoscore_data, day_map
        )

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, and user_4
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_2
        user_2.change_manager(user_1)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(user_1)
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

        # Get user_1 and user_2
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for both users
        for user in [user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3 and user_4
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
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

        # Wait for the manager table to be visible after change date
        manager_page.wait_for_manager_table_loading_complete()

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

        # Get user_1 and user_2
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for both users
        for user in [user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3 and user_4
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
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

        # Wait for the manager table to be visible after change date
        manager_page.wait_for_manager_table_loading_complete()

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Todo: Change from date to to_date

        # Refresh the page to ensure latest data is loaded
        manager_page.refresh_page()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.change_status(Status.HIDDEN.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.change_status(Status.HIDDEN.val)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.change_status(Status.HIDDEN.val)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.change_status(Status.HIDDEN.val)
        user_6.commit(db_client)

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

        # Get login user and user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, and user_4
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)

        # Change manager and role of user_2
        user_2.change_manager(user_1)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(user_1)
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status & status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.TEAM.val)
            user.commit(db_client)

        # Change user_1 manager as login user
        user_1.change_manager(login_user)
        user_1.commit(db_client)

        # Get user_3, user_4, and user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status & status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3, user_4, and user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_2])

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status & status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3, user_4, and user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status & status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3, user_4, user_5, and user_6
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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

        # Change manager and role of user_6
        user_6.change_manager(user_2)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

        # Terminate user_1 and user_5
        user_1.change_role(Role.TERMINATED.id)
        user_1.commit(db_client)

        user_5.change_role(Role.TERMINATED.id)
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
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_2])

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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status & status for all three users
        for user in [login_user, user_1, user_2]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_3, user_4, user_5, and user_6
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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

        # Change manager and role of user_6
        user_6.change_manager(user_2)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

        # Terminate user_1 and user_5
        user_1.change_role(Role.NOT_ACTIVATED.id)
        user_1.commit(db_client)

        user_5.change_role(Role.NOT_ACTIVATED.id)
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
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_2])

        # Use helper for row count and sorting assertion
        assert_manager_prodoscore_and_team_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map
        )

    @pytest.mark.order(24)
    @pytest.mark.manager_page
    def test_click_manager_navigates_to_manager_under_page(
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, and user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Verify navigation to employee under page and back for each employee
        assert_manager_under_page_navigation(
            manager_page,
            employees,
            employee_prodoscore_data,
            day_map,
        )

    @pytest.mark.order(25)
    @pytest.mark.manager_page
    def test_manager_name_sorting_both_directions(
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, and user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by manager name ascending
        expect(manager_page.manager_name_sort_button_down).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(
            manager_page, [login_user, user_1], ascending=True
        )

        # Sort by manager name descending
        manager_page.sort_manager_table_by_manager_name()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by manager name descending
        expect(manager_page.manager_name_sort_button_up).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_and_row_count(
            manager_page, [login_user, user_1], ascending=False
        )

    @pytest.mark.order(26)
    @pytest.mark.manager_page
    def test_prodoscore_sorting_ascending_and_descending(
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, and user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Sort by prodoscore ascending
        manager_page.sort_manager_table_by_prodoscore()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by prodoscore ascending
        expect(manager_page.prodoscore_sort_button_down).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_by_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map, ascending=True
        )

        # Sort by prodoscore descending
        manager_page.sort_manager_table_by_prodoscore()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by prodoscore descending
        expect(manager_page.prodoscore_sort_button_up).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_by_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map, ascending=False
        )

    @pytest.mark.order(27)
    @pytest.mark.manager_page
    def test_direct_team_prodoscore_sorting_ascending_and_descending(
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, and user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Sort by direct team prodoscore ascending
        manager_page.sort_manager_table_by_direct_team_prodoscore()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by direct team prodoscore ascending
        expect(manager_page.direct_team_prodoscore_sort_button_down).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_by_direct_team_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map, ascending=True
        )

        # Sort by direct team prodoscore descending
        manager_page.sort_manager_table_by_direct_team_prodoscore()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by direct team prodoscore descending
        expect(manager_page.direct_team_prodoscore_sort_button_up).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_by_direct_team_prodoscore(
            manager_page, employees, employee_prodoscore_data, day_map, ascending=False
        )

    @pytest.mark.order(28)
    @pytest.mark.manager_page
    def test_percent_change_column_sorts_ascending_and_descending(
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

        # Get login user and user_1
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for both users
        for user in [login_user, user_1]:
            user.change_role(Role.ADMINISTRATOR.id)
            user.change_view_status(ViewStatus.COMPANY.val)
            user.commit(db_client)

        # Get user_2, user_3, user_4, user_5, and user_6
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)
        user_6 = employees.get(TestUser.USER_6.val)

        # Change manager and role of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.commit(db_client)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.MANAGER.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_1)
        user_5.change_role(Role.MANAGER.id)
        user_5.commit(db_client)

        # Change manager and role of user_6
        user_6.change_manager(user_1)
        user_6.change_role(Role.MANAGER.id)
        user_6.commit(db_client)

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

        # Sort by percentage change ascending
        manager_page.sort_manager_table_by_percent_change()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by percentage change ascending
        expect(manager_page.percent_change_sort_button_down).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_by_percentage_change(
            manager_page, employees, employee_prodoscore_data, day_map, ascending=True
        )

        # Sort by percentage change descending
        manager_page.sort_manager_table_by_percent_change()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify sorting by percentage change descending
        expect(manager_page.percent_change_sort_button_up).to_be_visible()

        # Use helper for row count and sorting assertion
        assert_manager_table_sorted_by_percentage_change(
            manager_page, employees, employee_prodoscore_data, day_map, ascending=False
        )

    @pytest.mark.order(29)
    @pytest.mark.manager_page
    def test_sorting_from_any_page_returns_to_first_page(
        self,
        domain,
        pagination_users,
        manager_page,
        db_client,
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
        manager_page.wait_for_manager_table_loading_complete()

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
        manager_page.wait_for_manager_table_loading_complete()

        # Assert pagination buttons
        expect(manager_page.get_button_by_number(1)).not_to_have_attribute(
            "aria-current", "page"
        )
        expect(manager_page.manager_page_first_button).to_be_enabled()
        expect(manager_page.manager_page_previous_button).to_be_enabled()
        expect(manager_page.manager_page_next_button).to_be_disabled()
        expect(manager_page.manager_page_last_button).to_be_disabled()

        # Sort by manager name to reset pagination
        manager_page.sort_manager_table_by_manager_name()

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

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

    @pytest.mark.order(30)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_department_filter_search_and_multiselect_functionality(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status and department for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.change_department(Department.ADMINISTRATION.id)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_department(Department.AUDIT.id)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.change_department(Department.FINANCE.id)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Search administration department in the dropdown
        manager_page.search_department(Department.ADMINISTRATION.name_str)

        # Wait for search complete
        manager_page.wait_for_department_search_complete()

        # Unselect select all departments
        manager_page.click_department_select_all()

        # Select the "Administration" department
        manager_page.select_department_by_name(Department.ADMINISTRATION.name_str)

        # Clear the search field
        manager_page.clear_department_search()

        # Search audit department in the dropdown
        manager_page.search_department(Department.AUDIT.name_str)

        # Wait for search complete
        manager_page.wait_for_department_search_complete()

        # Select the "Audit" department
        manager_page.select_department_by_name(Department.AUDIT.name_str)

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

    @pytest.mark.order(31)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_department_filter_shows_only_managers_in_selected_departments(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status and department for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.change_department(Department.ADMINISTRATION.id)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_department(Department.AUDIT.id)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.change_department(Department.FINANCE.id)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Search finance department in the dropdown
        manager_page.search_department(Department.FINANCE.name_str)

        # Wait for search complete
        manager_page.wait_for_department_search_complete()

        # Unselect select all departments
        manager_page.click_department_select_all()

        # Select the "Finance" department
        manager_page.select_department_by_name(Department.FINANCE.name_str)

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_2])

    @pytest.mark.order(32)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_department_filter_placeholder_shows_selection_before_and_after_apply(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status and department for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.change_department(Department.ADMINISTRATION.id)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_department(Department.AUDIT.id)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.change_department(Department.FINANCE.id)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Unselect select all departments
        manager_page.click_department_select_all()

        # Search administration department in the dropdown
        manager_page.search_department(Department.ADMINISTRATION.name_str)

        # Wait for search complete
        manager_page.wait_for_department_search_complete()

        # Select the "Administration" department
        manager_page.select_department_by_name(Department.ADMINISTRATION.name_str)

        # Clear the search field
        manager_page.clear_department_search()

        # Search audit department in the dropdown
        manager_page.search_department(Department.AUDIT.name_str)

        # Wait for search complete
        manager_page.wait_for_department_search_complete()

        # Select the "Audit" department
        manager_page.select_department_by_name(Department.AUDIT.name_str)

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Validate placeholder text before applying filter (dropdown closed, selections made)
        selected_depts = [Department.ADMINISTRATION.name_str, Department.AUDIT.name_str]
        placeholder_before_apply = (
            manager_page.get_department_dropdown_placeholder_text()
        )
        assert_filters_placeholder(
            placeholder_before_apply, selected_depts, state="before_apply"
        )

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Validate placeholder text after applying filter (filter applied to table)
        placeholder_after_apply = (
            manager_page.get_department_dropdown_placeholder_text()
        )
        assert_filters_placeholder(
            placeholder_after_apply, selected_depts, state="after_apply"
        )

    @pytest.mark.order(33)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_deselecting_department_select_all_disables_apply_button_and_clears_other_filters(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status and department for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.change_department(Department.ADMINISTRATION.id)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_department(Department.AUDIT.id)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.change_department(Department.FINANCE.id)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Assert filter controls are enabled
        expect(manager_page.apply_button).to_be_enabled()
        expect(manager_page.role_dropdown_options).to_be_enabled()
        expect(manager_page.manager_dropdown_options).to_be_enabled()
        expect(manager_page.employee_dropdown_options).to_be_enabled()

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Unselect select all departments
        manager_page.click_department_select_all()

        # Assert filter controls are disabled
        expect(manager_page.apply_button).to_be_disabled()
        expect(manager_page.role_dropdown_options).to_be_disabled()
        expect(manager_page.manager_dropdown_options).to_be_disabled()
        expect(manager_page.employee_dropdown_options).to_be_disabled()

    @pytest.mark.order(34)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_app_user_department_appears_when_manager_is_valid_and_visible(
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

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & is_app_user & status & department of user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_is_app_user(IsAppUser.ACTIVATE.val)
        # user_1.change_status(EmployeeStatus.INACTIVE.val)
        user_1.change_department(Department.AUDIT.id)
        user_1.commit(db_client)

        # Get user_2
        user_2 = employees.get(TestUser.USER_2.val)

        # Change manager and role of user_2
        user_2.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()

        # Search administration department in the dropdown
        manager_page.search_department(Department.AUDIT.name_str)

        # Wait for search complete
        manager_page.wait_for_department_search_complete()

        # Verify audit department is shown in the search results
        assert Department.AUDIT.name_str in manager_page.get_department_result_names()

    @pytest.mark.order(35)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_role_filter_search_and_multiselect_functionality(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.MANAGER.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.CONTRACTOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Unselect select all roles
        manager_page.click_role_select_all()

        # Search administrators role in the dropdown
        manager_page.search_role(Role.ADMINISTRATOR.name_str)

        # Wait for search complete
        manager_page.wait_for_role_search_complete()

        # Select the "Administrators" role
        manager_page.select_role_by_name(Role.ADMINISTRATOR.name_str)

        # Clear the search field
        manager_page.clear_role_search()

        # Search manager role in the dropdown
        manager_page.search_role(Role.MANAGER.name_str)

        # Wait for search complete
        manager_page.wait_for_role_search_complete()

        # Select the "Managers" role
        manager_page.select_role_by_name(Role.MANAGER.name_str)

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying role filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

    @pytest.mark.order(36)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_role_filter_shows_only_managers_in_selected_roles(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.MANAGER.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.CONTRACTOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
        user_3.change_role(Role.SALES.id)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_1)
        user_4.change_role(Role.SALES.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_2)
        user_5.change_role(Role.SALES.id)
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

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Unselect select all roles
        manager_page.click_role_select_all()

        # Search manager role in the dropdown
        manager_page.search_role(Role.MANAGER.name_str)

        # Wait for search complete
        manager_page.wait_for_role_search_complete()

        # Select the "Manager" role
        manager_page.select_role_by_name(Role.MANAGER.name_str)

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying role filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_1])

    @pytest.mark.order(37)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_role_filter_placeholder_shows_selection_before_and_after_apply(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.MANAGER.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.CONTRACTOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Unselect select all roles
        manager_page.click_role_select_all()

        # Search administrator role in the dropdown
        manager_page.search_role(Role.ADMINISTRATOR.name_str)

        # Wait for search complete
        manager_page.wait_for_role_search_complete()

        # Select the "Administrator" role
        manager_page.select_role_by_name(Role.ADMINISTRATOR.name_str)

        # Clear the search field
        manager_page.clear_role_search()

        # Search manager role in the dropdown
        manager_page.search_role(Role.MANAGER.name_str)

        # Wait for search complete
        manager_page.wait_for_role_search_complete()

        # Select the "Manager" role
        manager_page.select_role_by_name(Role.MANAGER.name_str)

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Validate placeholder text before applying filter (dropdown closed, selections made)
        selected_roles = [Role.ADMINISTRATOR.name_str, Role.MANAGER.name_str]
        placeholder_before_apply = manager_page.get_role_dropdown_placeholder_text()
        assert_filters_placeholder(
            placeholder_before_apply, selected_roles, state="before_apply"
        )

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying role filter
        manager_page.wait_for_manager_table_loading_complete()

        # Validate placeholder text after applying filter (filter applied to table)
        placeholder_after_apply = manager_page.get_role_dropdown_placeholder_text()
        assert_filters_placeholder(
            placeholder_after_apply, selected_roles, state="after_apply"
        )

    @pytest.mark.order(38)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_deselecting_role_select_all_disables_apply_button_and_clears_other_filters(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.MANAGER.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.CONTRACTOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Assert filter controls are enabled
        expect(manager_page.apply_button).to_be_enabled()
        expect(manager_page.department_dropdown_options).to_be_enabled()
        expect(manager_page.manager_dropdown_options).to_be_enabled()
        expect(manager_page.employee_dropdown_options).to_be_enabled()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Unselect select all roles
        manager_page.click_role_select_all()

        # Assert filter controls are disabled
        expect(manager_page.apply_button).to_be_disabled()
        expect(manager_page.department_dropdown_options).to_be_disabled()
        expect(manager_page.manager_dropdown_options).to_be_disabled()
        expect(manager_page.employee_dropdown_options).to_be_disabled()

    @pytest.mark.order(39)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_app_user_role_appears_when_manager_is_valid_and_visible(
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

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & is_app_user & status of user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_is_app_user(IsAppUser.ACTIVATE.val)
        # user_1.change_status(EmployeeStatus.INACTIVE.val)
        user_1.commit(db_client)

        # Get user_2
        user_2 = employees.get(TestUser.USER_2.val)

        # Change manager and role of user_2
        user_2.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()

        # Search administrator role in the dropdown
        manager_page.search_role(Role.ADMINISTRATOR.name_str)

        # Wait for search complete
        manager_page.wait_for_role_search_complete()

        # Verify administrator role is shown in the search results
        assert Role.ADMINISTRATOR.name_str in manager_page.get_role_result_names()

    @pytest.mark.order(40)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_employee_filter_search_and_multiselect_functionality(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Unselect select all employees
        manager_page.click_employee_select_all()

        # Search login user employee in the dropdown
        manager_page.search_employee(login_user.full_name)

        # Wait for search complete
        manager_page.wait_for_employee_search_complete()

        # Select the login user employee
        manager_page.select_employee_by_name(login_user.full_name)

        # Clear the search field
        manager_page.clear_employee_search()

        # Search user 1 employee in the dropdown
        manager_page.search_employee(user_1.full_name)

        # Wait for search complete
        manager_page.wait_for_employee_search_complete()

        # Select the user 1 employee
        manager_page.select_employee_by_name(user_1.full_name)

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [login_user, user_1])

    @pytest.mark.order(41)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_employee_filter_shows_only_selected_managers(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Unselect select all employees
        manager_page.click_employee_select_all()

        # Search user 2 employee in the dropdown
        manager_page.search_employee(user_2.full_name)

        # Wait for search complete
        manager_page.wait_for_employee_search_complete()

        # Select the user 2 employee
        manager_page.select_employee_by_name(user_2.full_name)

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_2])

    @pytest.mark.order(42)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_employee_filter_placeholder_shows_selection_before_and_after_apply(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Unselect select all employees
        manager_page.click_employee_select_all()

        # Search login user employee in the dropdown
        manager_page.search_employee(login_user.full_name)

        # Wait for search complete
        manager_page.wait_for_employee_search_complete()

        # Select the login user employee
        manager_page.select_employee_by_name(login_user.full_name)

        # Clear the search field
        manager_page.clear_employee_search()

        # Search user_1 employee in the dropdown
        manager_page.search_employee(user_1.full_name)

        # Wait for search complete
        manager_page.wait_for_employee_search_complete()

        # Select the user_1 employee
        manager_page.select_employee_by_name(user_1.full_name)

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Validate placeholder text before applying filter (dropdown closed, selections made)
        selected_employees = [login_user.full_name, user_1.full_name]
        placeholder_before_apply = manager_page.get_employee_dropdown_placeholder_text()
        assert_filters_placeholder(
            placeholder_before_apply, selected_employees, state="before_apply"
        )

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Validate placeholder text after applying filter (filter applied to table)
        placeholder_after_apply = manager_page.get_employee_dropdown_placeholder_text()
        assert_filters_placeholder(
            placeholder_after_apply, selected_employees, state="after_apply"
        )

    @pytest.mark.order(43)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_deselecting_employee_select_all_in_employee_filter_disables_other_filters(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)
        user_2 = employees.get(TestUser.USER_2.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        user_2.change_role(Role.ADMINISTRATOR.id)
        user_2.change_view_status(ViewStatus.COMPANY.val)
        user_2.commit(db_client)

        # Get user_3, user_4, user_5
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager and role of user_3
        user_3.change_manager(login_user)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Assert filter controls are enabled
        expect(manager_page.apply_button).to_be_enabled()
        expect(manager_page.department_dropdown_options).to_be_enabled()
        expect(manager_page.role_dropdown_options).to_be_enabled()
        expect(manager_page.manager_dropdown_options).to_be_enabled()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Unselect select all employees
        manager_page.click_employee_select_all()

        # Assert filter controls are disabled
        expect(manager_page.apply_button).to_be_disabled()
        expect(manager_page.department_dropdown_options).to_be_enabled()
        expect(manager_page.role_dropdown_options).to_be_disabled()
        expect(manager_page.manager_dropdown_options).to_be_disabled()

    @pytest.mark.order(44)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_app_user_employee_appears_when_manager_is_valid_and_visible(
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

        # Get user_1
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status & is_app_user & status of user_1
        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_is_app_user(IsAppUser.ACTIVATE.val)
        # user_1.change_status(EmployeeStatus.INACTIVE.val)
        user_1.commit(db_client)

        # Get user_2
        user_2 = employees.get(TestUser.USER_2.val)

        # Change manager and role of user_2
        user_2.change_manager(user_1)
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
        manager_page.wait_for_manager_table_loading_complete()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()

        # Search user_1 employee in the dropdown
        manager_page.search_employee(user_1.full_name)

        # Wait for search complete
        manager_page.wait_for_employee_search_complete()

        # Verify user_1 employee is shown in the search results
        assert user_1.full_name in manager_page.get_employee_result_names()

    @pytest.mark.order(45)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_manager_filter_search_and_multiselect_functionality(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Unselect select all managers
        manager_page.click_manager_select_all()

        # Search login user manager in the dropdown
        manager_page.search_manager(login_user.full_name)

        # Wait for search complete
        manager_page.wait_for_manager_search_complete()

        # Select the login user manager
        manager_page.select_manager_by_name(login_user.full_name)

        # Clear the search field
        manager_page.clear_manager_search()

        # Search user 1 manager in the dropdown
        manager_page.search_manager(user_1.full_name)

        # Wait for search complete
        manager_page.wait_for_manager_search_complete()

        # Select the user 1 manager
        manager_page.select_manager_by_name(user_1.full_name)

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_2, user_3])

    @pytest.mark.order(46)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_manager_filter_shows_only_selected_managers(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Unselect select all managers
        manager_page.click_manager_select_all()

        # Search login user manager in the dropdown
        manager_page.search_manager(login_user.full_name)

        # Wait for search complete
        manager_page.wait_for_manager_search_complete()

        # Select the login user manager
        manager_page.select_manager_by_name(login_user.full_name)

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_2])

    @pytest.mark.order(47)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_manager_filter_placeholder_shows_selection_before_and_after_apply(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Unselect select all managers
        manager_page.click_manager_select_all()

        # Search login user manager in the dropdown
        manager_page.search_manager(login_user.full_name)

        # Wait for search complete
        manager_page.wait_for_manager_search_complete()

        # Select the login user manager
        manager_page.select_manager_by_name(login_user.full_name)

        # Clear the search field
        manager_page.clear_manager_search()

        # Search user 1 manager in the dropdown
        manager_page.search_manager(user_1.full_name)

        # Wait for search complete
        manager_page.wait_for_manager_search_complete()

        # Select the user 1 manager
        manager_page.select_manager_by_name(user_1.full_name)

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Validate placeholder text before applying filter (dropdown closed, selections made)
        selected_managers = [login_user.full_name, user_1.full_name]
        placeholder_before_apply = manager_page.get_manager_dropdown_placeholder_text()
        assert_filters_placeholder(
            placeholder_before_apply, selected_managers, state="before_apply"
        )

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying department filter
        manager_page.wait_for_manager_table_loading_complete()

        # Validate placeholder text after applying filter (filter applied to table)
        placeholder_after_apply = manager_page.get_manager_dropdown_placeholder_text()
        assert_filters_placeholder(
            placeholder_after_apply, selected_managers, state="after_apply"
        )

    @pytest.mark.order(48)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_deselecting_manager_select_all_disables_apply_button_and_clears_other_filters(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Assert filter controls are enabled
        expect(manager_page.apply_button).to_be_enabled()
        expect(manager_page.department_dropdown_options).to_be_enabled()
        expect(manager_page.role_dropdown_options).to_be_enabled()
        expect(manager_page.employee_dropdown_options).to_be_enabled()

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Unselect select all managers
        manager_page.click_manager_select_all()

        # Assert filter controls are disabled
        expect(manager_page.apply_button).to_be_disabled()
        expect(manager_page.department_dropdown_options).to_be_disabled()
        expect(manager_page.role_dropdown_options).to_be_disabled()
        expect(manager_page.employee_dropdown_options).to_be_disabled()

    @pytest.mark.order(49)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_app_user_manager_appears_when_manager_is_valid_and_visible(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.change_is_app_user(IsAppUser.ACTIVATE.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()

        # Search user_1 manager in the dropdown
        manager_page.search_manager(user_1.full_name)

        # Wait for search complete
        manager_page.wait_for_manager_search_complete()

        # Verify user_1 manager is shown in the search results
        assert user_1.full_name in manager_page.get_manager_result_names()

    @pytest.mark.order(50)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_no_network_request_sent_before_apply_button_clicked(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change department, manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.change_department(Department.AUDIT.id)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Start monitoring ALL requests (no pattern = capture everything)
        manager_page.start_request_monitoring()

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()
        manager_page.click_department_select_all()
        manager_page.search_department(Department.AUDIT.name_str)
        manager_page.wait_for_department_search_complete()
        manager_page.select_department_by_name(Department.AUDIT.name_str)
        manager_page.department_dropdown_arrow.click()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()
        manager_page.click_role_select_all()
        manager_page.search_role(Role.MANAGER.name_str)
        manager_page.wait_for_role_search_complete()
        manager_page.select_role_by_name(Role.MANAGER.name_str)
        manager_page.role_dropdown_arrow.click()

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()
        manager_page.click_manager_select_all()
        manager_page.search_manager(login_user.full_name)
        manager_page.wait_for_manager_search_complete()
        manager_page.select_manager_by_name(login_user.full_name)
        manager_page.manager_dropdown_arrow.click()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()
        manager_page.click_employee_select_all()
        manager_page.search_employee(user_2.full_name)
        manager_page.wait_for_employee_search_complete()
        manager_page.select_employee_by_name(user_2.full_name)
        manager_page.employee_dropdown_arrow.click()

        # Validate number of requests before applying filter
        request_count_before_apply = manager_page.get_request_count(
            "**/api/v2/dashboard/employees**"
        )
        assert request_count_before_apply == 0, (
            f"Request count mismatch before applying manager filter.\n"
            f"Actual: {request_count_before_apply}\n"
            f"Expected: 0"
        )

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying manager filter
        manager_page.wait_for_manager_table_loading_complete()

        # Clean up
        manager_page.stop_request_monitoring()

        # Verify row count and sorting
        assert_manager_table_sorted_and_row_count(manager_page, [user_2])

    @pytest.mark.order(51)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_no_results_message_displayed_when_filters_return_no_matches(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change department, manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.change_department(Department.AUDIT.id)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()
        manager_page.click_department_select_all()
        manager_page.search_department(Department.AUDIT.name_str)
        manager_page.wait_for_department_search_complete()
        manager_page.select_department_by_name(Department.AUDIT.name_str)
        manager_page.department_dropdown_arrow.click()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()
        manager_page.click_role_select_all()
        manager_page.search_role(Role.MANAGER.name_str)
        manager_page.wait_for_role_search_complete()
        manager_page.select_role_by_name(Role.MANAGER.name_str)
        manager_page.role_dropdown_arrow.click()

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()
        manager_page.click_manager_select_all()
        manager_page.search_manager(user_2.full_name)
        manager_page.wait_for_manager_search_complete()
        manager_page.select_manager_by_name(user_2.full_name)
        manager_page.manager_dropdown_arrow.click()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()
        manager_page.click_employee_select_all()
        manager_page.search_employee(user_2.full_name)
        manager_page.wait_for_employee_search_complete()
        manager_page.select_employee_by_name(user_2.full_name)
        manager_page.employee_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying manager filter
        manager_page.wait_for_no_data_for_selected_filters()

        # Verify no data message and image is shown when there is no data
        expect(manager_page.no_data_for_selected_filters).to_be_visible()
        expect(manager_page.no_data_found_image).to_be_visible()

    @pytest.mark.order(52)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_filter_dropdown_search_results_cleared_after_apply_button_clicked(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change department, manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.change_department(Department.AUDIT.id)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()
        manager_page.click_department_select_all()
        manager_page.search_department(Department.AUDIT.name_str)
        manager_page.wait_for_department_search_complete()
        manager_page.select_department_by_name(Department.AUDIT.name_str)
        manager_page.department_dropdown_arrow.click()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()
        manager_page.click_role_select_all()
        manager_page.search_role(Role.MANAGER.name_str)
        manager_page.wait_for_role_search_complete()
        manager_page.select_role_by_name(Role.MANAGER.name_str)
        manager_page.role_dropdown_arrow.click()

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()
        manager_page.click_manager_select_all()
        manager_page.search_manager(login_user.full_name)
        manager_page.wait_for_manager_search_complete()
        manager_page.select_manager_by_name(login_user.full_name)
        manager_page.manager_dropdown_arrow.click()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()
        manager_page.click_employee_select_all()
        manager_page.search_employee(user_2.full_name)
        manager_page.wait_for_employee_search_complete()
        manager_page.select_employee_by_name(user_2.full_name)
        manager_page.employee_dropdown_arrow.click()

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying manager filter
        manager_page.wait_for_manager_table_loading_complete()

        # Click department select dropdown arrow and verify no departments are selected
        manager_page.department_dropdown_arrow.click()
        assert len(manager_page.get_department_result_names()) == 0, (
            f"Department dropdown should be empty after filters.\n"
            f"Actual: {manager_page.get_department_result_names()}\n"
            f"Expected: []"
        )

        # Click role select dropdown arrow and verify no roles are selected
        manager_page.role_dropdown_arrow.click()
        assert len(manager_page.get_role_result_names()) == 0, (
            f"Role dropdown should be empty after filters.\n"
            f"Actual: {manager_page.get_role_result_names()}\n"
            f"Expected: []"
        )

        # Click manager select dropdown arrow and verify no managers are selected
        manager_page.manager_dropdown_arrow.click()
        assert len(manager_page.get_manager_result_names()) == 0, (
            f"Manager dropdown should be empty after filters.\n"
            f"Actual: {manager_page.get_manager_result_names()}\n"
            f"Expected: []"
        )

        # Click employee select dropdown arrow and verify no employees are selected
        manager_page.employee_dropdown_arrow.click()
        assert len(manager_page.get_employee_result_names()) == 0, (
            f"Employee dropdown should be empty after filters.\n"
            f"Actual: {manager_page.get_employee_result_names()}\n"
            f"Expected: []"
        )

    @pytest.mark.order(53)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_all_filters_placeholder_shows_single_selection_before_and_after_apply(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change department, manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.change_department(Department.AUDIT.id)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()
        manager_page.click_department_select_all()
        manager_page.search_department(Department.AUDIT.name_str)
        manager_page.wait_for_department_search_complete()
        manager_page.select_department_by_name(Department.AUDIT.name_str)
        manager_page.department_dropdown_arrow.click()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()
        manager_page.click_role_select_all()
        manager_page.search_role(Role.MANAGER.name_str)
        manager_page.wait_for_role_search_complete()
        manager_page.select_role_by_name(Role.MANAGER.name_str)
        manager_page.role_dropdown_arrow.click()

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()
        manager_page.click_manager_select_all()
        manager_page.search_manager(login_user.full_name)
        manager_page.wait_for_manager_search_complete()
        manager_page.select_manager_by_name(login_user.full_name)
        manager_page.manager_dropdown_arrow.click()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()
        manager_page.click_employee_select_all()
        manager_page.search_employee(login_user.full_name)
        manager_page.wait_for_employee_search_complete()
        manager_page.select_employee_by_name(login_user.full_name)
        manager_page.employee_dropdown_arrow.click()

        # Validate placeholder text in department dropdown before applying filter (dropdown closed, selections made)
        selected_department = Department.AUDIT.name_str
        placeholder_before_apply = (
            manager_page.get_department_dropdown_placeholder_text()
        )
        assert selected_department == placeholder_before_apply, (
            f"Department placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_before_apply}\n"
            f"Expected: {selected_department}"
        )

        # Validate placeholder text in role dropdown before applying filter (dropdown closed, selections made)
        selected_role = Role.MANAGER.name_str
        placeholder_before_apply = manager_page.get_role_dropdown_placeholder_text()
        assert selected_role == placeholder_before_apply, (
            f"Role placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_before_apply}\n"
            f"Expected: {selected_role}"
        )

        # Validate placeholder text in manager dropdown before applying filter (dropdown closed, selections made)
        selected_manager = login_user.full_name
        placeholder_before_apply = manager_page.get_manager_dropdown_placeholder_text()
        assert selected_manager == placeholder_before_apply, (
            f"Manager placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_before_apply}\n"
            f"Expected: {selected_manager}"
        )

        # Validate placeholder text in employee dropdown before applying filter (dropdown closed, selections made)
        selected_employee = login_user.full_name
        placeholder_before_apply = manager_page.get_employee_dropdown_placeholder_text()
        assert selected_employee == placeholder_before_apply, (
            f"Employee placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_before_apply}\n"
            f"Expected: {selected_employee}"
        )

        # Click apply button
        manager_page.apply_button.click()

        # Wait for the manager table to be visible after applying manager filter
        manager_page.wait_for_manager_table_loading_complete()

        # Validate placeholder text in department dropdown after applying filter
        placeholder_after_apply = (
            manager_page.get_department_dropdown_placeholder_text()
        )
        assert selected_department == placeholder_after_apply, (
            f"Department placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_after_apply}\n"
            f"Expected: {selected_department}"
        )

        # Validate placeholder text in role dropdown after applying filter
        placeholder_after_apply = manager_page.get_role_dropdown_placeholder_text()
        assert selected_role == placeholder_after_apply, (
            f"Role placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_after_apply}\n"
            f"Expected: {selected_role}"
        )

        # Validate placeholder text in manager dropdown after applying filter
        placeholder_after_apply = manager_page.get_manager_dropdown_placeholder_text()
        assert selected_manager == placeholder_after_apply, (
            f"Manager placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_after_apply}\n"
            f"Expected: {selected_manager}"
        )

        # Validate placeholder text in employee dropdown after applying filter
        placeholder_after_apply = manager_page.get_employee_dropdown_placeholder_text()
        assert selected_employee == placeholder_after_apply, (
            f"Employee placeholder mismatch after applying filters.\n"
            f"Actual: {placeholder_after_apply}\n"
            f"Expected: {selected_employee}"
        )

    @pytest.mark.order(54)
    @pytest.mark.manager_page
    @pytest.mark.manager_page_filters
    def test_reset_button_returns_filters_and_sort_to_default_but_preserves_date_range(
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

        # Get login user, user_1 and user_2
        login_user = employees.get(TestUser.LOGIN_USER.val)
        user_1 = employees.get(TestUser.USER_1.val)

        # Change role & view status for all three users
        login_user.change_role(Role.ADMINISTRATOR.id)
        login_user.change_view_status(ViewStatus.COMPANY.val)
        login_user.commit(db_client)

        user_1.change_role(Role.ADMINISTRATOR.id)
        user_1.change_view_status(ViewStatus.COMPANY.val)
        user_1.commit(db_client)

        # Get user_2, user_3, user_4, user_5
        user_2 = employees.get(TestUser.USER_2.val)
        user_3 = employees.get(TestUser.USER_3.val)
        user_4 = employees.get(TestUser.USER_4.val)
        user_5 = employees.get(TestUser.USER_5.val)

        # Change department, manager, role and view status of user_2
        user_2.change_manager(login_user)
        user_2.change_role(Role.MANAGER.id)
        user_2.change_view_status(ViewStatus.TEAM.val)
        user_2.change_department(Department.AUDIT.id)
        user_2.commit(db_client)

        # Change manager, role and view status of user_3
        user_3.change_manager(user_1)
        user_3.change_role(Role.MANAGER.id)
        user_3.change_view_status(ViewStatus.TEAM.val)
        user_3.commit(db_client)

        # Change manager and role of user_4
        user_4.change_manager(user_2)
        user_4.change_role(Role.MANAGER.id)
        user_4.commit(db_client)

        # Change manager and role of user_5
        user_5.change_manager(user_3)
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

        # Change from date to current date
        manager_page.change_from_date(current_date)

        # Wait for the manager table to be visible after refresh
        manager_page.wait_for_manager_table_loading_complete()

        # Verify from date is set correctly
        from_date_value = manager_page.get_from_date_value()
        assert from_date_value == current_date, (
            f"From date value mismatch after setting from date.\n"
            f"Actual: {from_date_value}\n"
            f"Expected: {current_date}"
        )

        # Sort by manager name descending
        manager_page.sort_manager_table_by_manager_name()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify reset the sorting (manager name descending)
        expect(manager_page.manager_name_sort_button_up).to_be_visible()
        assert_manager_table_sorted_and_row_count(
            manager_page, [login_user, user_1, user_2, user_3], ascending=False
        )

        # Click department select dropdown arrow
        manager_page.department_dropdown_arrow.click()
        manager_page.click_department_select_all()
        manager_page.search_department(Department.AUDIT.name_str)
        manager_page.wait_for_department_search_complete()
        manager_page.select_department_by_name(Department.AUDIT.name_str)
        manager_page.department_dropdown_arrow.click()

        # Click role select dropdown arrow
        manager_page.role_dropdown_arrow.click()
        manager_page.click_role_select_all()
        manager_page.search_role(Role.MANAGER.name_str)
        manager_page.wait_for_role_search_complete()
        manager_page.select_role_by_name(Role.MANAGER.name_str)
        manager_page.role_dropdown_arrow.click()

        # Click manager select dropdown arrow
        manager_page.manager_dropdown_arrow.click()
        manager_page.click_manager_select_all()
        manager_page.search_manager(login_user.full_name)
        manager_page.wait_for_manager_search_complete()
        manager_page.select_manager_by_name(login_user.full_name)
        manager_page.manager_dropdown_arrow.click()

        # Click employee select dropdown arrow
        manager_page.employee_dropdown_arrow.click()
        manager_page.click_employee_select_all()
        manager_page.search_employee(user_2.full_name)
        manager_page.wait_for_employee_search_complete()
        manager_page.select_employee_by_name(user_2.full_name)
        manager_page.employee_dropdown_arrow.click()

        # Click Reset button
        manager_page.reset_button.click()

        # Wait for the manager table to be visible after sorting
        manager_page.wait_for_manager_table_loading_complete()

        # Verify from date is not reset after reset filter
        new_from_date_value = manager_page.get_from_date_value()
        assert new_from_date_value == current_date, (
            f"From date value mismatch after setting from date.\n"
            f"Actual: {new_from_date_value}\n"
            f"Expected: {current_date}"
        )

        # Verify reset the sorting to default (manager name ascending)
        expect(manager_page.manager_name_sort_button_down).to_be_visible()
        assert_manager_table_sorted_and_row_count(
            manager_page, [login_user, user_1, user_2, user_3], ascending=True
        )

        # Validate placeholder text in department dropdown after reset filter
        placeholder_after_reset = (
            manager_page.get_department_dropdown_placeholder_text()
        )
        assert "All Departments" == placeholder_after_reset, (
            f"Department placeholder mismatch after reset filter.\n"
            f"Actual: {placeholder_after_reset}\n"
            f"Expected: All Departments"
        )

        # Validate placeholder text in role dropdown after reset filter
        placeholder_after_reset = manager_page.get_role_dropdown_placeholder_text()
        assert "All Roles" == placeholder_after_reset, (
            f"Role placeholder mismatch after reset filter.\n"
            f"Actual: {placeholder_after_reset}\n"
            f"Expected: All Roles"
        )

        # Validate placeholder text in manager dropdown after reset filter
        placeholder_after_reset = manager_page.get_manager_dropdown_placeholder_text()
        assert "All Managers" == placeholder_after_reset, (
            f"Manager placeholder mismatch after reset filter.\n"
            f"Actual: {placeholder_after_reset}\n"
            f"Expected: All Managers"
        )

        # Validate placeholder text in employee dropdown after reset filter
        placeholder_after_reset = manager_page.get_employee_dropdown_placeholder_text()
        assert "All Employees" == placeholder_after_reset, (
            f"Employee placeholder mismatch after reset filter.\n"
            f"Actual: {placeholder_after_reset}\n"
            f"Expected: All Employees"
        )
