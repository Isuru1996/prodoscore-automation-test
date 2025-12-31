from enum import Enum


class EmployeeStatus(Enum):
    ACTIVE = 1
    INACTIVE = 0

    @property
    def status_val(self):
        return self.value
