from enum import Enum


class Status(Enum):
    VISIBLE = 1
    HIDDEN = 0

    @property
    def val(self):
        return self.value
