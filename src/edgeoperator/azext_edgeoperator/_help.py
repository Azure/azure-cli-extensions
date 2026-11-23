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

helps["aldo log-collection"] = """
    type: group
    short-summary: Collect ALDO logs and manage log collection jobs.
    long-summary: The current subscription must be the Operator subscription.
"""

helps["aldo log-collection collect"] = """
    type: command
    short-summary: Start collecting logs for a time range.
    long-summary: >-
        Starts a log collection job and, unless --no-wait is used, waits for it to finish and returns the job.
        Collection can take a long time. With --no-wait the job ID is not returned; use
        'az aldo log-collection list' to find the job and 'az aldo log-collection wait' to wait for it.
    examples:
      - name: Collect logs for one day and wait for the job to finish.
        text: az aldo log-collection collect --from-date 2026-01-01T00:00:00Z --to-date 2026-01-02T00:00:00Z
      - name: Collect logs from specific roles without waiting.
        text: >-
            az aldo log-collection collect --from-date 2026-01-01T00:00:00Z --to-date 2026-01-02T00:00:00Z
            --filter-roles Agents Oplets --no-wait
"""

helps["aldo log-collection collect-indirect"] = """
    type: command
    short-summary: Start collecting logs to a destination path.
    long-summary: >-
        Starts a log collection job that saves logs to --save-to-path and, unless --no-wait is used, waits for it
        to finish and returns the job. If --username is given without --password, you are prompted for the password.
    examples:
      - name: Collect logs to a destination path that requires credentials.
        text: >-
            az aldo log-collection collect-indirect --from-date 2026-01-01T00:00:00Z
            --to-date 2026-01-02T00:00:00Z --save-to-path \\\\fileserver\\share\\logs --username operator
"""

helps["aldo log-collection show"] = """
    type: command
    short-summary: Show a log collection job.
    examples:
      - name: Show a log collection job by its GUID.
        text: az aldo log-collection show --job-id 11111111-1111-1111-1111-111111111111
"""

helps["aldo log-collection list"] = """
    type: command
    short-summary: List log collection jobs from a date-time onward.
    long-summary: >-
        The service requires a history start time, so --from-date is required.
    examples:
      - name: List log collection jobs since the start of 2026 as a table.
        text: az aldo log-collection list --from-date 2026-01-01T00:00:00Z --output table
"""

helps["aldo log-collection wait"] = """
    type: command
    short-summary: Place the CLI in a waiting state until a log collection job finishes.
    examples:
      - name: Wait until a log collection job succeeds.
        text: az aldo log-collection wait --job-id 11111111-1111-1111-1111-111111111111 --created
"""
