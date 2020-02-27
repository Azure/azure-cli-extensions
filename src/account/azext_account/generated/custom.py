# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def account_subscription_create_csp_subscription(cmd, client,
                                                 billing_account_name,
                                                 customer_name,
                                                 display_name,
                                                 sku_id,
                                                 reseller_id=None,
                                                 service_provider_id=None):
    body = {}
    body['display_name'] = display_name  # string
    body['sku_id'] = sku_id  # string
    body['reseller_id'] = reseller_id  # string
    body['service_provider_id'] = service_provider_id  # string
    return client.create_csp_subscription(billing_account_name=billing_account_name, customer_name=customer_name, body=body)


def account_subscription_create_subscription(cmd, client,
                                             billing_account_name,
                                             billing_profile_name,
                                             invoice_section_name,
                                             body):
    return client.create_subscription(billing_account_name=billing_account_name, billing_profile_name=billing_profile_name, invoice_section_name=invoice_section_name, body=body)


def account_subscription_rename(cmd, client,
                                subscription_name=None):
    return client.rename(subscription_name=subscription_name)


def account_subscription_create_subscription_in_enrollment_account(cmd, client,
                                                                   enrollment_account_name,
                                                                   body):
    return client.create_subscription_in_enrollment_account(enrollment_account_name=enrollment_account_name, body=body)


def account_subscription_cancel(cmd, client):
    return client.cancel()


def account_subscription_enable(cmd, client):
    return client.enable()


def account_subscription_operation_show(cmd, client,
                                        operation_id):
    return client.get(operation_id=operation_id)


def account_operations_list(cmd, client):
    return client.list()
