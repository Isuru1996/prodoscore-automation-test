from automation_test.db.employee_prodoscore_utils import (
    bulk_insert_employee_prodoscores,
)
from automation_test.db.organization_prodoscore_utils import (
    bulk_insert_organization_prodoscores,
    insert_organization_prodoscore,
)
from automation_test.models import Employee, EmployeeProdoscore, OrganizationProdoscore
from automation_test.utils.date_utils import add_days_to_date


# Common step 1: Map day keys to dates
def map_day_keys_to_dates(employee_prodoscore_data, current_date):
    day_map = {}
    for week_key, week_data in employee_prodoscore_data.items():
        day_map[week_key] = {}
        for day_key in week_data.keys():
            day_num = int(day_key.replace("day", ""))
            if week_key == "current_week":
                day_map[week_key][day_key] = add_days_to_date(
                    current_date, -(7 - day_num)
                )
            elif week_key == "previous_week":
                day_map[week_key][day_key] = add_days_to_date(
                    current_date, -(14 - day_num)
                )
    return day_map


# Insert employee prodoscores from test data
def insert_employee_prodoscores_from_testdata(
    employee_prodoscore_data, day_map, employees, db_client
):
    employee_prodoscores = []
    for week_key, week_days in day_map.items():
        for day_key, date_str in week_days.items():
            day_data = employee_prodoscore_data.get(week_key, {}).get(day_key, {})
            for manager_key, manager_data in day_data.items():
                manager_user = employees.get(manager_key)
                self_score = manager_data.get("self")
                if self_score:
                    employee_prodoscores.append(
                        EmployeeProdoscore(
                            domain_id=manager_user.domain_id,
                            employee_id=manager_user.id,
                            date=date_str,
                            role=manager_user.role,
                            score=self_score["score"],
                        )
                    )
                for sub_key, sub_score in manager_data.get("subordinates", {}).items():
                    sub_user = employees.get(sub_key)
                    employee_prodoscores.append(
                        EmployeeProdoscore(
                            domain_id=sub_user.domain_id,
                            employee_id=sub_user.id,
                            date=date_str,
                            role=sub_user.role,
                            score=sub_score["score"],
                        )
                    )
    bulk_insert_employee_prodoscores(db_client, employee_prodoscores)


# Insert organization prodoscores from test data
def insert_organization_prodoscores_from_testdata(
    organization_prodoscore_data, day_map, domain, db_client
):
    organization_prodoscores = []
    for week_key, week_days in day_map.items():
        for day_key, date_str in week_days.items():
            org_prodoscore_value = organization_prodoscore_data.get(week_key, {}).get(
                day_key
            )
            if org_prodoscore_value is not None:
                organization_prodoscores.append(
                    OrganizationProdoscore(
                        domain_id=domain.id,
                        date=date_str,
                        score=org_prodoscore_value["score"],
                    )
                )
    bulk_insert_organization_prodoscores(db_client, organization_prodoscores)
