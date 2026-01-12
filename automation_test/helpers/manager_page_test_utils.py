"""
Helper functions for manager page test assertions.
"""

from playwright.sync_api import expect

from automation_test.utils.employee_data_helper import (
    calculate_percent_change,
    get_average_score,
    get_average_score_without_rounding,
    get_expected_team_distribution_tooltip,
    get_team_distribution_bars,
    score_to_color,
)


def assert_manager_prodoscore_team_scores_and_percentage_change(
    manager_page, employees, employee_prodoscore_data, day_map
):
    """
    Assert manager and team prodoscore and percentage change for all employees.
    Args:
        manager_page: The page object with table accessors.
        employees: Dict of employee objects keyed by id.
        employee_prodoscore_data: Nested dict of prodoscore data.
        day_map: Dict mapping week keys to day keys.
        get_average_score: Function to compute average score (with rounding).
        score_to_color: Function to map score to color.
        get_average_score_without_rounding: Function to compute average score (no rounding).
        calculate_percent_change: Function to compute percent change.
    """
    for key, employee in employees.items():
        prev_self_scores = [
            employee_prodoscore_data.get("previous_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("previous_week", {})
        ]
        curr_self_scores = [
            employee_prodoscore_data.get("current_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("current_week", {})
        ]
        if not any(prev_self_scores) and not any(curr_self_scores):
            continue

        manager_data = manager_page.get_manager_data(employee.full_name)

        # Validate manager's prodoscore for current week
        expected_prodoscore = get_average_score(curr_self_scores)
        expected_prodoscore_color = score_to_color(expected_prodoscore)
        actual_prodoscore = manager_data.get("prodoscore").get("score")
        actual_prodoscore_color = manager_data.get("prodoscore").get("color")
        assert actual_prodoscore == expected_prodoscore, (
            f"Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore}\n"
            f"Expected: {expected_prodoscore}"
        )
        assert actual_prodoscore_color == expected_prodoscore_color, (
            f"Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore_color}\n"
            f"Expected: {expected_prodoscore_color}"
        )

        # Validate percentage change in team prodoscore
        prev_week_scores = []
        curr_week_scores = []

        for day_key in day_map.get("previous_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("previous_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            scores = [sub["score"] for sub in subordinates.values()]
            if scores:
                prev_week_scores.append(get_average_score_without_rounding(scores))

        for day_key in day_map.get("current_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("current_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            scores = [sub["score"] for sub in subordinates.values()]
            if scores:
                curr_week_scores.append(get_average_score_without_rounding(scores))

        prev_week_avg = (
            get_average_score_without_rounding(prev_week_scores)
            if prev_week_scores
            else None
        )
        curr_week_avg = (
            get_average_score_without_rounding(curr_week_scores)
            if curr_week_scores
            else None
        )

        expected_percentage_change = calculate_percent_change(
            prev_week_avg, curr_week_avg
        )
        actual_percentage_change = manager_data.get("percent_change")

        assert actual_percentage_change == expected_percentage_change, (
            f"Percentage change mismatch for {employee.full_name}.\n"
            f"Actual: {actual_percentage_change}\n"
            f"Expected: {expected_percentage_change}"
        )

        # Validate team prodoscore for current week
        expected_team_prodoscore = get_average_score(curr_week_scores)
        expected_team_prodoscore_color = score_to_color(expected_team_prodoscore)
        actual_team_prodoscore = manager_data.get("direct_team_prodoscore").get("score")
        actual_team_prodoscore_color = manager_data.get("direct_team_prodoscore").get(
            "color"
        )
        assert actual_team_prodoscore == expected_team_prodoscore, (
            f"Team Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_prodoscore}\n"
            f"Expected: {expected_team_prodoscore}"
        )
        assert actual_team_prodoscore_color == expected_team_prodoscore_color, (
            f"Team Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_prodoscore_color}\n"
            f"Expected: {expected_team_prodoscore_color}"
        )


def assert_hover_and_distribution_bars(
    manager_page, employees, employee_prodoscore_data, day_map
):
    """
    Assert manager and team prodoscore and percentage change for all employees.
    Args:
        manager_page: The page object with table accessors.
        employees: Dict of employee objects keyed by id.
        employee_prodoscore_data: Nested dict of prodoscore data.
        day_map: Dict mapping week keys to day keys.
        get_average_score: Function to compute average score (with rounding).
        score_to_color: Function to map score to color.
        get_average_score_without_rounding: Function to compute average score (no rounding).
        calculate_percent_change: Function to compute percent change.
    """
    for key, employee in employees.items():
        prev_self_scores = [
            employee_prodoscore_data.get("previous_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("previous_week", {})
        ]
        curr_self_scores = [
            employee_prodoscore_data.get("current_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("current_week", {})
        ]
        if not any(prev_self_scores) and not any(curr_self_scores):
            continue

        # Get actual manager data from the page
        manager_data = manager_page.get_manager_data(employee.full_name)

        # Collect each subordinate's total score for current week
        subordinate_avg_scores = []
        # Collect all unique subordinate keys for this manager across all days in current week
        subordinate_keys = set()
        for day_key in day_map.get("current_week", {}):
            subordinates = (
                employee_prodoscore_data.get("current_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            subordinate_keys.update(subordinates.keys())

        for sub_key in subordinate_keys:
            # Sum all scores for this subordinate across all days in current week
            sub_score = []
            for day_key in day_map.get("current_week", {}):
                score = (
                    employee_prodoscore_data.get("current_week", {})
                    .get(day_key, {})
                    .get(key, {})
                    .get("subordinates", {})
                    .get(sub_key, {})
                    .get("score")
                )
                if score is not None:
                    sub_score.append(score)
            subordinate_avg_scores.append(get_average_score_without_rounding(sub_score))

        # Team distribution bars
        expected_team_distribution_bars: list[dict] = get_team_distribution_bars(
            subordinate_avg_scores
        )
        actual_team_distribution_bars: list[dict] = manager_data.get(
            "team_distribution"
        )
        assert actual_team_distribution_bars == expected_team_distribution_bars, (
            f"Team distribution bars mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_distribution_bars}\n"
            f"Expected: {expected_team_distribution_bars}"
        )

        # Hover the team distribution bar
        manager_page.hover_team_distribution_bar_by_manager_name(employee.full_name)

        # Verify tooltip visibility
        expect(manager_page.team_distribution_tooltip).to_be_visible()

        # Verify tooltip values
        tooltip_data = manager_page.get_team_distribution_tooltip_values()
        expected_tooltip_data = get_expected_team_distribution_tooltip(
            subordinate_avg_scores
        )
        assert tooltip_data == expected_tooltip_data, (
            f"Team distribution tooltip data mismatch for {employee.full_name}.\n"
            f"Actual: {tooltip_data}\n"
            f"Expected: {expected_tooltip_data}"
        )


def assert_percentage_change(
    manager_page, employees, employee_prodoscore_data, day_map
):
    """
    Assert percentage change in team prodoscore for all employees.
    Args:
        manager_page: The page object with table accessors.
        employees: Dict of employee objects keyed by id.
        employee_prodoscore_data: Nested dict of prodoscore data.
        day_map: Dict mapping week keys to day keys.
    """
    for key, employee in employees.items():
        prev_self_scores = [
            employee_prodoscore_data.get("previous_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("previous_week", {})
        ]
        curr_self_scores = [
            employee_prodoscore_data.get("current_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("current_week", {})
        ]
        if not any(prev_self_scores) and not any(curr_self_scores):
            continue

        manager_data = manager_page.get_manager_data(employee.full_name)

        # Validate percentage change in team prodoscore
        prev_week_scores = []
        curr_week_scores = []

        for day_key in day_map.get("previous_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("previous_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            scores = [sub["score"] for sub in subordinates.values()]
            if scores:
                prev_week_scores.append(get_average_score_without_rounding(scores))

        for day_key in day_map.get("current_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("current_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            scores = [sub["score"] for sub in subordinates.values()]
            if scores:
                curr_week_scores.append(get_average_score_without_rounding(scores))

        prev_week_avg = (
            get_average_score_without_rounding(prev_week_scores)
            if prev_week_scores
            else None
        )
        curr_week_avg = (
            get_average_score_without_rounding(curr_week_scores)
            if curr_week_scores
            else None
        )

        expected_percentage_change = calculate_percent_change(
            prev_week_avg, curr_week_avg
        )
        actual_percentage_change = manager_data.get("percent_change")

        assert actual_percentage_change == expected_percentage_change, (
            f"Percentage change mismatch for {employee.full_name}.\n"
            f"Actual: {actual_percentage_change}\n"
            f"Expected: {expected_percentage_change}"
        )


def assert_manager_prodoscore_and_team_prodoscore(
    manager_page, employees, employee_prodoscore_data, day_map
):
    """
    Assert manager and team prodoscore for all employees.
    Args:
        manager_page: The page object with table accessors.
        employees: Dict of employee objects keyed by id.
        employee_prodoscore_data: Nested dict of prodoscore data.
        day_map: Dict mapping week keys to day keys.
    """
    for key, employee in employees.items():
        # Skip manager if role <= 0
        if getattr(employee, "role", 1) <= 0:
            continue

        prev_self_scores = [
            employee_prodoscore_data.get("previous_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("previous_week", {})
        ]
        curr_self_scores = [
            employee_prodoscore_data.get("current_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("current_week", {})
        ]
        if not any(prev_self_scores) and not any(curr_self_scores):
            continue

        manager_data = manager_page.get_manager_data(employee.full_name)

        # Validate manager's prodoscore for current week
        expected_prodoscore = get_average_score(curr_self_scores)
        expected_prodoscore_color = score_to_color(expected_prodoscore)
        actual_prodoscore = manager_data.get("prodoscore").get("score")
        actual_prodoscore_color = manager_data.get("prodoscore").get("color")
        assert actual_prodoscore == expected_prodoscore, (
            f"Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore}\n"
            f"Expected: {expected_prodoscore}"
        )
        assert actual_prodoscore_color == expected_prodoscore_color, (
            f"Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore_color}\n"
            f"Expected: {expected_prodoscore_color}"
        )

        # Validate percentage change in team prodoscore
        prev_week_scores = []
        curr_week_scores = []

        for day_key in day_map.get("previous_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("previous_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            # Skip subordinates with role <= 0 (get from employees dict)
            scores = [
                sub["score"]
                for sub_id, sub in subordinates.items()
                if getattr(employees.get(sub_id), "role", 1) > 0
            ]
            if scores:
                prev_week_scores.append(get_average_score_without_rounding(scores))

        for day_key in day_map.get("current_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("current_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            # Skip subordinates with role <= 0 (get from employees dict)
            scores = [
                sub["score"]
                for sub_id, sub in subordinates.items()
                if getattr(employees.get(sub_id), "role", 1) > 0
            ]
            if scores:
                curr_week_scores.append(get_average_score_without_rounding(scores))

        # Validate team prodoscore for current week
        expected_team_prodoscore = get_average_score(curr_week_scores)
        expected_team_prodoscore_color = score_to_color(expected_team_prodoscore)
        actual_team_prodoscore = manager_data.get("direct_team_prodoscore").get("score")
        actual_team_prodoscore_color = manager_data.get("direct_team_prodoscore").get(
            "color"
        )
        assert actual_team_prodoscore == expected_team_prodoscore, (
            f"Team Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_prodoscore}\n"
            f"Expected: {expected_team_prodoscore}"
        )
        assert actual_team_prodoscore_color == expected_team_prodoscore_color, (
            f"Team Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_prodoscore_color}\n"
            f"Expected: {expected_team_prodoscore_color}"
        )


def assert_manager_table_sorted_and_row_count(manager_page, expected_users):
    """
    Assert that the manager table has the expected number of rows and is sorted by manager name.
    Args:
        manager_page: The page object with table accessors.
        expected_users: List of user objects (with .full_name) expected in the table.
    """
    num_rows = manager_page.get_number_of_rows_in_manager_table()
    expected_num_rows = len(expected_users)
    assert num_rows == expected_num_rows, (
        f"Row count mismatch.\n"
        f"Actual: {num_rows}\n"
        f"Expected: {expected_num_rows}",
    )

    # Verify the manager table is sorted by manager name (full_name)
    manager_names_in_table = [
        manager_page.get_manager_name_by_row(i) for i in range(num_rows)
    ]
    expected_names = sorted([user.full_name for user in expected_users])
    assert manager_names_in_table == expected_names, (
        f"Manager table not sorted by name.\n"
        f"Actual: {manager_names_in_table}\n"
        f"Expected: {expected_names}"
    )


def assert_manager_prodoscore_with_no_score(
    manager_page, employees, employee_prodoscore_data, employee_holidays_data, day_map
):
    """
    Assert manager prodoscore displays '-' when manager is on holiday for the entire week.
    Args:
        manager_page: The page object with table accessors.
        employees: Dict of employee objects keyed by id.
        employee_prodoscore_data: Nested dict of prodoscore data.
        employee_holidays_data: Nested dict of employee holiday data.
        day_map: Dict mapping week keys to day keys.
    """

    def is_on_holiday(user_key, week_key, day_key):
        holidays = (employee_holidays_data or {}).get(week_key, {}).get(user_key, [])
        return day_key in holidays

    def is_on_holiday_entire_week(user_key, week_key, day_keys):
        holidays = set(
            (employee_holidays_data or {}).get(week_key, {}).get(user_key, [])
        )
        return set(day_keys) <= holidays and len(day_keys) > 0

    for key, employee in employees.items():
        prev_week_days = list(day_map.get("previous_week", {}))
        curr_week_days = list(day_map.get("current_week", {}))

        prev_self_scores = [
            employee_prodoscore_data.get("previous_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in prev_week_days
            if not is_on_holiday(key, "previous_week", day_key)
        ]
        curr_self_scores = [
            employee_prodoscore_data.get("current_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in curr_week_days
            if not is_on_holiday(key, "current_week", day_key)
        ]

        # Special scenario: manager is on holiday for the entire week
        manager_on_holiday_entire_week = is_on_holiday_entire_week(
            key, "current_week", curr_week_days
        )

        if (
            not any(prev_self_scores)
            and not any(curr_self_scores)
            and not manager_on_holiday_entire_week
        ):
            continue

        manager_data = manager_page.get_manager_data(employee.full_name)

        # If manager is on holiday for the entire week, expect prodoscore to be '-'
        if manager_on_holiday_entire_week:
            expected_prodoscore = "-"
            expected_prodoscore_color = "unknown"
        else:
            expected_prodoscore = get_average_score(curr_self_scores)
            expected_prodoscore_color = score_to_color(expected_prodoscore)

        actual_prodoscore = manager_data.get("prodoscore").get("score")
        actual_prodoscore_color = manager_data.get("prodoscore").get("color")

        assert actual_prodoscore == expected_prodoscore, (
            f"Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore}\n"
            f"Expected: {expected_prodoscore}"
        )
        assert actual_prodoscore_color == expected_prodoscore_color, (
            f"Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore_color}\n"
            f"Expected: {expected_prodoscore_color}"
        )


def assert_manager_prodoscore_team_prodoscore_and_team_distributions(
    manager_page, employees, employee_prodoscore_data, day_map
):
    """
    Assert manager and team prodoscore for all employees.
    Args:
        manager_page: The page object with table accessors.
        employees: Dict of employee objects keyed by id.
        employee_prodoscore_data: Nested dict of prodoscore data.
        day_map: Dict mapping week keys to day keys.
    """
    for key, employee in employees.items():
        # Skip manager if role <= 0
        if getattr(employee, "role", 1) <= 0:
            continue

        prev_self_scores = [
            employee_prodoscore_data.get("previous_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("previous_week", {})
        ]
        curr_self_scores = [
            employee_prodoscore_data.get("current_week", {})
            .get(day_key, {})
            .get(key, {})
            .get("self", {})
            .get("score")
            for day_key in day_map.get("current_week", {})
        ]
        if not any(prev_self_scores) and not any(curr_self_scores):
            continue

        manager_data = manager_page.get_manager_data(employee.full_name)

        # Validate manager's prodoscore for current week
        expected_prodoscore = get_average_score(curr_self_scores)
        expected_prodoscore_color = score_to_color(expected_prodoscore)
        actual_prodoscore = manager_data.get("prodoscore").get("score")
        actual_prodoscore_color = manager_data.get("prodoscore").get("color")
        assert actual_prodoscore == expected_prodoscore, (
            f"Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore}\n"
            f"Expected: {expected_prodoscore}"
        )
        assert actual_prodoscore_color == expected_prodoscore_color, (
            f"Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_prodoscore_color}\n"
            f"Expected: {expected_prodoscore_color}"
        )

        # Validate percentage change in team prodoscore
        prev_week_scores = []
        curr_week_scores = []

        for day_key in day_map.get("previous_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("previous_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            # Skip subordinates with role <= 0 (get from employees dict)
            scores = [
                sub["score"]
                for sub_id, sub in subordinates.items()
                if getattr(employees.get(sub_id), "role", 1) > 0
            ]
            if scores:
                prev_week_scores.append(get_average_score_without_rounding(scores))

        for day_key in day_map.get("current_week", {}).keys():
            subordinates = (
                employee_prodoscore_data.get("current_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            # Skip subordinates with role <= 0 (get from employees dict)
            scores = [
                sub["score"]
                for sub_id, sub in subordinates.items()
                if getattr(employees.get(sub_id), "role", 1) > 0
            ]
            if scores:
                curr_week_scores.append(get_average_score_without_rounding(scores))

        # Validate team prodoscore for current week
        expected_team_prodoscore = get_average_score(curr_week_scores)
        expected_team_prodoscore_color = score_to_color(expected_team_prodoscore)
        actual_team_prodoscore = manager_data.get("direct_team_prodoscore").get("score")
        actual_team_prodoscore_color = manager_data.get("direct_team_prodoscore").get(
            "color"
        )
        assert actual_team_prodoscore == expected_team_prodoscore, (
            f"Team Prodoscore mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_prodoscore}\n"
            f"Expected: {expected_team_prodoscore}"
        )
        assert actual_team_prodoscore_color == expected_team_prodoscore_color, (
            f"Team Prodoscore color mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_prodoscore_color}\n"
            f"Expected: {expected_team_prodoscore_color}"
        )

        # Collect each subordinate's total score for current week
        subordinate_avg_scores = []
        # Collect all unique subordinate keys for this manager across all days in current week
        subordinate_keys = set()
        for day_key in day_map.get("current_week", {}):
            subordinates = (
                employee_prodoscore_data.get("current_week", {})
                .get(day_key, {})
                .get(key, {})
                .get("subordinates", {})
            )
            subordinate_keys.update(subordinates.keys())

        for sub_key in subordinate_keys:
            # Sum all scores for this subordinate across all days in current week
            sub_score = []
            for day_key in day_map.get("current_week", {}):
                score = (
                    employee_prodoscore_data.get("current_week", {})
                    .get(day_key, {})
                    .get(key, {})
                    .get("subordinates", {})
                    .get(sub_key, {})
                    .get("score")
                )
                if score is not None:
                    sub_score.append(score)
            subordinate_avg_scores.append(get_average_score_without_rounding(sub_score))

        # Team distribution bars
        expected_team_distribution_bars: list[dict] = get_team_distribution_bars(
            subordinate_avg_scores
        )
        actual_team_distribution_bars: list[dict] = manager_data.get(
            "team_distribution"
        )
        assert actual_team_distribution_bars == expected_team_distribution_bars, (
            f"Team distribution bars mismatch for {employee.full_name}.\n"
            f"Actual: {actual_team_distribution_bars}\n"
            f"Expected: {expected_team_distribution_bars}"
        )

        # Hover the team distribution bar
        manager_page.hover_team_distribution_bar_by_manager_name(employee.full_name)

        # Verify tooltip visibility
        expect(manager_page.team_distribution_tooltip).to_be_visible()

        # Verify tooltip values
        tooltip_data = manager_page.get_team_distribution_tooltip_values()
        expected_tooltip_data = get_expected_team_distribution_tooltip(
            subordinate_avg_scores
        )
        assert tooltip_data == expected_tooltip_data, (
            f"Team distribution tooltip data mismatch for {employee.full_name}.\n"
            f"Actual: {tooltip_data}\n"
            f"Expected: {expected_tooltip_data}"
        )
