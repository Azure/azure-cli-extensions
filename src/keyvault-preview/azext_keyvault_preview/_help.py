# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import
# pylint: disable=line-too-long, too-many-lines

helps['keyvault update-hsm'] = """
type: command
short-summary: Update the properties of a HSM.
examples:
  - name: Update the properties of a HSM.
    text: |
        az keyvault update-hsm --enable-purge-protection true --hsm-name myhsm --resource-group myrg
  - name: Set multi regions for a HSM
    text: az keyvault update-hsm --secondary-locations westus eastus --hsm-name myhsm --resource-group myrg
"""