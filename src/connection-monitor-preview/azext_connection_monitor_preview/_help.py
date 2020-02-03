# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import

helps['network watcher connection-monitor create'] = """
type: command
short-summary: Create a connection monitor.
long-summary: |
  This extension allow to create V1 and V2 version of connection monitor.
  V1 connection monitor supports single source and destination endpoint which comes with V1 argument groups as usual.
  V2 connection monitor supports multiple endpoints and several test protocol which comes with V2 argument groups.
parameters:
  - name: --source-resource
    short-summary: >
        Currently only Virtual Machines are supported.
  - name: --dest-resource
    short-summary: >
        Currently only Virtual Machines are supported.
examples:
  - name: Create a connection monitor for a virtual machine.
    text: |
        az network watcher connection-monitor create -g MyResourceGroup -n MyConnectionMonitorName \\
            --source-resource MyVM
  - name: Create a V2 connection monitor
    text: >
      az network watcher connection-monitor create
      --location westus
      --name MyV2ConnectionMonitor
      --endpoint-source-name "vm01"
      --endpoint-source-resource-id MyVM01ResourceID
      --endpoint-dest-name bing
      --endpoint-dest-address bing.com
      --test-config-name TCPTestConfig
      --protocol Tcp
      --tcp-port 2048
"""


helps['network watcher connection-monitor endpoint'] = """
type: group
short-summary: Manage endpoint of a connection monitor
"""

helps['network watcher connection-monitor endpoint add'] = """
type: command
short-summary: Add an endpoint to a connection monitor
examples:
  - name: Add an endpoint as destination
    text: >
      az network watcher connection-monitor endpoint add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyEndpoint
      --address "bing.com"
      --dest-test-groups DefaultTestGroup
  - name: Add an endpoint as source
    text: >
      az network watcher connection-monitor endpoint add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyEndpoint
      --resource-id MyVMResourceID
      --source-test-groups DefaultTestGroup
  - name: Add an endpoint with filter
    text: >
      az network watcher connection-monitor endpoint add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyEndpoint
      --resource-id MyLogAnalysisWorkSpaceID
      --source-test-groups DefaultTestGroup
      --filter-type Include
      --filter-item type=AgentAddress address=npmuser
      --filter-item type=AgentAddress address=pypiuser
"""

helps['network watcher connection-monitor endpoint remove'] = """
type: command
short-summary: Remove an endpoint from a connection monitor
examples:
  - name: Remove endpoint from all test groups of a connection monitor
    text: >
      az network watcher connection-monitor endpoint remove
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyEndpoint
  - name: Remove endpoint from two test groups of a connection monitor
    text: >
      az network watcher connection-monitor endpoint remove
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyEndpoint
      --test-groups DefaultTestGroup HealthCheckTestGroup
"""

helps['network watcher connection-monitor endpoint show'] = """
type: command
short-summary: Show an endpoint from a connection monitor
"""

helps['network watcher connection-monitor endpoint list'] = """
type: command
short-summary: List all endpoints form a connection monitor
"""

helps['network watcher connection-monitor test-configuration'] = """
type: group
short-summary: Manage test configuration of a connection monitor
"""

helps['network watcher connection-monitor test-configuration add'] = """
type: command
short-summary: Add a test configuration to a connection monitor
examples:
  - name: Add a test configuration with HTTP supported
    text: >
      az network watcher connection-monitor test-configuration add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyHTTPTestConfiguration
      --test-groups DefaultTestGroup
      --protocol Http
      --http-request-header name=Host value=bing.com
      --http-request-header name=UserAgent value=Edge
  - name: Add a test configuration with TCP supported
    text: >
      az network watcher connection-monitor test-configuration add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyHTTPTestConfiguration
      --test-groups TCPTestGroup DefaultTestGroup
      --protocol Tcp
      --tcp-port 4096
"""

helps['network watcher connection-monitor test-configuration remove'] = """
type: command
short-summary: Remove a test configuration from a connection monitor
examples:
  - name: Remove a test configuration from all test groups of a connection monitor
    text: >
      az network watcher connection-monitor test-configuration remove
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyTCPTestConfiguration
  - name: Remove a test configuration from two test groups of a connection monitor
    text: >
      az network watcher connection-monitor test-configuration remove
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyHTTPTestConfiguration
      --test-groups HTTPTestGroup DefaultTestGroup
"""

helps['network watcher connection-monitor test-configuration show'] = """
type: command
short-summary: Show a test configuration from a connection monitor
"""

helps['network watcher connection-monitor test-configuration list'] = """
type: command
short-summary: List all test configurations of a connection monitor
"""

helps['network watcher connection-monitor test-group'] = """
type: group
short-summary: Manage a test group of a connection monitor
"""

helps['network watcher connection-monitor test-group add'] = """
type: command
short-summary: Add a test group along with new-added/existing endpoint and test configuration to a connection monitor
examples:
  - name: Add a test group along with existing endpoint and test configuration via their names
    text: >
      az network watcher connection-monitor test-group add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyHTTPTestGroup
      --endpoint-source-name MySourceEndpoint
      --endpoint-dest-name MyDestinationEndpoint
      --test-config-name MyTestConfiguration
  - name: Add a test group long with new-added source endpoint and existing test configuration via its name
    text: >
      az network watcher connection-monitor test-group add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyAccessibilityTestGroup
      --endpoint-source-name MySourceEndpoint
      --endpoint-source-resource-id MyLogAnalysisWorkspaceID
      --endpoint-dest-name MyExistingDestinationEndpoint
      --test-config-name MyExistingTestConfiguration
  - name: Add a test group along with new-added endpoints and test configuration
    text: >
      az network watcher connection-monitor test-group add
      --connection-monitor MyConnectionMonitor
      --location westus
      --name MyAccessibilityTestGroup
      --endpoint-source-name MySourceEndpoint
      --endpoint-source-resource-id MyVMResourceID
      --endpoint-dest-name bing
      --endpoint-dest-address bing.com
      --test-config-name MyNewTestConfiguration
      --protocol Tcp
      --tcp-port 4096
"""

helps['network watcher connection-monitor test-group remove'] = """
type: command
short-summary: Remove test group from a connection monitor
"""

helps['network watcher connection-monitor test-group show'] = """
type: command
short-summary: Show a test group of a connection monitor
"""

helps['network watcher connection-monitor test-group list'] = """
type: command
short-summary: List all test groups of a connection monitor
"""

helps['network watcher connection-monitor output'] = """
type: group
short-summary: Manage output of connection monitor
"""

helps['network watcher connection-monitor output add'] = """
type: command
short-summary: Add an output to a connection monitor
"""

helps['network watcher connection-monitor output remove'] = """
type: command
short-summary: Remove all outputs from a connection monitor
"""

helps['network watcher connection-monitor output list'] = """
type: command
short-summary: List all output from a connection monitor
"""
