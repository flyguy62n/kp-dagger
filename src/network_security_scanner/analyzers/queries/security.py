"""Security analysis queries."""

# CIS Benchmark queries
CIS_QUERIES = {
    "cisco_ios": {
        "password_policy": """
            SELECT device_id, 'Weak password policy' as finding
            FROM device_configs
            WHERE device_type = 'cisco-ios'
            AND NOT (config_text LIKE '%service password-encryption%')
        """,
        "ssh_version": """
            SELECT device_id, 'SSH version not specified' as finding
            FROM device_configs
            WHERE device_type = 'cisco-ios'
            AND NOT (config_text LIKE '%ip ssh version 2%')
        """,
    },
    "cisco_asa": {
        "password_policy": """
            SELECT device_id, 'Password policy not configured' as finding
            FROM device_configs
            WHERE device_type = 'cisco-asa'
            AND NOT (config_text LIKE '%password-policy%')
        """,
    },
}

# Access control queries
ACL_QUERIES = {
    "permissive_rules": """
        SELECT device_id, acl_name, rule_number, 'Permissive ACL rule' as finding
        FROM access_lists
        WHERE action = 'permit'
        AND (source = 'any' OR destination = 'any')
    """,
}

# Best practice queries
BEST_PRACTICE_QUERIES = {
    "unused_interfaces": """
        SELECT device_id, interface_name, 'Unused interface not shutdown' as finding
        FROM interfaces
        WHERE status = 'up' AND config NOT LIKE '%description%'
    """,
}
