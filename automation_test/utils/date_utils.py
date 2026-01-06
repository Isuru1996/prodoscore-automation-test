import datetime


def get_ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def to_choose_date_string(date_str):
    # date_str: "2025-12-02"
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    weekday = dt.strftime("%A")
    month = dt.strftime("%B")
    day = get_ordinal(dt.day)
    return f"Choose {weekday}, {month} {day},"


def add_days_to_date(date_str: str, days: int) -> str:
    """
    Add or subtract days from a date string in 'YYYY-MM-DD' format.

    :param date_str: Date string in 'YYYY-MM-DD' format.
    :param days: Number of days to add (can be negative).
    :return: New date as string in 'YYYY-MM-DD' format.
    """
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    new_dt = dt + datetime.timedelta(days=days)
    return new_dt.strftime("%Y-%m-%d")
