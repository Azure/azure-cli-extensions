# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

helps = {}

_common_params = """parameters:
    - name: --load-test-resource, --name, -n
      type: string
      short-summary: 'Name or ARM resource ID of the load test resource'
      long-summary: |
          Name or ARM resource ID of the load test resource
    - name: --resource-group, -g
      type: string
      short-summary: 'Name of the resource group'
      long-summary: |
          Name of the resource group
"""

helps[
    "load test"
] = """
type: group
short-summary: Command group to manage load tests.
long-summary: Command group to manage load test with create, update, delete, list, etc.
""" + _common_params

helps[
    "load test app-component"
] = """
type: group
short-summary: Command group to manage app components.
long-summary: Command group to manage load test app-components with add, list and remove.
""" + _common_params

helps[
    "load test server-metric"
] = """
type: group
short-summary: Command group to manage server metrics.
long-summary: Command group to manage load test server-metrics with add, list and remove.
""" + _common_params

helps[
    "load test file"
] = """
type: group
short-summary: Command group for operations on test files.
long-summary: Command group for operations on test files such as upload, delete, list and download.
""" + _common_params

helps[
    "load test-run"
] = """
type: group
short-summary: Command group to manage load test runs.
long-summary: Command group to manage load test runs with create, update, delete, list, stop, etc.
""" + _common_params

helps[
    "load test-run app-component"
] = """
type: group
short-summary: Command group to manage load test run app components.
long-summary: Command group to manage load test run app-components with add, list and remove.
""" + _common_params

helps[
    "load test-run server-metric"
] = """
type: group
short-summary: Command group to manage load test run server-metrics.
long-summary: Command group to manage load test run server-metrics with add, list and remove.
""" + _common_params

helps[
    "load test-run metrics"
] = """
type: group
short-summary: Command group to retrieve load test run metrics.
long-summary: Command group to retrieve load test run metrics with list, get-namespaces, get-definitions, get-dimension.
""" + _common_params
