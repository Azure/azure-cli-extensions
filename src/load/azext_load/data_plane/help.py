helps = {}

helps[
    "load test"
] = """
type: group
short-summary: Command group with commands related to test.
long-summary: Command group with commands related to test such as create, update, delete, list, etc.
parameters:
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
    "load test app-components"
] = """
type: group
short-summary: Command group with commands related to test app-components.
long-summary: Command group with commands related to test app-components such as add, list and remove.
parameters:
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
    "load test server-metrics"
] = """
type: group
short-summary: Command group with commands related to test server-metrics.
long-summary: Command group with commands related to test server-metrics such as add, list and remove.
parameters:
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
