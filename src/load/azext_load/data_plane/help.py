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
    - name: --resource-group, --rg, -g
      type: string
      short-summary: 'Name of the resource group'
      long-summary: |
          Name of the resource group
"""
