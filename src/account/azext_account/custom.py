# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-statements
# pylint: disable=too-many-lines
# pylint: disable=too-many-locals
# pylint: disable=unused-argument


def cancel_account_subscription(cmd, client):
    return client.cancel()


def rename_account_subscription(cmd, client,
                                subscription_name=None):
    return client.rename(subscription_name=subscription_name)


def enable_account_subscription(cmd, client):
    return client.enable()


def list_locations_account_subscription(cmd, client):
    return client.list_locations()


def get_account_subscription(cmd, client):
    return client.get()


def list_account_subscription(cmd, client):
    return client.list()


def get_account_subscription_operation(cmd, client,
                                       operation_id):
    return client.get(operation_id=operation_id)


def create_subscription_account_subscription_factory(cmd, client,
                                                     billing_account_name,
                                                     billing_profile_name,
                                                     invoice_section_name,
                                                     billing_profile_id,
                                                     sku_id,
                                                     display_name=None,
                                                     cost_center=None,
                                                     owner=None,
                                                     management_group_id=None,
                                                     additional_parameters=None,
                                                     reseller_id=None,
                                                     service_provider_id=None,
                                                     owners=None,
                                                     offer_type=None):
    return client.create_subscription(billing_account_name=billing_account_name, billing_profile_name=billing_profile_name, invoice_section_name=invoice_section_name, display_name=display_name, billing_profile_id=billing_profile_id, sku_id=sku_id, cost_center=cost_center, owner=owner, management_group_id=management_group_id, additional_parameters=additional_parameters, reseller_id=reseller_id, service_provider_id=service_provider_id, owners=owners, offer_type=offer_type)


def create_csp_subscription_account_subscription_factory(cmd, client,
                                                         billing_account_name,
                                                         customer_name,
                                                         billing_profile_id,
                                                         sku_id,
                                                         display_name=None,
                                                         cost_center=None,
                                                         owner=None,
                                                         management_group_id=None,
                                                         additional_parameters=None,
                                                         reseller_id=None,
                                                         service_provider_id=None,
                                                         owners=None,
                                                         offer_type=None):
    return client.create_csp_subscription(billing_account_name=billing_account_name, customer_name=customer_name, display_name=display_name, billing_profile_id=billing_profile_id, sku_id=sku_id, cost_center=cost_center, owner=owner, management_group_id=management_group_id, additional_parameters=additional_parameters, reseller_id=reseller_id, service_provider_id=service_provider_id, owners=owners, offer_type=offer_type)


def create_subscription_in_enrollment_account_account_subscription_factory(cmd, client,
                                                                           name,
                                                                           billing_profile_id,
                                                                           sku_id,
                                                                           display_name=None,
                                                                           cost_center=None,
                                                                           owner=None,
                                                                           management_group_id=None,
                                                                           additional_parameters=None,
                                                                           reseller_id=None,
                                                                           service_provider_id=None,
                                                                           owners=None,
                                                                           offer_type=None):
    return client.create_subscription_in_enrollment_account(enrollment_account_name=name, display_name=display_name, billing_profile_id=billing_profile_id, sku_id=sku_id, cost_center=cost_center, owner=owner, management_group_id=management_group_id, additional_parameters=additional_parameters, reseller_id=reseller_id, service_provider_id=service_provider_id, owners=owners, offer_type=offer_type)


def list_account_subscription_operation(cmd, client):
    return client.list()


def list_account_operation(cmd, client):
    return client.list()


def list_account_tenant(cmd, client):
    return client.list()
