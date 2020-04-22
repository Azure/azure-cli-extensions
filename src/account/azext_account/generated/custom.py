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


def account_subscription_create_subscription(cmd, client,
                                             billing_account_name,
                                             billing_profile_name,
                                             invoice_section_name,
                                             display_name,
                                             sku_id,
                                             cost_center=None,
                                             owner=None,
                                             management_group_id=None,
                                             no_wait=False):

    body = {}
    body['display_name'] = display_name
    body['sku_id'] = sku_id
    body['cost_center'] = cost_center
    body['owner'] = {'object_id': owner}
    body['management_group_id'] = management_group_id
    return sdk_no_wait(no_wait, client.create_subscription, billing_account_name=billing_account_name, billing_profile_name=billing_profile_name, invoice_section_name=invoice_section_name, body=body)


def account_subscription_create_subscription_in_enrollment_account(cmd, client,
                                                                   enrollment_account_name,
                                                                   display_name=None,
                                                                   management_group_id=None,
                                                                   owners=None,
                                                                   offer_type=None,
                                                                   no_wait=False):
    if owners is not None:
        owners = [{'object_id': x} for x in owners]

    body = {}
    body['display_name'] = display_name
    body['management_group_id'] = management_group_id
    body['owners'] = owners
    body['offer_type'] = offer_type
    return sdk_no_wait(no_wait, client.create_subscription_in_enrollment_account, enrollment_account_name=enrollment_account_name, body=body)


def account_subscription_create_csp_subscription(cmd, client,
                                                 billing_account_name,
                                                 customer_name,
                                                 display_name,
                                                 sku_id,
                                                 reseller_id=None,
                                                 no_wait=False):
    body = {}
    body['display_name'] = display_name
    body['sku_id'] = sku_id
    body['reseller_id'] = reseller_id
    return sdk_no_wait(no_wait, client.create_csp_subscription, billing_account_name=billing_account_name, customer_name=customer_name, body=body)


def account_subscription_rename(cmd, client, subscription_id,
                                subscription_name=None):
    return client.rename(subscription_id=subscription_id, subscription_name=subscription_name)


def account_subscription_cancel(cmd, client, subscription_id):
    return client.cancel(subscription_id=subscription_id)


def account_subscription_enable(cmd, client, subscription_id):
    return client.enable(subscription_id=subscription_id)
