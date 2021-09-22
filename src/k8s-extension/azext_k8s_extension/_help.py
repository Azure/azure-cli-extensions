# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
from . import consts


helps[f'{consts.EXTENSION_NAME}'] = """
    type: group
    short-summary: Commands to manage Kubernetes Extensions.
"""

helps[f'{consts.EXTENSION_NAME} create'] = f"""
    type: command
    short-summary: Create a Kubernetes Extension.
    examples:
      - name: Create a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} create --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters \\
          --name myextension --extension-type microsoft.openservicemesh \\
          --scope cluster --release-train stable
"""

helps[f'{consts.EXTENSION_NAME} list'] = f"""
    type: command
    short-summary: List Kubernetes Extensions.
    examples:
      - name: List all Kubernetes Extensions on a cluster
        text: |-
          az {consts.EXTENSION_NAME} list --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters
"""

helps[f'{consts.EXTENSION_NAME} delete'] = f"""
    type: command
    short-summary: Delete a Kubernetes Extension.
    examples:
      - name: Delete an existing Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} delete --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myextension
"""

helps[f'{consts.EXTENSION_NAME} show'] = f"""
    type: command
    short-summary: Show a Kubernetes Extension.
    examples:
      - name: Show details of a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} show --resource-group my-resource-group \\
          --cluster-name mycluster --cluster-type connectedClusters --name myextension
"""
