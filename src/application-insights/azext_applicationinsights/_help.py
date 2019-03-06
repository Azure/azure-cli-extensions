# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps

# pylint: disable=line-too-long

helps['monitor app-insights'] = """
    type: group
    short-summary: Commands for querying data in Application Insights applications.
    parameters:
      - name: --offset
        short-summary: >
          Time offset of the query range, in ##d##h format.
        long-summary: >
          Can be used with either --start-time or --end-time. If used with --start-time, then
          the end time will be calculated by adding the offset. If used with --end-time (default), then
          the start time will be calculated by subtracting the offset. If --start-time and --end-time are
          provided, then --offset will be ignored.
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
          az monitor app-insights query --app e292531c-eb03-4079-9bb0-fe6b56b99f8b --analytics-query 'requests | summarize count() by bin(timestamp, 1h)' --offset P3DT12H
"""

helps['monitor app-insights metrics show'] = """
    type: command
    short-summary: View the value of a single metric.
    parameters:
      - name: --interval
        short-summary: >
          The interval over which to aggregate metrics, in ##h##m format.
    examples:
      - name: View the count of availabilityResults events.
        text: |
          az monitor app-insights metrics show --app e292531c-eb03-4079-9bb0-fe6b56b99f8b --metric availabilityResults/count
"""

helps['monitor app-insights metrics get-metadata'] = """
    type: command
    short-summary: Get the metadata for metrics on a particular application.
    examples:
      - name: Views the metadata for the provided app.
        text: |
          az monitor app-insights metrics get-metadata --app e292531c-eb03-4079-9bb0-fe6b56b99f8b
"""

helps['monitor app-insights events show'] = """
    type: command
    short-summary: List events by type or view a single event from an application, specified by type and ID.
    examples:
      - name: Get an availability result by ID.
        text: |
          az monitor app-insights events show --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults --event b2cf08df-bf42-4278-8d2c-5b55f85901fe
      - name: List availability results from the last 24 hours.
        text: |
          az monitor app-insights events show --app 578f0e27-12e9-4631-bc02-50b965da2633 --type availabilityResults --offset 24h
"""
