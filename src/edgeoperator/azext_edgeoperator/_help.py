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
            --to-date 2026-01-02T00:00:00Z --save-to-path C:\\Logs\\IndirectCollection --username operator
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

helps["aldo billing-configuration"] = """
    type: group
    short-summary: Manage the ALDO billing configuration.
    long-summary: The current subscription must be the Operator subscription.
"""

helps["aldo billing-configuration show"] = """
    type: command
    short-summary: Show the active ALDO billing configuration.
    examples:
      - name: Show the active billing configuration.
        text: az aldo billing-configuration show
"""

helps["aldo billing-configuration create"] = """
    type: command
    short-summary: Create or fully replace the active ALDO billing configuration.
    long-summary: >-
        Sends a PUT request for the default singleton. This replaces the configuration rather than merging changes.
        Each successful PUT also creates an immutable snapshot.
        Use --manifest to send the Azure-issued billing configuration unchanged, which is required when it includes
        licenses or signatures. Otherwise, provide the individual billing arguments.
    examples:
      - name: Replace the billing configuration with an Azure-issued manifest file.
        text: az aldo billing-configuration create --manifest billing-manifest.json
      - name: Replace the billing configuration using individual arguments.
        text: >-
            az aldo billing-configuration create
            --disconnected-operation /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/rg-aldo/providers/Microsoft.Edge/disconnectedOperations/example
            --stamp-id 11111111-1111-1111-1111-111111111111 --location eastus --billing-model Capacity
            --connection-intent Disconnected --auto-renew Enabled --billing-status Enabled
            --cores 12 --pricing-model Annual --start-date 2026-01-01 --end-date 2026-12-31
"""

helps["aldo billing-configuration snapshot"] = """
    type: group
    short-summary: View immutable snapshots of previous ALDO billing configurations.
"""

helps["aldo billing-configuration snapshot show"] = """
    type: command
    short-summary: Show a billing configuration snapshot.
    examples:
      - name: Show a snapshot by a name returned from 'az aldo billing-configuration snapshot list'.
        text: az aldo billing-configuration snapshot show --name 0b008b2d-0000-0100-0000-6789abcd0000
"""

helps["aldo billing-configuration snapshot list"] = """
    type: command
    short-summary: List billing configuration snapshots.
    examples:
      - name: List billing configuration snapshots as a table.
        text: az aldo billing-configuration snapshot list --output table
"""
