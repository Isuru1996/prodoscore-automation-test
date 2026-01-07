from dataclasses import dataclass
from typing import Optional


@dataclass
class EmployeeProdoscore:
    id: Optional[int] = None
    domain_id: int = 0
    employee_id: int = 0
    date: str = ""
    role: int = 0
    score: float = 0.0
    ip_int_ext: int = 0
    total_gap_time: int = 100
    total_active_time: int = 1
    gap_times: str = "[[0,210]]"
    first_last_activity_times: str = "[-1,-1]"

    def commit(self, db_util) -> None:
        """
        Commits the current state of the EmployeeProdoscore object to the database.
        Args:
            db_util: Database utility with an update_data method
        """
        row_to_update = {
            "domain_id": self.domain_id,
            "employee_id": self.employee_id,
            "date": self.date,
            "role": self.role,
            "score": self.score,
            "ip_int_ext": self.ip_int_ext,
            "total_gap_time": self.total_gap_time,
            "total_active_time": self.total_active_time,
            "gap_times": self.gap_times,
            "first_last_activity_times": self.first_last_activity_times,
        }
        db_util.update_data(
            "proapp_employee_prodoscore", row_to_update, f"id = '{self.id}'"
        )

    def change_date(self, new_date: str) -> None:
        self.date = new_date

    def change_role(self, new_role: int) -> None:
        self.role = new_role

    def change_score(self, new_score: float) -> None:
        self.score = new_score

    def change_ip_int_ext(self, new_ip_int_ext: int) -> None:
        self.ip_int_ext = new_ip_int_ext

    def change_total_gap_time(self, new_total_gap_time: int) -> None:
        self.total_gap_time = new_total_gap_time

    def change_total_active_time(self, new_total_active_time: int) -> None:
        self.total_active_time = new_total_active_time

    def change_gap_times(self, new_gap_times: str) -> None:
        self.gap_times = new_gap_times

    def change_first_last_activity_times(
        self, new_first_last_activity_times: str
    ) -> None:
        self.first_last_activity_times = new_first_last_activity_times
