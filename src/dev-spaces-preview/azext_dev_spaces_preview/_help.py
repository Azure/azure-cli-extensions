# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps   # pylint: disable=import-error


# ADS command help

helps['ads'] = """
     type: group
     short-summary: (PREVIEW) Manage Azure Dev Spaces.
"""

helps['ads use'] = """
    type: command
    short-summary: (PREVIEW) Use Azure Dev Spaces with a managed Kubernetes cluster.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of resource group. You can configure the default group using 'az configure --defaults group=<name>'.
        - name: --space -s
          type: string
          short-summary: Name of the dev space to use.
        - name: --parent-space -p
          type: string
          short-summary: Name of a parent dev space to inherit from when creating a new dev space. By default, if there is already a single dev space with no parent, the new space inherits from this one.
        - name: --update
          type: bool
          short-summary: Update Azure Dev Spaces tools.
"""

helps['ads remove'] = """
    type: command
    short-summary: (PREVIEW) Remove Azure Dev Spaces from a managed Kubernetes cluster.
    parameters:
        - name: --name -n
          type: string
          short-summary: Name of the managed cluster.
        - name: --resource-group -g
          type: string
          short-summary: Name of resource group. You can configure the default group using 'az configure --defaults group=<name>'.
        - name: --yes -y
          type: bool
          short-summary: Do not prompt for confirmation.
"""
