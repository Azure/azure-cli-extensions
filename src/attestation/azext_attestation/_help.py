# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['attestation operation'] = """
    type: group
    short-summary: Commands to manage attestation operation.
"""

helps['attestation operation list'] = """
    type: command
    short-summary: Lists all of the available Azure attestation operations.
    examples:
      - name: Operations_List
        text: |-
               az attestation operation list
"""

helps['attestation attestation-provider'] = """
    type: group
    short-summary: Commands to manage attestation attestation provider.
"""

helps['attestation attestation-provider create'] = """
    type: command
    short-summary: Creates or updates the Attestation Provider.
    examples:
      - name: AttestationProviders_Create
        text: |-
               az attestation attestation-provider create --resource-group "MyResourceGroup" --name \\
               "MyAttestationProvider"
"""

helps['attestation attestation-provider update'] = """
    type: command
    short-summary: Creates or updates the Attestation Provider.
"""

helps['attestation attestation-provider delete'] = """
    type: command
    short-summary: Delete Attestation Service.
    examples:
      - name: AttestationProviders_Delete
        text: |-
               az attestation attestation-provider delete --resource-group "MyResourceGroup" --name \\
               "MyAttestationProvider"
"""

helps['attestation attestation-provider show'] = """
    type: command
    short-summary: Get the status of Attestation Provider.
    examples:
      - name: AttestationProviders_Get
        text: |-
               az attestation attestation-provider show --resource-group "MyResourceGroup" --name \\
               "MyAttestationProvider"
"""

helps['attestation attestation-provider list'] = """
    type: command
    short-summary: Returns attestation providers list in a resource group.
    examples:
      - name: AttestationProviders_List
        text: |-
               az attestation attestation-provider list
      - name: AttestationProviders_ListByResourceGroup
        text: |-
               az attestation attestation-provider list --resource-group "testrg1"
"""
