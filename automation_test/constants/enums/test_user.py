from enum import Enum


class TestUser(Enum):
    """Enum for test user identifiers."""

    __test__ = False

    LOGIN_USER = "login_user"
    USER_1 = "user_1"
    USER_2 = "user_2"
    USER_3 = "user_3"
    USER_4 = "user_4"
    USER_5 = "user_5"
    USER_6 = "user_6"

    @property
    def val(self):
        return self.value
