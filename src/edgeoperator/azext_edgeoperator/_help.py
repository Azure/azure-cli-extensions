from knack.help_files import helps


helps["aldo"] = """
    type: group
    short-summary: Manage Azure Local Disconnected Operations resources.
"""

helps["aldo system-readiness"] = """
    type: group
    short-summary: Manage ALDO system readiness.
"""

helps["aldo system-readiness show"] = """
    type: command
    short-summary: Show the current ALDO system readiness status.
    long-summary: Retrieves the read-only system readiness singleton for the current subscription.
"""
