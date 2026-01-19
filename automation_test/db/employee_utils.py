from typing import Dict, List

from automation_lib.core import Config

from automation_test.api_clients.prodoscore_crypto_client import ProdoscoreCryptoClient

from ..models import Employee


def create_employees(
    db_client, login_user_id: int, employee_ids: List[int]
) -> Dict[str, Employee]:
    """
    Fetch employee records by IDs and return a mapping with login_user, user_1, user_2, user_3, ...
    Args:
        db_client: The database client/connection.
        employee_ids: A list of employee IDs to fetch.
        The first ID in the list is assumed to be the login user.
    Returns:
        A dict mapping login_user, user_1, user_2, user_3, ... to Employee objects.
    """
    employee_ids = employee_ids + [login_user_id]
    if not employee_ids:
        return {}
    placeholders = ", ".join(["%s"] * len(employee_ids))
    sql = f"SELECT * FROM proapp_employee WHERE id IN ({placeholders})"
    results = db_client.fetch_all(sql, tuple(employee_ids))
    employees = [
        Employee(
            id=result["id"],
            domain_id=result["domain_id"],
            email=result["email"],
            email_hash=result.get("email_hash"),
            full_name=result.get("fullname"),
            department_id=result.get("department_id"),
            manager_id=result.get("manager_id"),
            role=result.get("role"),
            view_status=result.get("view_status"),
            profile_id=result.get("profileId"),
            status=result.get("status"),
            password=result.get("password"),
            details_enabled=result.get("details_enabled"),
            report_email=result.get("report_email"),
            report_enabled=result.get("report_enabled"),
            activate_workshift=result.get("activate_workshift"),
            is_app_user=result.get("is_app_user"),
            time_zone=result.get("timezone"),
            notices=result.get("notices"),
            crx_status=result.get("crx_status"),
            coll_id=result.get("coll_id"),
        )
        for result in results
    ]

    # Separate login user from others
    login_user = next((e for e in employees if e.id == login_user_id), None)
    others = [e for e in employees if e.id != login_user_id]
    others_sorted = sorted(others, key=lambda e: e.id if e.id is not None else 0)
    result = {}
    if login_user:
        result["login_user"] = login_user
    # Add other users as user_1, user_2, user_3, etc.
    for idx, emp in enumerate(others_sorted, start=1):
        result[f"user_{idx}"] = emp
    return result


def update_employees_default(db_client, domain_id, login_id):
    """
    Sets up all employees in the given domain with default values in the database, excluding the login_id.

    Args:
            db_client: The database client/connection.
            domain_id: The ID of the domain whose employees are to be updated.
            login_id: The ID of the logged-in user to be excluded from the update.
    """
    row_to_update = {
        "manager_id": 52,
        "role": 0,
        "timezone": "America/Los_Angeles",
        "status": 1,
        "password": "[NOPASSWORD]",
        "details_enabled": 1,
        "report_email": "",
        "report_enabled": 1000,
        "activate_workshift": -1,
        "is_app_user": 0,
        "notices": None,
        "crx_status": 0,
        "coll_id": None,
        "view_status": 1,
    }
    set_clause = ", ".join(f"{k} = %s" for k in row_to_update)
    values = list(row_to_update.values())
    sql = f"UPDATE proapp_employee SET {set_clause} WHERE domain_id = %s AND id != %s"
    db_client.execute_update(sql, tuple(values + [domain_id, login_id]))

    # Also update the login user's role, status, and view_status
    login_update = {
        "role": 15000,
        "status": 1,
        "view_status": 3,
    }
    login_set_clause = ", ".join(f"{k} = %s" for k in login_update)
    login_values = list(login_update.values())
    login_sql = f"UPDATE proapp_employee SET {login_set_clause} WHERE id = %s"
    db_client.execute_update(login_sql, tuple(login_values + [login_id]))


