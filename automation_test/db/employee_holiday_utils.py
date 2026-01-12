from typing import List

from automation_test.models import EmployeeHoliday


def insert_employee_holiday(db_client, employee_holiday: EmployeeHoliday) -> int | None:
    """
    Insert an EmployeeHoliday record into the database.
    Args:
        db_client: The database client/connection.
        employee_holiday: An EmployeeHoliday object to insert.
    Returns:
        The ID of the inserted EmployeeHoliday record.
    """
    columns = [
        "domain_id",
        "employee_id",
        "date",
        "source",
        "status",
        "updated_status",
    ]

    values = [
        employee_holiday.domain_id,
        employee_holiday.employee_id,
        employee_holiday.date,
        employee_holiday.source,
        employee_holiday.status,
        employee_holiday.updated_status,
    ]
    sql = f"""
        INSERT INTO proapp_employee_holiday
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    db_client.execute_update(sql, tuple(values))
    # Optionally fetch the inserted ID if needed
    return employee_holiday.id


def bulk_insert_employee_holidays(
    db_client, emp_holidays: List[EmployeeHoliday]
) -> None:
    """
    Bulk insert EmployeeHoliday records into the database.
    Args:
        db_client: The database client/connection.
        emp_holidays: A list of EmployeeHoliday objects to insert.
    Returns:
        None
    """
    if not emp_holidays:
        return
    columns = [
        "domain_id",
        "employee_id",
        "date",
        "source",
        "status",
        "updated_status",
    ]

    sql = f"""
        INSERT INTO proapp_employee_holiday
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    params_list = [
        (o.domain_id, o.employee_id, o.date, o.source, o.status, o.updated_status)
        for o in emp_holidays
    ]
    db_client.bulk_insert(sql, params_list)


def delete_employee_holiday(db_client, filter_condition: str) -> int:
    """
    Delete EmployeeHoliday records from the database based on a filter condition.
    Args:
        db_client: The database client/connection.
        filter_condition: SQL WHERE clause condition as a string (e.g., "date >= '2024-01-01' and domain_id = '123'").
    Returns:
        Number of deleted rows.
    """
    sql = f"DELETE FROM proapp_employee_holiday WHERE {filter_condition}"
    return db_client.execute_update(sql)
