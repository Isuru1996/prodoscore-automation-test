from enum import Enum


class ViewStatus(Enum):
    COMPANY = 3  # role >= 15000
    TEAM = 2  # role >= 10000 AND role < 15000
    SELF = 1  # role < 10000

    @property
    def val(self):
        return self.value
