# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument

from azure.cli.core.util import sdk_no_wait


def account_subscription_rename(cmd, client, subscription_id,
                                subscription_name=None):
    body = {'subscriptionName': subscription_name}
    return client.rename(subscription_id=subscription_id, body=body)


def account_alias_create(client,
                         alias_name,
                         workload=None,
                         billing_scope=None,
                         display_name=None,
                         subscription_id=None,
                         reseller_id=None,
                         no_wait=False):
    body = {
        'properties': {
            'display_name': display_name,
            'workload': workload,
            'billing_scope': billing_scope,
            'subscription_id': subscription_id,
            'reseller_id': reseller_id
        }
    }
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       alias_name=alias_name,
                       body=body)


def account_subscription_list_location(client,
                                       subscription_id):
    return client.list_locations(subscription_id=subscription_id)
