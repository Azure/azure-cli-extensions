# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['storage account file-service-properties'] = """
type: group
short-summary: Manage the properties of file service in storage account.
"""

helps['storage account file-service-properties show'] = """
type: command
short-summary: Show the properties of file service in storage account.
long-summary: >
    Show the properties of file service in storage account.
examples:
  - name: Show the properties of file service in storage account.
    text: az storage account file-service-properties show -n mystorageaccount -g MyResourceGroup
"""

helps['storage account file-service-properties update'] = """
type: command
short-summary: Update the properties of file service in storage account.
long-summary: >
    Update the properties of file service in storage account.
examples:
  - name: Enable soft delete policy and set delete retention days to 100 for file service in storage account.
    text: az storage account file-service-properties update --enable-delete-retention true --delete-retention-days 100 -n mystorageaccount -g MyResourceGroup
  - name: Disable soft delete policy for file service.
    text: az storage account file-service-properties update --enable-delete-retention false -n mystorageaccount -g MyResourceGroup
"""
