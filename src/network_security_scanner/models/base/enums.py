"""Common enumerations across all models."""

from enum import Enum


class DeviceType(str, Enum):
    """Supported device types."""

    CISCO_IOS = "cisco-ios"
    CISCO_ASA = "cisco-asa"
    FORTIGATE = "fortigate"
    PALOALTO = "paloalto"


class RuleAction(str, Enum):
    """Access control rule actions."""

    PERMIT = "permit"
    DENY = "deny"
    ALLOW = "allow"
    DROP = "drop"
    REJECT = "reject"


class Protocol(str, Enum):
    """Network protocols."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ESP = "esp"
    AH = "ah"
    GRE = "gre"
    OSPF = "ospf"
    EIGRP = "eigrp"
    IP = "ip"
    ANY = "any"


class Severity(str, Enum):
    """Finding severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStatus(str, Enum):
    """Compliance check status."""

    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"
    MANUAL_REVIEW = "manual_review"


class RoutingProtocolType(str, Enum):
    """Routing protocol types."""

    STATIC = "static"
    OSPF = "ospf"
    EIGRP = "eigrp"
    BGP = "bgp"
    RIP = "rip"
    IS_IS = "is-is"
