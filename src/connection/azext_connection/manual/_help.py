# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from knack.help_files import helps
from ._validators import SOURCE_RESOURCES, TARGET_RESOURCES


for source in SOURCE_RESOURCES:
    helps['{source} connection'.format(source=source.value)] = """
        type: group
        short-summary: Manage {source} connections
    """.format(source=source.value)

    helps['{source} connection list-support-types'.format(source=source.value)] = """
        type: command
        short-summary: List target resource types and auth types supported by {source} connections.
        examples:
          - name: List all {source} supported target resource types and auth types
            text: |-
                  az {source} connection list-support-types -o table
          - name: List {source} supported auth types for a specific target resource type
            text: |-
                  az {source} connection list list-support-types --target-type storage-blob -o table
    """.format(source=source.value)

    helps['{source} connection list'.format(source=source.value)] = """
      type: command
      short-summary: List connections which connects to a {source}.
      examples:
        - name: List {source} connections interactively
          text: |-
                 az {source} connection list
        - name: List {source} connections by source resource id
          text: |-
                 az {source} connection list --source-id "ResourceId"
    """.format(source=source.value)

    helps['{source} connection delete'.format(source=source.value)] = """
      type: command
      short-summary: Delete a {source} connection.
      examples:
        - name: Delete a {source} connection interactively
          text: |-
                 az {source} connection delete
        - name: Delete a {source} connection by connection id
          text: |-
                 az {source} connection delete --id "ConnectionId"
    """.format(source=source.value)

    helps['{source} connection list-configuration'.format(source=source.value)] = """
      type: command
      short-summary: List source configurations of a {source} connection.
      examples:
        - name: List a connection's source configurations interactively
          text: |-
                 az {source} connection list-configuration
        - name: List a connection's source configurations by connection id
          text: |-
                 az {source} connection list-configuration --id "ConnectionId"
    """.format(source=source.value)

    helps['{source} connection validate'.format(source=source.value)] = """
      type: command
      short-summary: Validate a {source} connection.
      examples:
        - name: Validate a connection interactively
          text: |-
                 az {source} connection validate
        - name: Validate a connection by connection id
          text: |-
                 az {source} connection validate --id "ConnectionId"
    """.format(source=source.value)

    helps['{source} connection wait'.format(source=source.value)] = """
      type: command
      short-summary: Place the CLI in a waiting state until a condition of the connection is met.
      examples:
          - name: Wait until the connection is successfully created.
            text: |-
                   az {source} connection wait --id "ConnectionId" --created
    """.format(source=source.value)

    helps['{source} connection show'.format(source=source.value)] = """
      type: command
      short-summary: Get the details of a {source} connection.
      examples:
          - name: Get a connection interactively
            text: |-
                   az {source} connection show
          - name: Get a connection by connection id
            text: |-
                   az {source} connection show --id "ConnectionId"
    """.format(source=source.value)

    helps['{source} connection create'.format(source=source.value)] = """
      type: group
      short-summary: Create a {source} connection
    """.format(source=source.value)

    for target in TARGET_RESOURCES:
        helps['{source} connection create {target}'.format(source=source.value, target=target.value)] = """
          type: command
          short-summary: Create a {source} connection with {target}.
          parameters:
            - name: --secret
              short-summary: The secret auth info
              long-summary: |
                Usage: --secret name=XX secret=XX

                name    : Username or account name for secret auth.
                secret  : Password or account key for secret auth.
            - name: --service-principal
              short-summary: The service principal auth info
              long-summary: |
                Usage: --service-principal id=XX name=XX

                id      : Required. Client Id fo the service principal.
                name    : Required. Name of the service principal.        
            - name: --user-identity
              short-summary: The user assigned identity auth info
              long-summary: |
                Usage: --user-identity id=XX

                id      : Required. Client Id of the user assigned managed identity.
            - name: --system-identity
              short-summary: The system assigned identity auth info
              long-summary: |
                Usage: --system-identity

          examples:
            - name: Create a connection between {source} and {target} interactively
              text: |-
                     az {source} connection {target} create
            - name: Create a connection between {source} and {target}
              text: |-
                     az {source} connection {target} create --name "ConnectionName" --source-id "SourceResourceId" --target-id "TargetResourceId" --secret-auth-info name=XX secret=XX --client-type python
        """.format(source=source.value, target=target.value)