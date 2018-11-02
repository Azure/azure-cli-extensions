# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['monitor app-insights'] = """
    type: group
    short-summary: Commands for querying data in Application Insights applications.
"""

helps['monitor app-insights metrics'] = """
    type: group
    short-summary: Retrieve metrics from an application.
"""

helps['monitor app-insights events'] = """
    type: group
    short-summary: Retrieve events from an application.
"""

helps['monitor app-insights query'] = """
    type: command
    short-summary: Execute a query over data in your application.
    examples:
      - name: Execute a simple query over past 3.5 days.
        text: |
          az monitor app-insights query --app-id e292531c-eb03-4079-9bb0-fe6b56b99f8b --analytics-query "requests | summarize count() by bin(timestamp, 1h)" -t P3DT12H
"""

helps['monitor app-insights metrics show'] = """
    type: command
    short-summary: View the value of a single metric.
    examples:
      - name: View the count of availabilityResults events.
        text: |
          az monitor app-insights metrics show --app-id e292531c-eb03-4079-9bb0-fe6b56b99f8b --metric-id availabilityResults/count
"""

helps['monitor app-insights metrics get-metadata'] = """
    type: command
    short-summary: Get the metadata for metrics on a particular application.
    examples:
      - name: Views the metadata for the provided app.
        text: |
          az monitor app-insights metrics get-metadata --app-id e292531c-eb03-4079-9bb0-fe6b56b99f8b
"""

helps['monitor app-insights events show'] = """
    type: command
    short-summary: View a single event from an application, specified by type and ID.
    examples:
      - name: Get an availability result by ID.
        text: |
          az monitor app-insights events show --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --event-type availabilityResults --event-id b2cf08df-bf42-4278-8d2c-5b55f85901fe
"""

helps['monitor app-insights events list'] = """
    type: command
    short-summary: View a list of events from an application, filtered by type.
    examples:
      - name: List availability results from the last 24 hours.
        text: |
          az monitor app-insights events list --app-id 578f0e27-12e9-4631-bc02-50b965da2633 --event-type availabilityResults -t PT24H
"""
