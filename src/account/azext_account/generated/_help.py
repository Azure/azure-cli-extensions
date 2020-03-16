# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['account subscription'] = """
    type: group
    short-summary: account subscription
"""

helps['account subscription create-subscription'] = """
    type: command
    short-summary: The operation to create a new WebDirect or EA Azure subscription.
    examples:
      - name: createSubscription
        text: |-
               az account subscription create-subscription --billing-account-name \\
               "0aa27f2b-ec7f-5a65-71f6-a5ff0897bd55:ae0dae1e-de9a-41f6-8257-76b055d98372_2019-05-31" \\
               --billing-profile-name "27VR-HDWX-BG7-TGB" --cost-center "135366376" --display-name \\
               "Contoso MCA subscription" --sku-id "0001" --invoice-section-name "JGF7-NSBG-PJA-TGB"
"""

helps['account subscription create-subscription-in-enrollment-account'] = """
    type: command
    short-summary: Creates an Azure subscription
    examples:
      - name: createSubscription
        text: |-
               az account subscription create-subscription-in-enrollment-account --display-name \\
               "Test Ea Azure Sub" --offer-type "MS-AZR-0017P" --enrollment-account-name \\
               "73f8ab6e-cfa0-42be-b886-be6e77c2980c"
"""

helps['account subscription create-csp-subscription'] = """
    type: command
    short-summary: The operation to create a new CSP subscription.
    examples:
      - name: createSubscription
        text: |-
               az account subscription create-csp-subscription --billing-account-name \\
               "2bc54a6f-8d8a-5be1-5bff-bb4f285f512b:11a72812-d9a4-446e-9a1e-70c8bcadf5c0_2019-05-31" \\
               --display-name "Contoso MCA subscription" --sku-id "0001" --customer-name \\
               "e33ba30d-3718-4b15-bfaa-5627a57cda6f"
"""

helps['account subscription rename'] = """
    type: command
    short-summary: The operation to rename a subscription
    examples:
      - name: renameSubscription
        text: |-
               az account subscription rename --subscription-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
"""

helps['account subscription cancel'] = """
    type: command
    short-summary: The operation to cancel a subscription
    examples:
      - name: cancelSubscription
        text: |-
               az account subscription cancel --subscription-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
"""

helps['account subscription enable'] = """
    type: command
    short-summary: The operation to enable a subscription
    examples:
      - name: enableSubscription
        text: |-
               az account subscription enable --subscription-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
"""

helps['account subscription-operation'] = """
    type: group
    short-summary: account subscription-operation
"""

helps['account subscription-operation show'] = """
    type: command
    short-summary: Get the status of the pending Microsoft.Subscription API operations.
    examples:
      - name: getPendingSubscriptionOperations
        text: |-
               az account subscription-operation show --operation-id \\
               "e4b8d068-f574-462a-a76f-6fa0afc613c9"
"""

helps['account operation'] = """
    type: group
    short-summary: account operation
"""

helps['account operation list'] = """
    type: command
    short-summary: Lists all of the available Microsoft.Subscription API operations.
    examples:
      - name: getOperations
        text: |-
               az account operation list
"""
