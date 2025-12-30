from dataclasses import dataclass
from typing import Optional


@dataclass
class Employee:
    id: Optional[int]
    domain_id: int
    email: str
    email_hash: str
    full_name: str
    department_id: int
    manager_id: int
    role: int
    view_status: int
    profile_id: str
    status: int
    password: str
    details_enabled: int
    report_email: str
    report_enabled: int
    activate_workshift: int
    is_app_user: int
    time_zone: str
    notices: str
    crx_status: int
    coll_id: str
    test_name: str

    def commit(self, db_client):
        row_to_update = {
            "domain_id": self.domain_id,
            "fullname": self.full_name,
            "department_id": self.department_id,
            "manager_id": self.manager_id,
            "role": self.role,
            "view_status": self.view_status,
            "profileId": self.profile_id,
            "status": self.status,
            "password": self.password,
            "details_enabled": self.details_enabled,
            "report_email": self.report_email,
            "report_enabled": self.report_enabled,
            "activate_workshift": self.activate_workshift,
            "is_app_user": self.is_app_user,
            "timezone": self.time_zone,
            "notices": self.notices,
            "crx_status": self.crx_status,
            "coll_id": self.coll_id,
        }
        set_clause = ", ".join(f"{k} = %s" for k in row_to_update)
        values = list(row_to_update.values())
        sql = f"UPDATE proapp_employee SET {set_clause} WHERE id = %s"
        db_client.execute_update(sql, tuple(values + [self.id]))

    def change_name(self, new_name):
        self.full_name = new_name

    def change_department(self, new_department):
        self.department_id = new_department

    def change_role(self, new_role):
        self.role = new_role

    def change_view_status(self, new_view_status):
        self.view_status = new_view_status

    def change_profile_id(self, new_profile_id):
        self.profile_id = new_profile_id

    def change_status(self, new_status):
        self.status = new_status

    def change_password(self, new_password):
        self.password = new_password

    def change_manager(self, employee):
        self.manager_id = employee.id

    def change_report_email(self, employee):
        self.report_email = employee.email

    def change_is_app_user(self, is_app_user):
        self.is_app_user = is_app_user

    def change_time_zone(self, time_zone):
        self.time_zone = time_zone

    def change_notices(self, notices):
        self.notices = notices

    def change_crx_status(self, crx_status):
        self.crx_status = crx_status

    def change_coll_id(self, coll_id):
        self.coll_id = coll_id
