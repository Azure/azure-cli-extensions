# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def account_subscription_create_subscription(cmd, client,
                                             billing_account_name,
                                             billing_profile_name,
                                             invoice_section_name,
                                             body_display_name,
                                             body_sku_id,
                                             body_cost_center=None,
                                             body_owner=None,
                                             body_management_group_id=None):
    return client.create_subscription(billing_account_name=billing_account_name, billing_profile_name=billing_profile_name, invoice_section_name=invoice_section_name, display_name=body_display_name, sku_id=body_sku_id, cost_center=body_cost_center, owner=body_owner, management_group_id=body_management_group_id)


def account_subscription_create_subscription_in_enrollment_account(cmd, client,
                                                                   enrollment_account_name,
                                                                   body_display_name=None,
                                                                   body_management_group_id=None,
                                                                   body_owners=None,
                                                                   body_offer_type=None):
    return client.create_subscription_in_enrollment_account(enrollment_account_name=enrollment_account_name, display_name=body_display_name, management_group_id=body_management_group_id, owners=body_owners, offer_type=body_offer_type)


def account_subscription_create_csp_subscription(cmd, client,
                                                 billing_account_name,
                                                 customer_name,
                                                 body_display_name,
                                                 body_sku_id,
                                                 body_reseller_id=None):
    return client.create_csp_subscription(billing_account_name=billing_account_name, customer_name=customer_name, display_name=body_display_name, sku_id=body_sku_id, reseller_id=body_reseller_id)


def account_subscription_rename(cmd, client,subscription_id=subscription_id,
                                body_subscription_name=None):
    return client.rename(subscription_id=subscription_id,subscription_name=body_subscription_name)


def account_subscription_cancel(cmd, client,subscription_id):
    return client.cancel(subscription_id=subscription_id)


def account_subscription_enable(cmd, client,subscription_id):
    return client.enable(subscription_id=subscription_id)


def account_subscription_operation_show(cmd, client,
                                        operation_id):
    return client.get(operation_id=operation_id)


def account_operation_list(cmd, client):
    return client.list()
