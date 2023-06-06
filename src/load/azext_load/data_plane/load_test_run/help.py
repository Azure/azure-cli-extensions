# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

helps = {}

helps[
    "load test-run create"
] = """
type: command
short-summary: Create new load test run.
long-summary: Create a new load test run.
"""

helps[
    "load test-run list"
] = """
type: command
short-summary: List all test runs.
long-summary: List all test runs in the given load test resource.
"""

helps[
    "load test-run show"
] = """
type: command
short-summary: Show details of test run.
long-summary: Show details of the test run identified by given test-run-id.
"""

helps[
    "load test-run update"
] = """
type: command
short-summary: Update existing load test run.
long-summary: Update an existing load test run.
"""

helps[
    "load test-run stop"
] = """
type: command
short-summary: Stop running load test run.
long-summary: Stop a running load test run.
"""

helps[
    "load test-run delete"
] = """
type: command
short-summary: Delete existing load test run.
long-summary: Delete an existing load test run.
"""

helps[
    "load test-run download-files"
] = """
type: command
short-summary: Download files of existing load test run.
long-summary: Download files of an existing load test run.
"""

helps[
    "load test-run app-component add"
] = """
type: command
short-summary: Add app component to test run.
long-summary: Add app component to an existing load test run.
"""

helps[
    "load test-run app-component list"
] = """
type: command
short-summary: List all app component of test run.
long-summary: List all app component of a test run.
"""

helps[
    "load test-run app-component remove"
] = """
type: command
short-summary: Remove an app component from test run.
long-summary: Remove the given app component from the test run.
"""

helps[
    "load test-run server-metric add"
] = """
type: command
short-summary: Add server-metrics to test run.
long-summary: Add server-metrics to an existing load test run.
"""

helps[
    "load test-run server-metric list"
] = """
type: command
short-summary: List all server-metrics of test run.
long-summary: List all server-metrics of a test run.
"""

helps[
    "load test-run server-metric remove"
] = """
type: command
short-summary: Remove an server-metrics from test run.
long-summary: Remove the given server-metrics from the test run.
"""

helps[
    "load test-run metrics get-namespaces"
] = """
type: command
short-summary: Get all metric namespaces for load test run.
long-summary: Get all metric namespaces for a load test run.
examples:
    - name: Get metric namespace for a load test run.
      text: |
        az load test-run metrics get-namespaces --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group}
"""

helps[
    "load test-run metrics list"
] = """
type: command
short-summary: List metrics for load test run.
long-summary: List metrics for a load test run.
examples:
    - name: List all metrics for a given load test run and metric namespace.
      text: |
        az load test-run metrics list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics
    - name: List Virtual Users metrics for a given load test run.
      text: |
        az load test-run metrics list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics --metric-name VirtualUsers
    - name: List Virtual Users metrics for a given load test run, time period and aggregation interval.
      text: |
        az load test-run metrics list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics --metric-name VirtualUsers --start-time 2023-01-01T15:16:17Z --end-time 2023-01-01T16:17:18Z --interval PT5M
    - name: List Response Time metrics for a given load test run and all dimension filters.
      text: |
        az load test-run metrics list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --dimension-filters *
    - name: List Response Time metrics for a given load test run and all values for a specific dimension.
      text: |
        az load test-run metrics list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --dimension-filters RequestName=*
    - name: List Response Time metrics for a given load test run and specific dimensions.
      text: |
        az load test-run metrics list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --dimension-filters RequestName=Homepage RequestName=Homepage-1
"""

helps[
    "load test-run metrics get-definitions"
] = """
type: command
short-summary: Get all metric definitions for load test run.
long-summary: Get all metric definitions for a load test run.
examples:
    - name: Get metric definitions for a given load test run and test run metric namespace.
      text: |
        az load test-run metrics get-definitions --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics
    - name: Get metric definitions for a given load test run and engine health metric namespace.
      text: |
        az load test-run metrics get-definitions --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace EngineHealthMetrics
"""

helps[
    "load test-run metrics get-dimensions"
] = """
type: command
short-summary: Get all metric dimension values for load test run.
long-summary: Get all metric dimension values for a load test run.
examples:
    - name: Get CPU metric dimension values for a given load test run.
      text: |
        az load test-run metrics get-dimensions --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace EngineHealthMetrics --metric-name CPU --metric-dimension EngineId
    - name: Get Response Time metric dimension values for a given load test run, time period and aggregation interval.
      text: |
        az load test-run metrics get-dimensions --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --metric-dimension RequestName --start-time 2023-01-01T15:16:17Z --end-time 2023-01-01T16:17:18Z --interval PT5M
"""
