from typing import List

from automation_test.models.employee_prodoscore import EmployeeProdoscore


def insert_employee_prodoscore(db_client, prodoscore: EmployeeProdoscore) -> int | None:
    """
    Insert a single EmployeeProdoscore record into the database.
    Args:
        db_client: The database client/connection.
        prodoscore: EmployeeProdoscore object to insert.
    Returns:
        The inserted record's ID (if available), or 0.
    """
    columns = [
        "domain_id",
        "employee_id",
        "date",
        "role",
        "score",
        "ip_int_ext",
        "total_gap_time",
        "total_active_time",
        "gap_times",
        "first_last_activity_times",
    ]
    values = [
        prodoscore.domain_id,
        prodoscore.employee_id,
        prodoscore.date,
        prodoscore.role,
        prodoscore.score,
        prodoscore.ip_int_ext,
        prodoscore.total_gap_time,
        prodoscore.total_active_time,
        prodoscore.gap_times,
        prodoscore.first_last_activity_times,
    ]
    sql = f"""
        INSERT INTO proapp_employee_prodoscore
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    db_client.execute_update(sql, tuple(values))
    # Optionally fetch the inserted ID if needed
    return prodoscore.id


def bulk_insert_employee_prodoscores(
    db_client, prodoscores: List[EmployeeProdoscore]
) -> None:
    """
    Bulk insert multiple EmployeeProdoscore records into the database.
    Args:
        db_client: The database client/connection.
        prodoscores: List of EmployeeProdoscore objects to insert.
    """
    if not prodoscores:
        return
    columns = [
        "domain_id",
        "employee_id",
        "date",
        "role",
        "score",
        "ip_int_ext",
        "total_gap_time",
        "total_active_time",
        "gap_times",
        "first_last_activity_times",
    ]
    sql = f"""
        INSERT INTO proapp_employee_prodoscore
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    params_list = [
        (
            p.domain_id,
            p.employee_id,
            p.date,
            p.role,
            p.score,
            p.ip_int_ext,
            p.total_gap_time,
            p.total_active_time,
            p.gap_times,
            p.first_last_activity_times,
        )
        for p in prodoscores
    ]
    db_client.bulk_insert(sql, params_list)


def delete_employee_prodoscore(db_client, filter_condition: str) -> int:
    """
    Delete EmployeeProdoscore records from the database based on a filter condition.

    Args:
        db_client: The database client/connection.
        filter_condition: SQL WHERE clause condition as a string (e.g., "date >= '2024-01-01' and domain_id = '123'").

    Returns:
        Number of deleted rows.
    """
    sql = f"DELETE FROM proapp_employee_prodoscore WHERE {filter_condition}"
    return db_client.execute_update(sql)
