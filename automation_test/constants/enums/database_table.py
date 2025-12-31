from enum import Enum


class DatabaseTable(Enum):
    # Main database
    PROAPP_EMPLOYEE_PRODOSCORE = "proapp_employee_prodoscore"
    PROAPP_ORGANIZATION_PRODOSCORE = "proapp_organization_prodoscore"
    PROAPP_EMPLOYEE_HOLIDAY = "proapp_employee_holiday"
    PROAPP_ORGANIZATION_HOLIDAY = "proapp_organization_holiday"
    PROAPP_WORKSHIFT = "proapp_workshifts"
    PROAPP_STATISTIC = "proapp_statistic"
    PROAPP_DETAIL = "proapp_detail"
    PROAPP_NOTICE = "proapp_notice"
    PROAPP_EMPLOYEE = "proapp_employee"
    PROAPP_PRODUCT = "proapp_product"
    PROAPP_ORG_WEIGHT = "proapp_org_weight"
    PROAPP_ROLE = "proapp_role"
    PROAPP_BASELINE = "proapp_baseline"
    PROAPP_WORKING_NON_WORKING_DAYS = "proapp_working_nonworking_days"
    PROAPP_EMPLOYEE_IPADDRESS = "proapp_employee_ipaddress"
    PROAPP_IPADDRESS_ANNOTATIONS = "proapp_ipaddress_annotations"
    PROAPP_EMPLOYEE_TIMEZONE = "proapp_employee_timezone"
    PROAPP_PRODBOT_ALERTS = "proapp_prodbot_alerts"
    PROAPP_PRODBOT_ALERTS_SENT = "proapp_prodbot_alerts_sent"
    PROAPP_SFTP_IP_CONFIG = "proapp_sftp_ip_config"
    PROAPP_SLACK_STATISTICS = "proapp_slack_statistics"
    PROAPP_JIRA_OTHER_TYPE_STATISTICS = "proapp_jira_other_type_statistics"
    PROAPP_ADMIN_ACTIVITY = "proapp_admin_activity"
    PROAPP_LOGIN_ACTIVITY = "proapp_login_activity"
    # NLP database
    PROAPP_COLLAB_AGGR = "proapp_collab_aggr"
    PROAPP_EMPLOYEE_COLLABORATION = "proapp_employee_collaboration"
    PROAPP_ORGANIZATION_COLLABORATION = "proapp_organization_collaboration"

    @property
    def table_name(self):
        return self.value
