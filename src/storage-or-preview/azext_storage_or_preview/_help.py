# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['storage account or-policy'] = """
type: group
short-summary: Manage storage account Object Replication Policy.
"""

helps['storage account or-policy create'] = """
type: command
short-summary: Create Object Replication Service Policy for storage account.
examples:
  - name: Create Object Replication Service Policy for storage account.
    text: az storage account or-policy create -g ResourceGroupName -n storageAccountName -d destAccountName -s srcAccountName --destination-container dcont --source-container scont
  - name: Create Object Replication Service Policy trough json file for storage account.
    text: az storage account or-policy create -g ResourceGroupName -n storageAccountName --policy @policy.json
  - name: Create Object Replication Service Policy to source storage account through policy associated with destination storage account.
    text: az storage account or-policy show -g ResourceGroupName -n destAccountName --policy-id "3496e652-4cea-4581-b2f7-c86b3971ba92" | az storage account or-policy create -g ResourceGroupName -n srcAccountName -p "@-"
"""

helps['storage account or-policy list'] = """
type: command
short-summary: List Object Replication Service Policies associated with the specified storage account.
examples:
  - name: List Object Replication Service Policies associated with the specified storage account.
    text: az storage account or-policy list -g ResourceGroupName -n StorageAccountName
"""

helps['storage account or-policy delete'] = """
type: command
short-summary: Delete specified Object Replication Service Policy associated with the specified storage account.
examples:
  - name: Delete Object Replication Service Policy associated with the specified storage account.
    text: az storage account or-policy delete -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8"
"""

helps['storage account or-policy show'] = """
type: command
short-summary: Show the properties of specified Object Replication Service Policy for storage account.
examples:
  - name: Show the properties of specified Object Replication Service Policy for storage account.
    text: az storage account or-policy show -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8"
"""

helps['storage account or-policy update'] = """
type: command
short-summary: Update Object Replication Service Policy properties for storage account.
examples:
  - name: Update source storage account in Object Replication Service Policy.
    text: az storage account or-policy update -g ResourceGroupName -n StorageAccountName --source-account newSourceAccount --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8"
  - name: Update Object Replication Service Policy through json file.
    text: az storage account or-policy update -g ResourceGroupName -n StorageAccountName -p @policy.json
"""

helps['storage account or-policy rule'] = """
type: group
short-summary: Manage Object Replication Service Policy Rules.
"""

helps['storage account or-policy rule add'] = """
type: command
short-summary: Add rule to the specified Object Replication Service Policy.
examples:
  - name: Add rule to the specified Object Replication Service Policy.
    text: az storage account or-policy rule add -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8" -d destContainer -s srcContainer
"""

helps['storage account or-policy rule list'] = """
type: command
short-summary: List all the rules in the specified Object Replication Service Policy.
examples:
  - name: List all the rules in the specified Object Replication Service Policy.
    text: az storage account or-policy rule list -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8"
"""

helps['storage account or-policy rule remove'] = """
type: command
short-summary: Remove the specified rule from the specified Object Replication Service Policy.
examples:
  - name: Remove the specified rule from the specified Object Replication Service Policy.
    text: az storage account or-policy rule remove -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8" --rule-id "78746d86-d3b7-4397-a99c-0837e6741332"
"""

helps['storage account or-policy rule show'] = """
type: command
short-summary: Show the properties of specified rule in Object Replication Service Policy.
examples:
  - name: Show the properties of specified rule in Object Replication Service Policy.
    text: az storage account or-policy rule show -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8" --rule-id "78746d86-d3b7-4397-a99c-0837e6741332"
"""

helps['storage account or-policy rule update'] = """
type: command
short-summary: Update rule properties to Object Replication Service Policy.
examples:
  - name: Update rule properties to Object Replication Service Policy.
    text: az storage account or-policy rule update -g ResourceGroupName -n StorageAccountName --policy-id "04344ea7-aa3c-4846-bfb9-e908e32d3bf8" --rule-id "78746d86-d3b7-4397-a99c-0837e6741332" --prefix-match blobA blobB
"""
