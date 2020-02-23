# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=line-too-long
from knack.help_files import helps  # pylint: disable=unused-import


helps['account subscriptions'] = """
    type: group
    short-summary: account subscriptions
"""

helps['account subscriptions list'] = """
    type: command
    short-summary: Gets all subscriptions for a tenant.
"""

helps['account subscriptions show'] = """
    type: command
    short-summary: Gets details about a specified subscription.
"""

helps['account subscriptions rename'] = """
    type: command
    short-summary: The operation to rename a subscription
"""

helps['account subscriptions cancel'] = """
    type: command
    short-summary: The operation to cancel a subscription
"""

helps['account subscriptions enable'] = """
    type: command
    short-summary: The operation to enable a subscription
"""

helps['account subscription-operation'] = """
    type: group
    short-summary: account subscription-operation
"""

helps['account subscription-operation show'] = """
    type: command
    short-summary: Get the status of the pending Microsoft.Subscription API operations.
"""

helps['account subscription-factory'] = """
    type: group
    short-summary: account subscription-factory
"""

helps['account subscription-factory create-csp-subscription'] = """
    type: command
    short-summary: The operation to create a new CSP subscription.
"""

helps['account subscription-factory create-subscription-in-enrollment-account'] = """
    type: command
    short-summary: Creates an Azure subscription
"""

helps['account subscription-factory create-subscription'] = """
    type: command
    short-summary: The operation to create a new WebDirect or EA Azure subscription.
"""

helps['account subscription-operations'] = """
    type: group
    short-summary: account subscription-operations
"""

helps['account subscription-operations list'] = """
    type: command
    short-summary: Lists all of the available pending Microsoft.Subscription API operations.
"""

helps['account operations'] = """
    type: group
    short-summary: account operations
"""

helps['account operations list'] = """
    type: command
    short-summary: Lists all of the available Microsoft.Subscription API operations.
"""

helps['account tenants'] = """
    type: group
    short-summary: account tenants
"""

helps['account tenants list'] = """
    type: command
    short-summary: Gets the tenants for your account.
"""
