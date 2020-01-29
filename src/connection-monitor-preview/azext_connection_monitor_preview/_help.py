# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


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