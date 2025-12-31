from enum import Enum


class Role(Enum):
    NO_BASE_ROLE = (-3, "No Base Role")
    SERVICE_ACCOUNT = (-2, "Service Account")
    TERMINATED = (-1, "Terminated")
    NOT_ACTIVATED = (0, "Not Activated")
    ADMINISTRATOR = (15000, "Administrator")
    MANAGER = (10000, "Manager")
    CONTRACTOR = (1, "Contractor")
    SALES = (2, "Sales")
    LEGAL = (12, "Legal")
    MARKETING = (13, "Marketing")
    IT = (14, "IT")
    SUPPORT = (15, "Support")
    OUTSIDE_SALES = (16, "Outside Sales")
    INSIDE_SALES = (17, "Inside Sales")
    CHANNEL_SALES = (18, "Channel Sales")
    SALES_SUPPORT = (19, "Sales Support")
    BUSINESS_DEVELOPMENT = (20, "Business Development")
    ACCOUNT_MANAGER = (21, "Account Manager")
    SUPPLY_CHAIN_MANAGEMENT = (22, "Supply Chain Management")
    PROCUREMENT = (23, "Procurement")
    PROJECT_MANAGEMENT = (24, "Project Management")
    RECRUITER = (25, "Recruiter")

    @property
    def id(self):
        return self.value[0]

    @property
    def name_str(self):
        return self.value[1]

    @classmethod
    def get_role_name_by_id(cls, id):
        for role in cls:
            if role.id == id:
                return role.name_str
        raise ValueError(f"Invalid Role ID: {id}")
