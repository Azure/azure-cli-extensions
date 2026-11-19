# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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

helps["aldo observability-configuration"] = """
    type: group
    short-summary: Manage ALDO observability configuration.
"""

helps["aldo observability-configuration show"] = """
    type: command
    short-summary: Show the active ALDO observability configuration.
    long-summary: Retrieves the read-only observability configuration singleton for the current subscription.
"""

helps["aldo system-configuration"] = """
    type: group
    short-summary: Manage ALDO system configuration.
"""

helps["aldo system-configuration show"] = """
    type: command
    short-summary: Show the active ALDO system configuration.
    long-summary: Retrieves the system configuration singleton. The current subscription must be the Operator subscription.
    examples:
      - name: Show the active system configuration.
        text: az aldo system-configuration show
"""

helps["aldo system-configuration create"] = """
    type: command
    short-summary: Create or fully replace the active ALDO system configuration.
    long-summary: >-
        Sends a PUT request for the default singleton. This replaces the configuration rather than merging changes;
        omitted writable fields are not preserved.
        The service requires --dns-forwarder-ip, --connection-intent, --stamp-id, and --device-resource-id on every PUT.
        The current subscription must be the Operator subscription.
    examples:
      - name: Replace the system configuration with all four required writable values.
        text: >-
            az aldo system-configuration create --dns-forwarder-ip 192.0.2.53 --connection-intent Connected
            --stamp-id 11111111-1111-1111-1111-111111111111
            --device-resource-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-aldo/providers/Microsoft.Edge/disconnectedOperations/example-device
"""
