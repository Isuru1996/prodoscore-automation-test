from enum import Enum


class Department(Enum):
    UNASSIGNED = (1, "Unassigned")
    ADMINISTRATION = (2, "Administration")
    AUDIT = (3, "Audit")
    CONSTRUCTION_AND_DEVELOPMENT = (4, "Construction and Development")
    CUSTOMER = (5, "Customer")
    EXTERNAL_RELATIONS = (6, "External Relations")
    FINANCE = (7, "Finance")
    MANAGER_DEPARTMENT = (8, "Manager Department")
    LEGAL_AND_COMPLIANCE = (9, "Legal and Compliance")
    PEOPLE = (10, "People")
    PROCUREMENT = (11, "Procurement")
    SAFETY_AND_SECURITY = (12, "Safety and Security")
    STRATEGIC_INITIATIVES = (13, "Strategic Initiatives")
    PRODUCT_ENGINEERING = (14, "Product Engineering")
    DATA_ANALYTICS = (15, "Data Analytics")
    QUALITY_ASSURANCE = (16, "Quality Assurance")
    CUSTOMER_SUCCESS = (17, "Customer Success")
    INFORMATION_TECHNOLOGY = (18, "Information Technology")
    SALES_AND_MARKETING = (19, "Sales and Marketing")
    CLOUD_OPERATIONS = (20, "Cloud Operations")
    BUSINESS_INTELLIGENCE = (21, "Business Intelligence")
    HUMAN_RESOURCES = (22, "Human Resources")
    TRAINING_AND_DEVELOPMENT = (23, "Training and Development")
    SUPPORT_SERVICES = (24, "Support Services")
    RESEARCH_AND_INNOVATION = (25, "Research and Innovation")

    @property
    def id(self):
        return self.value[0]

    @property
    def name_str(self):
        return self.value[1]

    @classmethod
    def get_department_name_by_id(cls, id):
        for dept in cls:
            if dept.id == id:
                return dept.name_str
        raise ValueError(f"Invalid department ID: {id}")
