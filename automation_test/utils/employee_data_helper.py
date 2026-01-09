"""Helper functions for employee data and color mapping."""

import math


def score_to_color(score: int) -> str:
    """
    Map a prodoscore value to a color name based on business rules.
    Adjust thresholds and color names as needed.
    """
    if score >= 75:
        return "blue"
    elif score >= 40:
        return "gray"
    else:
        return "red"


def get_average_score(scores: list[int]) -> int:
    """
    Calculate the average score from a list of scores.
    Args:
        scores: List of individual employee scores.
    Returns:
        The average score as an integer.
    """
    total_score = sum(scores)
    average_score = total_score / len(scores)
    return math.floor(average_score)


def get_average_score_without_rounding(scores: list[int]) -> float:
    """
    Calculate the average score from a list of scores.
    Args:
        scores: List of individual employee scores.
    Returns:
        The average score as an integer.
    """
    total_score = sum(scores)
    average_score = total_score / len(scores)
    return average_score


def get_team_distribution_bars(scores: list[float]) -> list[dict]:
    """
    Given a list of subordinate scores, calculate the number of bars and their percentages by color.
    Returns a list of dicts: [{"color": str, "percentage": float}]
    """
    if not scores:
        return []
    total = len(scores)
    blue_count = sum(1 for s in scores if s >= 75)
    gray_count = sum(1 for s in scores if 40 <= s < 75)
    red_count = sum(1 for s in scores if s < 40)

    bars = []
    if blue_count > 0:
        percent = math.floor((blue_count / total) * 100)
        bars.append({"color": "blue", "value": f"{percent}%"})
    if gray_count > 0:
        percent = math.floor((gray_count / total) * 100)
        bars.append({"color": "gray", "value": f"{percent}%"})
    if red_count > 0:
        percent = math.floor((red_count / total) * 100)
        bars.append({"color": "red", "value": f"{percent}%"})

    # Sort bars by color order: blue, gray, red
    color_order = {"red": 0, "gray": 1, "blue": 2}
    bars.sort(key=lambda x: color_order.get(x["color"], 99))
    return bars


def get_expected_team_distribution_tooltip(
    subordinate_total_scores_list: list[float],
) -> dict:
    """
    Given a list of subordinate scores, return the expected tooltip value dict for below/within/above average.
    Structure matches the tooltip_data format.
    """
    scores = subordinate_total_scores_list
    total = len(scores)
    blue_count = sum(1 for s in scores if s >= 75)
    gray_count = sum(1 for s in scores if 40 <= s < 75)
    red_count = sum(1 for s in scores if s < 40)
    return {
        "below_average": {
            "percentage": {
                "value": f"{math.floor((red_count/total)*100)}%",
                "color": "red",
            },
            "count": {
                "value": str(red_count),
                "color": "red",
            },
        },
        "within_average": {
            "percentage": {
                "value": f"{math.floor((gray_count/total)*100)}%",
                "color": "gray",
            },
            "count": {
                "value": str(gray_count),
                "color": "gray",
            },
        },
        "above_average": {
            "percentage": {
                "value": f"{math.floor((blue_count/total)*100)}%",
                "color": "blue",
            },
            "count": {
                "value": str(blue_count),
                "color": "blue",
            },
        },
    }


def calculate_percent_change(prev_week_avg, curr_week_avg):
    """
    Calculate percent change between previous and current week averages.
    Returns a dict with keys: value, color, arrow_type.
    - value: percent change (rounded down, int, no sign, e.g. 12)
    - color: 'blue' if increase, 'gray' if zero, 'red' if decrease
    - arrow_type: 'arrow-up' if increase, 'arrow-down' if decrease, None if zero
    If prev_week_avg is None or zero, treat as 0 (if both are zero, percent change is 0).
    """
    if prev_week_avg is None:
        prev_week_avg = 0
    if curr_week_avg is None:
        curr_week_avg = 0
    if prev_week_avg == 0:
        if curr_week_avg == 0:
            percent = 0
        else:
            percent = 100  # treat as 100% increase from 0 to nonzero
    else:
        percent = ((curr_week_avg - prev_week_avg) / prev_week_avg) * 100
    percent_int = round(percent)  # round to nearest integer
    if percent_int > 0:
        color = "blue"
        arrow_type = "arrow-up"
    elif percent_int < 0:
        color = "red"
        arrow_type = "arrow-down"
    else:
        color = "black"
        arrow_type = None
    return {
        "value": f"{abs(percent_int)}%",
        "color": color,
        "arrow_type": arrow_type,
    }
