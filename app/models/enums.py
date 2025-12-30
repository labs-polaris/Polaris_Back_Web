from enum import Enum


class OrgRole(str, Enum):
    owner = "owner"
    admin = "admin"
    member = "member"


class ServiceType(str, Enum):
    WEB = "WEB"
    API = "API"
    BATCH = "BATCH"
    OTHER = "OTHER"


class EnvironmentType(str, Enum):
    PROD = "PROD"
    STAGE = "STAGE"
    DEV = "DEV"


class PolicyType(str, Enum):
    SLA = "SLA"
    SEVERITY_MAPPING = "SEVERITY_MAPPING"
    PR_GATE = "PR_GATE"


class IntegrationProvider(str, Enum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    JIRA = "JIRA"
    SLACK = "SLACK"
