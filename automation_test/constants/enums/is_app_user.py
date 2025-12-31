from enum import Enum


class IsAppUser(Enum):
    ACTIVATE = 1
    DEACTIVATE = 0

    @property
    def val(self):
        return self.value
