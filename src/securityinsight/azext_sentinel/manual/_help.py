# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=too-many-lines

from knack.help_files import helps

helps['sentinel'] = """
    type: group
    short-summary: Manage Security Insight
"""

helps['sentinel data-connector create'] = """
    type: command
    short-summary: "Create the data connector."
    parameters:
      - name: --aad-data-connector
        short-summary: "Represents AAD (Azure Active Directory) data connector."
        long-summary: |
            Usage: --aad-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --aatp-data-connector
        short-summary: "Represents Microsoft Defender for Identity data connector."
        long-summary: |
            Usage: --aatp-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --asc-data-connector
        short-summary: "Represents Microsoft Defender for Cloud data connector."
        long-summary: |
            Usage: --asc-data-connector subscription-id=XX state=XX kind=XX etag=XX

            subscription-id: The subscription id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --aws-cloud-trail-data-connector
        short-summary: "Represents Amazon Web Services CloudTrail data connector."
        long-summary: |
            Usage: --aws-cloud-trail-data-connector aws-role-arn=XX state=XX kind=XX etag=XX

            aws-role-arn: The Aws Role Arn (with CloudTrailReadOnly policy) that is used to access the Aws account.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --mcas-data-connector
        short-summary: "Represents Microsoft Defender for Cloud Apps data connector."
        long-summary: |
            Usage: --mcas-data-connector tenant-id=XX state-data-types-alerts-state=XX state-data-types-discovery-logs-\
state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state-data-types-alerts-state: Describe whether this data type connection is enabled or not.
            state-data-types-discovery-logs-state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --mdatp-data-connector
        short-summary: "Represents Microsoft Defender for Endpoint data connector."
        long-summary: |
            Usage: --mdatp-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --office-data-connector
        short-summary: "Represents office data connector."
        long-summary: |
            Usage: --office-data-connector tenant-id=XX state-data-types-share-point-state=XX \
state-data-types-exchange-state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state-data-types-share-point-state: Describe whether this data type connection is enabled or not.
            state-data-types-exchange-state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --ti-data-connector
        short-summary: "Represents threat intelligence data connector."
        long-summary: |
            Usage: --ti-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
    examples:
      - name: Creates or updates an Office365 data connector.
        text: |-
               az sentinel data-connector create --office-data-connector etag="{etag}" \
               tenant-id="{tenant-id}" --data-connector-id "{id}" --resource-group "myRg" --workspace-name "myWorkspace"
"""

helps['sentinel data-connector update'] = """
    type: command
    short-summary: "Update the data connector."
    parameters:
      - name: --aad-data-connector
        short-summary: "Represents AAD (Azure Active Directory) data connector."
        long-summary: |
            Usage: --aad-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --aatp-data-connector
        short-summary: "Represents Microsoft Defender for Identity data connector."
        long-summary: |
            Usage: --aatp-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --asc-data-connector
        short-summary: "Represents Microsoft Defender for Cloud data connector."
        long-summary: |
            Usage: --asc-data-connector subscription-id=XX state=XX kind=XX etag=XX

            subscription-id: The subscription id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --aws-cloud-trail-data-connector
        short-summary: "Represents Amazon Web Services CloudTrail data connector."
        long-summary: |
            Usage: --aws-cloud-trail-data-connector aws-role-arn=XX state=XX kind=XX etag=XX

            aws-role-arn: The Aws Role Arn (with CloudTrailReadOnly policy) that is used to access the Aws account.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --mcas-data-connector
        short-summary: "Represents Microsoft Defender for Cloud Apps data connector."
        long-summary: |
            Usage: --mcas-data-connector tenant-id=XX state-data-types-alerts-state=XX state-data-types-discovery-logs-\
state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state-data-types-alerts-state: Describe whether this data type connection is enabled or not.
            state-data-types-discovery-logs-state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --mdatp-data-connector
        short-summary: "Represents Microsoft Defender for Endpoint data connector."
        long-summary: |
            Usage: --mdatp-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --office-data-connector
        short-summary: "Represents office data connector."
        long-summary: |
            Usage: --office-data-connector tenant-id=XX state-data-types-share-point-state=XX \
state-data-types-exchange-state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state-data-types-share-point-state: Describe whether this data type connection is enabled or not.
            state-data-types-exchange-state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
      - name: --ti-data-connector
        short-summary: "Represents threat intelligence data connector."
        long-summary: |
            Usage: --ti-data-connector tenant-id=XX state=XX kind=XX etag=XX

            tenant-id: The tenant id to connect to, and get the data from.
            state: Describe whether this data type connection is enabled or not.
            kind: Required. The data connector kind
            etag: Etag of the azure resource
"""
