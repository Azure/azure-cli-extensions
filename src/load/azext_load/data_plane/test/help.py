helps = {}

helps[
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

helps[
    "load test list"
] = """
type: command
short-summary: List all tests.
long-summary: List all tests in the given load test resource.
"""

helps[
    "load test show"
] = """
type: command
short-summary: Show details of a test.
long-summary: Show details of the test identified by given test-id.
"""
