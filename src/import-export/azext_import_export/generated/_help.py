# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['import-export'] = """
    type: group
    short-summary: Manage Import Export
"""

helps['import-export list'] = """
    type: command
    short-summary: Returns all active and completed jobs in a subscription.
    examples:
      - name: List jobs in a resource group
        text: |-
               az import-export list --resource-group "myResourceGroup"
      - name: List jobs in current subscription
        text: |-
               az import-export list
"""

helps['import-export show'] = """
    type: command
    short-summary: Gets information about an existing job.
    examples:
      - name: Get job
        text: |-
               az import-export show --resource-group "myResourceGroup" --name "myJob"
"""

helps['import-export create'] = """
    type: command
    short-summary: Creates a new job or updates an existing job in the specified subscription.
    examples:
      - name: Create an import job
        text: |-
               az import-export create --resource-group "myResourceGroup" --name "myJob"
               --location "West US" --backup-drive-manifest true --diagnostics-path "waimportexport"
               --drive-list bit-locker-key=238810-662376-448998-450120-652806-203390-606320-483076
               drive-header-hash= drive-id=9CA995BB manifest-file=\\\\DriveManifest.xml
               manifest-hash=109B21108597EF36D5785F08303F3638 --type "Import" --log-level "Verbose"
               --return-address city=Redmond country-or-region=USA email=Test@contoso.com phone=4250000000
               postal-code=98007 recipient-name=Tests state-or-province=wa street-address1=Street1
               street-address2=street2 --storage-account "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-\\
               xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.ClassicStorage/storageAccounts/test"
"""

helps['import-export update'] = """
    type: command
    short-summary: Updates specific properties of a job. You can call this operation to notify the Import/Export service that the hard drives comprising the import or export job have been shipped to the Microsoft data center. It can also be used to cancel an existing job.
    examples:
      - name: Update job
        text: |-
               az import-export update --resource-group "myResourceGroup" --name "myJob"
               --backup-drive-manifest true --log-level "Verbose" --state ""
"""

helps['import-export delete'] = """
    type: command
    short-summary: Deletes an existing job. Only jobs in the Creating or Completed states can be deleted.
    examples:
      - name: Delete job
        text: |-
               az import-export delete --resource-group "myResourceGroup" --name "myJob"
"""

helps['import-export bit-locker-key'] = """
    type: group
    short-summary: import-export bit-locker-key
"""

helps['import-export bit-locker-key list'] = """
    type: command
    short-summary: Returns the BitLocker Keys for all drives in the specified job.
    examples:
      - name: List BitLocker Keys for drives in a job
        text: |-
               az import-export bit-locker-key list --resource-group "myResourceGroup" --job-name "myJob"
"""

helps['import-export location'] = """
    type: group
    short-summary: import-export location
"""

helps['import-export location list'] = """
    type: command
    short-summary: Returns a list of locations to which you can ship the disks associated with an import or export job. A location is a Microsoft data center region.
    examples:
      - name: List locations to which you can ship the disks
        text: |-
               az import-export location list
"""

helps['import-export location show'] = """
    type: command
    short-summary: Returns the details about a location to which you can ship the disks associated with an import or export job. A location is an Azure region.
    examples:
      - name: Show details about a location
        text: |-
               az import-export location show --location "West US 2"
"""
