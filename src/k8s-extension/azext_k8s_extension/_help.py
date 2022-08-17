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
          az {consts.EXTENSION_NAME} create --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --name myextension \
--extension-type microsoft.openservicemesh --scope cluster --release-train stable
"""

helps[f'{consts.EXTENSION_NAME} list'] = f"""
    type: command
    short-summary: List Kubernetes Extensions.
    examples:
      - name: List all Kubernetes Extensions on a cluster
        text: |-
          az {consts.EXTENSION_NAME} list --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters
"""

helps[f'{consts.EXTENSION_NAME} delete'] = f"""
    type: command
    short-summary: Delete a Kubernetes Extension.
    examples:
      - name: Delete an existing Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} delete --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --name myextension
"""

helps[f'{consts.EXTENSION_NAME} show'] = f"""
    type: command
    short-summary: Show a Kubernetes Extension.
    examples:
      - name: Show details of a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} show --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --name myextension
"""

helps[f'{consts.EXTENSION_NAME} update'] = f"""
    type: command
    short-summary: Update mutable properties of a Kubernetes Extension.
    long-summary: For update to ConfigSettings and ConfigProtectedSettings, please \
refer to documentation of the cluster extension service to check update to these \
properties is supported before updating these properties.
    examples:
      - name: Update a Kubernetes Extension
        text: |-
          az {consts.EXTENSION_NAME} update --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters \
--name myextension --auto-upgrade true/false --version extension-version \
--release-train stable --configuration-settings settings-key=settings-value \
--configuration-protected-settings protected-settings-key=protected-value \
--configuration-settings-file=config-settings-file \
--configuration-protected-settings-file=protected-settings-file
"""

helps[f'{consts.EXTENSION_NAME} extension-types'] = """
    type: group
    short-summary: Commands to discover Kubernetes Extension Types.
"""

helps[f'{consts.EXTENSION_NAME} extension-types list'] = f"""
    type: command
    short-summary: List Kubernetes Extension Types.
    examples:
      - name: List Kubernetes Extension Types
        text: |-
          az {consts.EXTENSION_NAME} extension-types list --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters
"""

helps[f'{consts.EXTENSION_NAME} extension-types list-by-location'] = f"""
    type: command
    short-summary: List available Kubernetes Extension Types in a specified region.
    examples:
      - name: List Kubernetes Extension Types by location
        text: |-
          az {consts.EXTENSION_NAME} extension-types list-by-location --location eastus2euap
"""

helps[f'{consts.EXTENSION_NAME} extension-types show'] = f"""
    type: command
    short-summary: Show properties for a Kubernetes Extension Type.
    examples:
      - name: Show Kubernetes Extension Type
        text: |-
          az {consts.EXTENSION_NAME} extension-types show --resource-group my-resource-group \
--cluster-name mycluster --cluster-type connectedClusters --extension-type cassandradatacenteroperator
"""

helps[f'{consts.EXTENSION_NAME} extension-types list-versions'] = f"""
    type: command
    short-summary: List available versions for a Kubernetes Extension Type.
    examples:
      - name: List versions for an Extension Type
        text: |-
          az {consts.EXTENSION_NAME} extension-types list-versions --location eastus2euap \
--extension-type cassandradatacenteroperator
"""
