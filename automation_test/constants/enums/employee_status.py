from enum import Enum


class EmployeeStatus(Enum):
    ACTIVE = 1
    INACTIVE = -1

    @property
    def val(self):
        return self.value
