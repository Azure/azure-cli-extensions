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
    return client.rename(subscription_id=subscription_id, subscription_name=subscription_name)


def account_subscription_cancel(cmd, client, subscription_id):
    return client.cancel(subscription_id=subscription_id)


def account_subscription_enable(cmd, client, subscription_id):
    return client.enable(subscription_id=subscription_id)


def account_subscription_list(client):
    return client.list()


def account_subscription_show(client,
                              subscription_id):
    return client.get(subscription_id=subscription_id)


def account_subscription_list_location(client,
                                       subscription_id):
    return client.list_location(subscription_id=subscription_id)


def account_tenant_list(client):
    return client.list()


def account_alias_list(client):
    return client.list()


def account_alias_show(client,
                       alias_name):
    return client.get(alias_name=alias_name)


def account_alias_create(client,
                         alias_name,
                         workload=None,
                         billing_scope=None,
                         display_name=None,
                         subscription_id=None,
                         no_wait=False):
    properties = {
        'display_name': display_name,
        'workload': workload,
        'billing_scope': billing_scope,
        'subscription_id': subscription_id
    }
    return sdk_no_wait(no_wait,
                       client.begin_create,
                       alias_name=alias_name,
                       properties=properties)


def account_alias_delete(client,
                         alias_name):
    return client.delete(alias_name=alias_name)
