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
examples:
    - name: Create a test run for a test and wait for test run completion.
      text: |
        az load test-run create --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {test_id} --test-run-id {test_run_id} --wait
    - name: Rerun an existing test run.
      text: |
        az load test-run create --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {test_id} --test-run-id {test_run_id} --description {description} --existing-test-run-id {existing_test_run_id}
"""

helps[
    "load test-run list"
] = """
type: command
short-summary: List all test runs.
examples:
    - name: List all tests runs in a test.
      text: |
        az load test-run list --load-test-resource {load_test_resource} --resource-group {resource_group} --test-id {test_id}
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
        az load test-run show --load-test-resource {load_test_resource} --resource-group {resource_group} --test-run-id {test_run_id}
"""

helps[
    "load test-run update"
] = """
type: command
short-summary: Update existing load test run.
examples:
    - name: Get the details of a test run.
      text: |
        az load test-run show --load-test-resource {load_test_resource} --resource-group {resource_group} --test-run-id {test_run_id}
"""

helps[
    "load test-run stop"
] = """
type: command
short-summary: Stop running a load test run.
examples:
    - name: Stop a test run.
      text: |
        az load test-run stop --load-test-resource {load_test_resource} --resource-group {resource_group} --test-run-id {test_run_id} --yes
"""

helps[
    "load test-run delete"
] = """
type: command
short-summary: Delete an existing load test run.
examples:
    - name: Delete a test run.
      text: |
        az load test-run delete --load-test-resource {load_test_resource} --resource-group {resource_group} --test-run-id {test_run_id} --yes
"""

helps[
    "load test-run download-files"
] = """
type: command
short-summary: Download files for an existing load test run.
examples:
    - name: Download input, log and result files for a test run. The directory should already exist.
      text: |
        az load test-run download-files --load-test-resource {load_test_resource} --resource-group {resource_group} --test-run-id {test_run_id} --path {path} --input --log --result
    - name: Download input and log files for a test run by creating the directory if it does not exist. 
      text: |
        az load test-run download-files --load-test-resource {load_test_resource} --resource-group {resource_group} --test-run-id {test_run_id} --path {path} --input --log --force
"""

helps[
    "load test-run app-component add"
] = """
type: command
short-summary: Add an app component to a test run.
examples:
    - name: Add an app component to a test run.
      text: |
        az load test-run app-component add --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --app-component-name {app_component_name} --app-component-type {app_component_type} --app-component-id {app_component_id}
"""

helps[
    "load test-run app-component list"
] = """
type: command
short-summary: List all app component of a test run.
examples:
    - name: List all app components for a test run.
      text: |
        az load test-run app-component list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} 
"""

helps[
    "load test-run app-component remove"
] = """
type: command
short-summary: Remove an app component from a test run.
examples:
    - name: Remove an app component from a test run.
      text: |
        az load test-run app-component remove --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --app-component-id {app_component_id} --yes
"""

helps[
    "load test-run server-metric add"
] = """
type: command
short-summary: Add a server-metric to a test run.
examples:
    - name: Add a server metric for an app component to a test run.
      text: |
        az load test-run server-metric add --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-id {server_metric_id} --metric-name {server_metric_name} --metric-namespace {server_metric_namespace} --aggregation {aggregation} --app-component-type {app_component_type} --app-component-id {app_component_id}
"""

helps[
    "load test-run server-metric list"
] = """
type: command
short-summary: List all server-metrics of a test run.
examples:
    - name: List all server metrics for a test run.
      text: |
        az load test-run server-metric list --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group}
"""

helps[
    "load test-run server-metric remove"
] = """
type: command
short-summary: Remove a server-metric from a test run.
examples:
    - name: Remove a server metric from a test run.
      text: |
        az load test-run server-metric remove --test-run-id {test_run_id} --load-test-resource {load_test_resource} --resource-group {resource_group} --metric-id {server_metric_id} --yes
"""

helps[
    "load test-run metrics get-namespaces"
] = """
type: command
short-summary: Get all metric namespaces for a load test run.
long-summary: Get all metric namespaces for a load test run.
"""

helps[
    "load test-run metrics list"
] = """
type: command
short-summary: List metrics for a load test run.
long-summary: List metrics for a load test run.
"""

helps[
    "load test-run metrics get-definitions"
] = """
type: command
short-summary: Get all metric definitions for a load test run.
long-summary: Get all metric definitions for a load test run.
"""

helps[
    "load test-run metrics get-dimensions"
] = """
type: command
short-summary: Get all metric dimensions for a load test run.
long-summary: Get all metric dimensions for a load test run.
"""
