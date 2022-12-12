# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
# pylint: disable=line-too-long, too-many-lines

helps['keyvault region'] = """
type: group
short-summary: Manage MHSM multi-regions.
"""

helps['keyvault region list'] = """
type: command
short-summary: Get regions information associated with the managed HSM Pool.
"""

helps['keyvault region add'] = """
type: command
short-summary: Add regions for the managed HSM Pool.
examples:
  - name: Add regions for the managed HSM.
    text: |
        az keyvault region add --region-name westus2 --hsm-name myhsm --resource-group myrg
"""

helps['keyvault region remove'] = """
type: command
short-summary: Remove regions for the managed HSM Pool.
examples:
  - name: Remove regions for the managed HSM.
    text: |
        az keyvault region remove --region-name westus2 --hsm-name myhsm --resource-group myrg
"""

helps['keyvault region wait'] = """
type: command
short-summary: Place the CLI in a waiting state until a condition of the HSM is met.
examples:
  - name: Pause CLI until the regions are updated.
    text: |
        az keyvault region wait --hsm-name myhsm --updated
"""
