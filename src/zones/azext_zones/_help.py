# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['zones'] = """
    type: group
    short-summary: Commands to validate Availability Zone Configuration. Use one of the options below.
"""

helps['zones validate'] = """
    type: command
    short-summary: Validates zone redundancy status of all resources in the current subscription context for which you have read access.
    examples:
      - name: Validate zone redundancy status of all resources in the specified resource group
        text: |-
          az zones validate --resource-groups myProductionRG
      - name: Validate zone redundancy status of all resources in the specified resource group, but omit the dependent/child resources
        text: |-
          az zones validate --resource-groups myProductionRG --omit-dependent
      - name: Validate zone redundancy status of all resources that have ALL the specified tags
        text: |-
          az zones validate --tags env=prod,criticality=high
"""
