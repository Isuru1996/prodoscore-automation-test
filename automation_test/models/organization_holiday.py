from dataclasses import dataclass
from typing import Optional

from automation_lib.core import BaseModel


@dataclass
class OrganizationHoliday(BaseModel):
    model_name: str = "OrganizationHolidayModel"
    id: Optional[int] = None
    domain_id: int = 0
    date: str = ""
    status: int = 0
    updated_status: int = 0

    def commit(self, db_util) -> None:
        """
        Commits the current state of the OrganizationHoliday object to the database.
        Args:
            db_util: Database utility with an update_data method
        """
        self.logger.info(
            f"Committing changes for organization holiday (ID: {self.id}, Date: {self.date})"
        )
        row_to_update = {
            "domain_id": self.domain_id,
            "date": self.date,
            "status": self.status,
            "updated_status": self.updated_status,
        }
        db_util.update_data(
            "proapp_organization_holiday", row_to_update, f"id = '{self.id}'"
        )

    def change_date(self, new_date: str) -> None:
        self.logger.info(
            f"Changing organization holiday date from {self.date} to {new_date}"
        )
        self.date = new_date

    def change_status(self, new_status: int) -> None:
        self.logger.info(f"Changing organization holiday status to {new_status}")
        self.status = new_status

    def change_updated_status(self, new_updated_status: int) -> None:
        self.logger.info(
            f"Changing organization holiday updated_status to {new_updated_status}"
        )
        self.updated_status = new_updated_status
