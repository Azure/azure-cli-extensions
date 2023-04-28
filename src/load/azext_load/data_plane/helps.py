dataplane_helps = {}
dataplane_helps[
    "load test"
] = """
type: group
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

