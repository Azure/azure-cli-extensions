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
    short-summary: Commands to manage account subscription.
"""

helps['account subscription cancel'] = """
    type: command
    short-summary: The operation to cancel a subscription
    examples:
      - name: cancelSubscription
        text: |-
               az account subscription cancel
"""

helps['account subscription rename'] = """
    type: command
    short-summary: The operation to rename a subscription
    examples:
      - name: renameSubscription
        text: |-
               az account subscription rename
"""

helps['account subscription enable'] = """
    type: command
    short-summary: The operation to enable a subscription
    examples:
      - name: enableSubscription
        text: |-
               az account subscription enable
"""

helps['account subscription list-locations'] = """
    type: command
    short-summary: This operation provides all the locations that are available for resource providers; however, each resource provider may support a subset of this list.
"""

helps['account subscription get'] = """
    type: command
    short-summary: Gets details about a specified subscription.
"""

helps['account subscription list'] = """
    type: command
    short-summary: Gets all subscriptions for a tenant.
"""

helps['account subscription-operation'] = """
    type: group
    short-summary: Commands to manage account subscription operation.
"""

helps['account subscription-operation get'] = """
    type: command
    short-summary: Get the status of the pending Microsoft.Subscription API operations.
    examples:
      - name: getPendingSubscriptionOperations
        text: |-
               az account subscription-operation get --operation-id \\
               "e4b8d068-f574-462a-a76f-6fa0afc613c9"
"""

helps['account subscription-factory'] = """
    type: group
    short-summary: Commands to manage account subscription factory.
"""

helps['account subscription-factory create-subscription'] = """
    type: command
    short-summary: The operation to create a new WebDirect or EA Azure subscription.
    examples:
      - name: createSubscription
        text: |-
               az account subscription-factory create-subscription --billing-account-name \\
               "0aa27f2b-ec7f-5a65-71f6-a5ff0897bd55:ae0dae1e-de9a-41f6-8257-76b055d98372_2019-05-31" \\
               --billing-profile-name "27VR-HDWX-BG7-TGB" --invoice-section-name "JGF7-NSBG-PJA-TGB" \\
               --display-name "Contoso MCA subscription" --billing-profile-id "/providers/Microsoft.Billi
               ng/billingAccounts/0aa27f2b-ec7f-5a65-71f6-a5ff0897bd55:ae0dae1e-de9a-41f6-8257-76b055d983
               72_2019-05-31/billingProfiles/27VR-HDWX-BG7-TGB" --sku-id "0001" --cost-center \\
               "135366376"
"""

helps['account subscription-factory create-csp-subscription'] = """
    type: command
    short-summary: The operation to create a new CSP subscription.
    examples:
      - name: createSubscription
        text: |-
               az account subscription-factory create-csp-subscription --billing-account-name \\
               "2bc54a6f-8d8a-5be1-5bff-bb4f285f512b:11a72812-d9a4-446e-9a1e-70c8bcadf5c0_2019-05-31" \\
               --customer-name "e33ba30d-3718-4b15-bfaa-5627a57cda6f" --display-name \\
               "Contoso MCA subscription" --sku-id "0001"
"""

helps['account subscription-factory create-subscription-in-enrollment-account'] = """
    type: command
    short-summary: Creates an Azure subscription
    examples:
      - name: createSubscription
        text: |-
               az account subscription-factory create-subscription-in-enrollment-account \\
               --enrollment-account-name "73f8ab6e-cfa0-42be-b886-be6e77c2980c" --display-name \\
               "Test Ea Azure Sub" --offer-type "MS-AZR-0017P"
"""

helps['account subscription-operation'] = """
    type: group
    short-summary: Commands to manage account subscription operation.
"""

helps['account subscription-operation list'] = """
    type: command
    short-summary: Lists all of the available pending Microsoft.Subscription API operations.
    examples:
      - name: getPendingSubscriptionOperations
        text: |-
               az account subscription-operation list
"""

helps['account operation'] = """
    type: group
    short-summary: Commands to manage account operation.
"""

helps['account operation list'] = """
    type: command
    short-summary: Lists all of the available Microsoft.Subscription API operations.
    examples:
      - name: getOperations
        text: |-
               az account operation list
"""

helps['account tenant'] = """
    type: group
    short-summary: Commands to manage account tenant.
"""

helps['account tenant list'] = """
    type: command
    short-summary: Gets the tenants for your account.
"""
