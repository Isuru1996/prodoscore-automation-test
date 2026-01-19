from dataclasses import dataclass
from typing import Optional

from automation_lib.core import BaseModel


@dataclass
class Employee(BaseModel):
    model_name: str = "EmployeeModel"
    id: Optional[int] = None
    domain_id: int = 0
    email: str = ""
    email_hash: str = ""
    full_name: str = ""
    department_id: int = 0
    manager_id: int = 0
    role: int = 0
    view_status: int = 0
    profile_id: str = ""
    status: int = 0
    password: str = ""
    details_enabled: int = 0
    report_email: str = ""
    report_enabled: int = 0
    activate_workshift: int = 0
    is_app_user: int = 0
    time_zone: str = ""
    notices: str = ""
    crx_status: int = 0
    coll_id: str = ""

    def commit(self, db_client):
        self.logger.info(
            f"Committing changes for employee {self.full_name} (ID: {self.id})"
        )
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
        self.logger.info(f"Changing {self.full_name} name to {new_name}")
        self.full_name = new_name

    def change_department(self, new_department):
        self.logger.info(f"Changing {self.full_name} department to {new_department}")
        self.department_id = new_department

    def change_role(self, new_role):
        self.logger.info(f"Changing {self.full_name} role to {new_role}")
        self.role = new_role

    def change_view_status(self, new_view_status):
        self.logger.info(f"Changing {self.full_name} view status to {new_view_status}")
        self.view_status = new_view_status

    def change_profile_id(self, new_profile_id):
        self.logger.info(f"Changing {self.full_name} profile ID to {new_profile_id}")
        self.profile_id = new_profile_id

    def change_status(self, new_status):
        self.logger.info(f"Changing {self.full_name} status to {new_status}")
        self.status = new_status

    def change_password(self, new_password):
        self.logger.info(f"Changing {self.full_name} password")
        self.password = new_password

    def change_manager(self, employee):
        self.logger.info(f"Changing {self.full_name} manager to {employee.full_name}")
        self.manager_id = employee.id

    def change_report_email(self, employee):
        self.logger.info(f"Changing {self.full_name} report email to {employee.email}")
        self.report_email = employee.email

    def change_is_app_user(self, is_app_user):
        self.logger.info(f"Changing {self.full_name} is_app_user to {is_app_user}")
        self.is_app_user = is_app_user

    def change_time_zone(self, time_zone):
        self.logger.info(f"Changing {self.full_name} time zone to {time_zone}")
        self.time_zone = time_zone

    def change_notices(self, notices):
        self.logger.info(f"Changing {self.full_name} notices to {notices}")
        self.notices = notices

    def change_crx_status(self, crx_status):
        self.logger.info(f"Changing {self.full_name} crx status to {crx_status}")
        self.crx_status = crx_status

    def change_coll_id(self, coll_id):
        self.logger.info(f"Changing {self.full_name} coll ID to {coll_id}")
        self.coll_id = coll_id
