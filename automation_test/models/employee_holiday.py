from dataclasses import dataclass
from typing import Optional

from automation_lib.core import BaseModel


@dataclass
class EmployeeHoliday(BaseModel):
    model_name: str = "EmployeeHolidayModel"
    id: Optional[int] = None
    domain_id: int = 0
    employee_id: int = 0
    date: str = ""
    source: str = ""
    status: int = 1
    updated_status: int = 1

    def commit(self, db_util) -> None:
        """
        Commits the current state of the EmployeeHoliday object to the database.
        Args:
            db_util: Database utility with an update_data method
        """
        self.logger.info(
            f"Committing changes for employee holiday (ID: {self.id}, Date: {self.date})"
        )
        row_to_update = {
            "domain_id": self.domain_id,
            "employee_id": self.employee_id,
            "date": self.date,
            "source": self.source,
            "status": self.status,
            "updated_status": self.updated_status,
        }
        db_util.update_data(
            "proapp_employee_holiday", row_to_update, f"id = '{self.id}'"
        )

    def change_date(self, new_date: str) -> None:
        self.logger.info(
            f"Changing employee holiday date from {self.date} to {new_date}"
        )
        self.date = new_date

    def change_source(self, new_source: str) -> None:
        self.logger.info(f"Changing employee holiday source to {new_source}")
        self.source = new_source

    def change_status(self, new_status: int) -> None:
        self.logger.info(f"Changing employee holiday status to {new_status}")
        self.status = new_status

    def change_updated_status(self, new_updated_status: int) -> None:
        self.logger.info(
            f"Changing employee holiday updated_status to {new_updated_status}"
        )
        self.updated_status = new_updated_status
