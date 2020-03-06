# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['databox job'] = """
    type: group
    short-summary: Commands to manage databox job.
"""

helps['databox job create'] = """
    type: command
    short-summary: Create a new job with the specified parameters.
    examples:
      - name: Create a databox job to use both storage account and managed disk as data destination.
        text: |-
               az databox job create --resource-group "SdkRg4981" --name "SdkJob3971" --location \\
               "westus" --sku "DataBox" --contact-name "Public SDK Test" \\
               --phone "1234567890" --email-list "testing@microsoft.com" \\
               --street-address1 "16 TOWNSEND ST" --street-address2 "Unit 1" --city "San Francisco"  \\
               --state-or-province "CA" --country "US" --postal-code "94107" --company-name "Microsoft" \\
               --storage-account sa1 sa2 --staging-storage-account sa \\
               --resource-group-for-managed-disk /subscriptions/sub/resourceGroups/rg

      - name: Create a databoxdisk job to use storage account as data destination.
        text: |-
               az databox job create --resource-group "SdkRg4981" --name "SdkJob3971" --location \\
               "westus" --sku "DataBoxDisk" --expected-data-size 1 --contact-name "Public SDK Test" \\
               --phone "1234567890" --email-list "testing@microsoft.com" --street-address1 "16 TOWNSEND ST" \\
               --street-address2 "Unit 1" --city "San Francisco" --state-or-province "CA" --country "US" \\
               --postal-code "94107" --company-name "Microsoft" --storage-account sa1
"""

helps['databox job update'] = """
    type: command
    short-summary: Update an existing job with the specified parameters.
    examples:
      - name: Update the job "SdkJob3971" with the specified parameters.
        text: |-
               az databox job update --resource-group "SdkRg4981" --name "SdkJob3971" \\
               --contact-name "Update Job" --phone "1234567890" \\
               --email-list "testing@microsoft.com" \\
               --street-address1 "16 TOWNSEND ST" \\
               --city "San Francisco" --state-or-province "CA" \\
               --country "US" --postal-code "94107" \\
               --company-name "Microsoft" \\
"""

helps['databox job delete'] = """
    type: command
    short-summary: Delete a job.
    examples:
      - name: Delete the job "SdkJob3971" in resource group "SdkRg4981".
        text: |-
               az databox job delete --resource-group "SdkRg4981" --name "SdkJob3971"
"""

helps['databox job show'] = """
    type: command
    short-summary: Get information about the specified job.
    examples:
      - name: Get the information about the job "SdkJob3971".
        text: |-
               az databox job show --resource-group "SdkRg4981" --name "SdkJob3971"
"""

helps['databox job list'] = """
    type: command
    short-summary: List all the jobs available under the given resource group or the given subscription.
    examples:
      - name: List all the jobs available under the current subscription.
        text: |-
               az databox job list
      - name: List all the jobs available under the resource group "SdkRg4981".
        text: |-
               az databox job list --resource-group "SdkRg4981"
"""

helps['databox job cancel'] = """
    type: command
    short-summary: Cancel a job.
    examples:
      - name: Cancel the job "SdkJob3971" under resource group "SdkRg4981".
        text: |-
               az databox job cancel --resource-group "SdkRg4981" --name "SdkJob3971" --reason "CancelTest"
"""

helps['databox job list-credentials'] = """
    type: command
    short-summary: List the unencrypted secrets related to the job.
    examples:
      - name: List the unencrypted secrets related to the job "TJ-636646322037905056".
        text: |-
               az databox job list-credentials --resource-group "bvttoolrg6" --name "TJ-636646322037905056"
"""
