# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['attestation'] = """
    type: group
    short-summary: Commands to manage attestation.
"""

helps['attestation create'] = """
    type: command
    short-summary: Creates or updates the Attestation Provider.
    examples:
      - name: AttestationProviders_Create
        text: |-
               az attestation create --resource-group "MyResourceGroup" --name "MyAttestationProvider"
"""

helps['attestation update'] = """
    type: command
    short-summary: Creates or updates the Attestation Provider.
"""

helps['attestation delete'] = """
    type: command
    short-summary: Delete Attestation Service.
    examples:
      - name: AttestationProviders_Delete
        text: |-
               az attestation delete --resource-group "MyResourceGroup" --name "MyAttestationProvider"
"""

helps['attestation show'] = """
    type: command
    short-summary: Get the status of Attestation Provider.
    examples:
      - name: AttestationProviders_Get
        text: |-
               az attestation show --resource-group "MyResourceGroup" --name "MyAttestationProvider"
"""
