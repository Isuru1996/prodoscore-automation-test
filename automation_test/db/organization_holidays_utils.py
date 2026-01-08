from typing import List

from automation_test.models import OrganizationHoliday


def insert_organization_holiday(
    db_client, org_holiday: OrganizationHoliday
) -> int | None:
    """
    Insert a single OrganizationHoliday record into the database.
    Args:
        db_client: The database client/connection.
        org_holiday: OrganizationHoliday object to insert.
    Returns:
        The inserted record's ID (if available), or None.
    """
    columns = [
        "domain_id",
        "date",
        "status",
        "updated_status",
    ]

    values = [
        org_holiday.domain_id,
        org_holiday.date,
        org_holiday.status,
        org_holiday.updated_status,
    ]
    sql = f"""
        INSERT INTO proapp_organization_holiday
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    db_client.execute_update(sql, tuple(values))
    # Optionally fetch the inserted ID if needed
    return org_holiday.id


def bulk_insert_organization_holidays(
    db_client, org_holidays: List[OrganizationHoliday]
) -> None:
    """
    Bulk insert multiple OrganizationHoliday records into the database.
    Args:
        db_client: The database client/connection.
        org_holidays: List of OrganizationHoliday objects to insert.
    """
    if not org_holidays:
        return
    columns = [
        "domain_id",
        "date",
        "status",
        "updated_status",
    ]

    sql = f"""
        INSERT INTO proapp_organization_holiday
        ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
    """
    params_list = [
        (o.domain_id, o.date, o.status, o.updated_status) for o in org_holidays
    ]
    db_client.bulk_insert(sql, params_list)


def delete_organization_holiday(db_client, filter_condition: str) -> int:
    """
    Delete OrganizationHoliday records from the database based on a filter condition.
    Args:
        db_client: The database client/connection.
        filter_condition: SQL WHERE clause condition as a string (e.g., "date >= '2024-01-01' and domain_id = '123'").
    Returns:
        Number of deleted rows.
    """
    sql = f"DELETE FROM proapp_organization_holiday WHERE {filter_condition}"
    return db_client.execute_update(sql)