def add_test_employees(
    db_client,
    config: Config,
    role: int,
    view_status: int,
    status: int,
    source: str,
    number_of_employees: int,
) -> List[int]:
    """
    Adds fake employees to the database for testing purposes.
    Args:
            db_client: The database client/connection.
            config: The configuration object to fetch settings.
            role: The role to assign to the fake employees.
            view_status: The view status to assign to the fake employees.
            status: The status to assign to the fake employees.
            source: A string prefix for the fake employee emails and names.
    """
    domain_id = config.get("domain.id")
    admin_email = config.get("domain.admin_email")
    prodoscore_crypto_base_url = config.get("api_clients.prodoscore_crypto.base_url")
    employees_to_insert: List[Dict] = []
    email_hashes: List[str] = []
    for i in range(1, number_of_employees + 1):
        email = f"{source.lower()}automationtest{i}@{admin_email.split('@')[1]}"
        prodoscore_crypto_client = ProdoscoreCryptoClient(
            base_url=prodoscore_crypto_base_url
        )
        encrypted_email_response = prodoscore_crypto_client.encrypt(plain_text=email)
        hashed_email_response = prodoscore_crypto_client.hash(text=email)

        email_hash = hashed_email_response.hash
        email_cipher = encrypted_email_response.cipher

        if email_hash:
            email_hashes.append(email_hash)

        # Prepare employee row
        employee_row = {
            "domain_id": domain_id,
            "manager_id": 52,
            "role": role,
            "view_status": view_status,
            "profileId": f"{source}: Test Profile ID {i}",
            "email": email_cipher,
            "email_hash": email_hash,
            "fullname": f"{source.lower()}_automation_test_user_{i}",
            "timezone": "America/Los_Angeles",
            "status": status,
        }
        employees_to_insert.append(employee_row)

    # Delete all existing users
    if email_hashes:
        placeholders = ", ".join(["%s"] * len(email_hashes))
        sql = f"DELETE FROM proapp_employee WHERE email_hash IN ({placeholders})"
        db_client.execute_update(sql, tuple(email_hashes))

    # Bulk insert using db_client.bulk_insert
    if employees_to_insert:
        columns = list(employees_to_insert[0].keys())
        sql = f"INSERT INTO proapp_employee ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        params_list = [
            tuple(row[col] for col in columns) for row in employees_to_insert
        ]
        db_client.bulk_insert(sql, params_list)

        # Fetch IDs of inserted employees
        placeholders = ", ".join(["%s"] * len(email_hashes))
        select_sql = (
            f"SELECT id FROM proapp_employee WHERE email_hash IN ({placeholders})"
        )
        results = db_client.fetch_all(select_sql, tuple(email_hashes))
        inserted_ids = [row["id"] for row in results]
        return inserted_ids
    return []


def delete_employees(db_client, employee_ids: List[int]) -> int:
    """
    Delete employees from the database by a list of employee IDs.
    Args:
        db_client: The database client/connection.
        employee_ids: List of employee IDs to delete.
    Returns:
        Number of deleted rows.
    """
    if not employee_ids:
        return 0
    placeholders = ", ".join(["%s"] * len(employee_ids))
    sql = f"DELETE FROM proapp_employee WHERE id IN ({placeholders})"
    return db_client.execute_update(sql, tuple(employee_ids))


def get_employees(
    db_client,
    employee_ids: List[int],
) -> List[Employee]:
    """
    Fetch employees from the database by a list of employee IDs.
    Args:
        db_client: The database client/connection.
        employee_ids: List of employee IDs to fetch.
    Returns:
        List of Employee objects fetched from the DB.
    """
    if not employee_ids:
        return []
    placeholders = ", ".join(["%s"] * len(employee_ids))
    sql = f"SELECT * FROM proapp_employee WHERE id IN ({placeholders})"
    results = db_client.fetch_all(sql, tuple(employee_ids))
    employees = [
        Employee(
            id=result["id"],
            domain_id=result["domain_id"],
            email=result["email"],
            email_hash=result.get("email_hash"),
            full_name=result.get("fullname"),
            department_id=result.get("department_id"),
            manager_id=result.get("manager_id"),
            role=result.get("role"),
            view_status=result.get("view_status"),
            profile_id=result.get("profileId"),
            status=result.get("status"),
            password=result.get("password"),
            details_enabled=result.get("details_enabled"),
            report_email=result.get("report_email"),
            report_enabled=result.get("report_enabled"),
            activate_workshift=result.get("activate_workshift"),
            is_app_user=result.get("is_app_user"),
            time_zone=result.get("timezone"),
            notices=result.get("notices"),
            crx_status=result.get("crx_status"),
            coll_id=result.get("coll_id"),
        )
        for result in results
    ]
    return employees


def set_manager_chain_for_employees(db_client, employees: List[Employee]) -> None:
    """
    Bulk update manager_id for a list of employees.
    Each employee's manager_id is set to the previous employee's id (wrap-around).
    Args:
        db_client: The database client/connection.
        employees: List of Employee objects to update.
    """
    if not employees or len(employees) < 2:
        return
    update_rows = []
    for i, emp in enumerate(employees):
        # Previous employee id, wrap-around
        prev_emp_id = employees[i - 1].id if i > 0 else employees[-1].id
        if emp.id is not None and prev_emp_id is not None:
            update_rows.append((prev_emp_id, emp.id))
    # Bulk update
    sql = "UPDATE proapp_employee SET manager_id = %s WHERE id = %s"
    db_client.bulk_update(sql, update_rows)
