# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from knack.help_files import helps


helps['account subscription'] = """
    type: group
    short-summary: Manage subscriptions
"""

helps['account subscription rename'] = """
    type: command
    short-summary: Rename subscription
    examples:
      - name: Rename subscription
        text: |-
               az account subscription rename --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription cancel'] = """
    type: command
    short-summary: Cancel subscription
    examples:
      - name: Cancel subscription
        text: |-
               az account subscription cancel --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription enable'] = """
    type: command
    short-summary: Enable subscription
    examples:
      - name: Enable subscription
        text: |-
               az account subscription enable --subscription-id "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
"""

helps['account subscription list'] = """
    type: command
    short-summary: Gets all subscriptions for a tenant.
    examples:
      - name: listSubscriptions
        text: |-
               az account subscription list
"""

helps['account subscription show'] = """
    type: command
    short-summary: Gets details about a specified subscription.
    examples:
      - name: getSubscription
        text: |-
               az account subscription show --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
"""

helps['account subscription list-location'] = """
    type: command
    short-summary: This operation provides all the locations that are available for resource providers; however, each r\
esource provider may support a subset of this list.
    examples:
      - name: listLocations
        text: |-
               az account subscription list-location --subscription-id "83aa47df-e3e9-49ff-877b-94304bf3d3ad"
"""

helps['account tenant'] = """
    type: group
    short-summary: account tenant
"""

helps['account tenant list'] = """
    type: command
    short-summary: Gets the tenants for your account.
    examples:
      - name: listTenants
        text: |-
               az account tenant list
"""

helps['account alias'] = """
    type: group
    short-summary: account alias
"""

helps['account alias list'] = """
    type: command
    short-summary: List Alias Subscriptions.
    examples:
      - name: List Alias Subscriptions
        text: |-
               az account alias list
"""

helps['account alias show'] = """
    type: command
    short-summary: Get Alias Subscription.
    examples:
      - name: GetAlias
        text: |-
               az account alias show --name "aliasForNewSub"
"""

helps['account alias create'] = """
    type: command
    short-summary: "Create Alias Subscription."
    examples:
      - name: CreateAlias
        text: |-
               az account alias create --name "aliasForNewSub" --billing-scope "/providers/Microsoft.Billing/billingAcc\
ounts/e879cf0f-2b4d-5431-109a-f72fc9868693:024cabf4-7321-4cf9-be59-df0c77ca51de_2019-05-31/billingProfiles/PE2Q-NOIT-BG\
7-TGB/invoiceSections/MTT4-OBS7-PJA-TGB" --display-name "Contoso MCA subscription" --workload "Production"
"""

helps['account alias delete'] = """
    type: command
    short-summary: Delete Alias.
    examples:
      - name: DeleteAlias
        text: |-
               az account alias delete --name "aliasForNewSub"
"""

helps['account alias wait'] = """
    type: command
    short-summary: Place the CLI in a waiting state until a condition of the account alias is met.
    examples:
      - name: Pause executing next line of CLI script until the account alias is successfully created.
        text: |-
               az account alias wait --name "aliasForNewSub" --created
"""
