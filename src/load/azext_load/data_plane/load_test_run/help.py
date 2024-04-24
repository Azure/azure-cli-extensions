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
short-summary: Create a new load test run.
long-summary: Create a new load test run for a given test. If an existing test run is specified, then the test run will be rerun. By default this command will wait for the test run to complete. Use --no-wait to skip this wait.
examples:
    - name: Create a test run for a test without waiting for test run completion.
      text: |
        az load test-run create --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-test-id --test-run-id sample-test-run-id --no-wait
    - name: Rerun an existing test run.
      text: |
        az load test-run create --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-test-id --test-run-id sample-test-run-id --description "Test run description" --existing-test-run-id existing_test_run_id
"""

helps[
    "load test-run list"
] = """
type: command
short-summary: List all test runs.
examples:
    - name: List all tests runs in a test.
      text: |
        az load test-run list --load-test-resource sample-alt-resource --resource-group sample-rg --test-id sample-test-id
"""

helps[
    "load test-run show"
] = """
type: command
short-summary: Show details of a test run.
long-summary: Show details of the test run identified by given test-run-id.
examples:
    - name: Get the details of a test run.
      text: |
        az load test-run show --load-test-resource sample-alt-resource --resource-group sample-rg --test-run-id sample-test-run-id
"""

helps[
    "load test-run update"
] = """
type: command
short-summary: Update an existing load test run.
examples:
    - name: Update the description for a test run
      text: |
        az load test-run update --load-test-resource sample-alt-resource --resource-group sample-rg --test-run-id sample-test-run-id --description "Test run description"
"""

helps[
    "load test-run stop"
] = """
type: command
short-summary: Stop running a load test run.
examples:
    - name: Stop a test run.
      text: |
        az load test-run stop --load-test-resource sample-alt-resource --resource-group sample-rg --test-run-id sample-test-run-id --yes
"""

helps[
    "load test-run delete"
] = """
type: command
short-summary: Delete an existing load test run.
examples:
    - name: Delete a test run.
      text: |
        az load test-run delete --load-test-resource sample-alt-resource --resource-group sample-rg --test-run-id sample-test-run-id --yes
"""

helps[
    "load test-run download-files"
] = """
type: command
short-summary: Download files for an existing load test run.
examples:
    - name: Download input, log and result files for a test run. The directory should already exist.
      text: |
        az load test-run download-files --load-test-resource sample-alt-resource --resource-group sample-rg --test-run-id sample-test-run-id --path ~/Downloads/OutputArtifacts --input --log --result
    - name: Download input and log files for a test run by creating the directory if it does not exist.
      text: |
        az load test-run download-files --load-test-resource sample-alt-resource --resource-group sample-rg --test-run-id sample-test-run-id --path ~/Downloads/OutputArtifacts --input --log --force
"""

helps[
    "load test-run app-component add"
] = """
type: command
short-summary: Add an app component to a test run.
examples:
    - name: Add an app component to a test run.
      text: |
        az load test-run app-component add --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --app-component-name appcomponentresource --app-component-type microsoft.insights/components --app-component-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/samplerg/providers/microsoft.insights/components/appcomponentresource" --app-component-kind web
"""

helps[
    "load test-run app-component list"
] = """
type: command
short-summary: List all app components for a test run.
examples:
    - name: List all app components for a test run.
      text: |
        az load test-run app-component list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test-run app-component remove"
] = """
type: command
short-summary: Remove an app component from a test run.
examples:
    - name: Remove an app component from a test run.
      text: |
        az load test-run app-component remove --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --app-component-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/app-comp-name --yes
"""

helps[
    "load test-run server-metric add"
] = """
type: command
short-summary: Add a server-metric to a test run.
examples:
    - name: Add a server metric for an app component to a test run.
      text: |
        az load test-run server-metric add --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/sample-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU" --metric-name  "Percentage CPU" --metric-namespace microsoft.compute/virtualmachinescalesets --aggregation Average --app-component-type Microsoft.Compute/virtualMachineScaleSets --app-component-id /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/app-comp-name
"""

helps[
    "load test-run server-metric list"
] = """
type: command
short-summary: List all server-metrics for a test run.
examples:
    - name: List all server metrics for a test run.
      text: |
        az load test-run server-metric list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test-run server-metric remove"
] = """
type: command
short-summary: Remove a server-metric from a test run.
examples:
    - name: Remove a server metric from a test run.
      text: |
        az load test-run server-metric remove --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-id "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Sample-rg/providers/Microsoft.Compute/virtualMachineScaleSets/Sample-temp-vmss/providers/microsoft.insights/metricdefinitions/Percentage CPU" --yes
"""

helps[
    "load test-run metrics get-namespaces"
] = """
type: command
short-summary: Get all metric namespaces for a load test run.
examples:
    - name: Get metric namespace for a load test run.
      text: |
        az load test-run metrics get-namespaces --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg
"""

helps[
    "load test-run metrics list"
] = """
type: command
short-summary: List metrics for a load test run.
examples:
    - name: List all metrics for a given load test run and metric namespace.
      text: |
        az load test-run metrics list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics
    - name: List Virtual Users metrics for a given load test run.
      text: |
        az load test-run metrics list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics --metric-name VirtualUsers
    - name: List Virtual Users metrics for a given load test run, time period and aggregation interval.
      text: |
        az load test-run metrics list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics --metric-name VirtualUsers --start-time 2023-01-01T15:16:17Z --end-time 2023-01-01T16:17:18Z --interval PT5M
    - name: List Response Time metrics for a given load test run and all dimension filters.
      text: |
        az load test-run metrics list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --dimension-filters *
    - name: List Response Time metrics for a given load test run and all values for a specific dimension.
      text: |
        az load test-run metrics list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --dimension-filters RequestName=*
    - name: List Response Time metrics for a given load test run and specific dimensions.
      text: |
        az load test-run metrics list --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --dimension-filters RequestName=Homepage RequestName=Homepage-1
"""

helps[
    "load test-run metrics get-definitions"
] = """
type: command
short-summary: Get all metric definitions for a load test run.
examples:
    - name: Get metric definitions for a given load test run and test run metric namespace.
      text: |
        az load test-run metrics get-definitions --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics
    - name: Get metric definitions for a given load test run and engine health metric namespace.
      text: |
        az load test-run metrics get-definitions --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace EngineHealthMetrics
"""

helps[
    "load test-run metrics get-dimensions"
] = """
type: command
short-summary: Get all metric dimension values for load test run.
examples:
    - name: Get CPU metric dimension values for a given load test run.
      text: |
        az load test-run metrics get-dimensions --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace EngineHealthMetrics --metric-name CPU --metric-dimension EngineId
    - name: Get Response Time metric dimension values for a given load test run, time period and aggregation interval.
      text: |
        az load test-run metrics get-dimensions --test-run-id sample-test-run-id --load-test-resource sample-alt-resource --resource-group sample-rg --metric-namespace LoadTestRunMetrics --metric-name ResponseTime --metric-dimension RequestName --start-time 2023-01-01T15:16:17Z --end-time 2023-01-01T16:17:18Z --interval PT5M
"""
