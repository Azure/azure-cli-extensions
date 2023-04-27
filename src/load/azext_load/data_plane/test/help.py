test_helps = {}
test_helps[
    "load test create"
] = """
type: command
short-summary: Create a new test test.
long-summary: Create a new test test.
parameters:
    - name: --test-id
      type: string
      short-summary: 'Unique name for the load test'
      long-summary: |
          Unique name for the load test, must contain only lower-case alphabetic, numeric, underscore or hyphen characters. Required.
    - name: --body
      type: string
      short-summary: 'Load test model'
      long-summary: |
          Load test model. Required.
"""

test_helps[
    "load test update"
] = """
type: command
short-summary: Update an existing test.
long-summary: Update an existing test.
parameters:
    - name: --test-id
      type: string
      short-summary: 'Unique name for the load test'
      long-summary: |
          Unique name for the load test, must contain only lower-case alphabetic, numeric, underscore or hyphen characters. Required.
    - name: --body
      type: string
      short-summary: 'Load test model'
      long-summary: |
          Load test model. Required.
"""

test_helps[
    "load test list"
] = """
type: command
short-summary: List all tests.
long-summary: List all tests in the given load test resource.
parameters:
    - name: --load-test-resource
      type: string
      short-summary: 'Name or ARM resource ID of the load test resource'
      long-summary: |
          Name or ARM resource ID of the load test resource
    - name: --resource-group
      type: string
      short-summary: 'Name of the resource group'
      long-summary: |
          Name of the resource group
"""
