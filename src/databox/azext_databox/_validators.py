# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import resource_id


def validate_create_input_parameters(cmd, namespace):
    _parse_storage_account_details(cmd, namespace)
    _parse_managed_disk_details(cmd, namespace)
    _validate_expected_data_size_for_databoxdisk(namespace)
    _validate_destination_account_details(namespace)


def _parse_storage_account_details(cmd, namespace):
    """Parse storage account details for destination."""
    from msrestazure.tools import is_valid_resource_id

    if not namespace.destination_account_details:
        namespace.destination_account_details = []

    if namespace.storage_accounts:
        for storage_account in namespace.storage_accounts:
            if storage_account and not is_valid_resource_id(storage_account):
                storage_account = resource_id(
                    subscription=get_subscription_id(cmd.cli_ctx),
                    resource_group=namespace.resource_group_name,
                    namespace='Microsoft.Storage',
                    type='storageAccounts',
                    name=storage_account
                )

            if storage_account:
                storage_account_details = {'storage_account_id': storage_account,
                                           'data_destination_type': 'StorageAccount'}
                namespace.destination_account_details.append(storage_account_details)

    del namespace.storage_accounts


def _parse_managed_disk_details(cmd, namespace):
    """Parse managed disk details for destination."""
    from msrestazure.tools import is_valid_resource_id

    if not namespace.destination_account_details:
        namespace.destination_account_details = []

    subscription = get_subscription_id(cmd.cli_ctx)
    if namespace.staging_storage_account and not is_valid_resource_id(namespace.staging_storage_account):
        namespace.staging_storage_account = resource_id(
            subscription=subscription,
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Storage',
            type='storageAccounts',
            name=namespace.staging_storage_account
        )

    if namespace.resource_group_for_managed_disk and not is_valid_resource_id(
            namespace.resource_group_for_managed_disk):
        namespace.resource_group_for_managed_disk = '/subscriptions/' + subscription + '/resourceGroups/' + namespace.resource_group_for_managed_disk

    if namespace.staging_storage_account and namespace.resource_group_for_managed_disk:
        managed_disk_details = {'staging_storage_account_id': namespace.staging_storage_account,
                                'resource_group_id': namespace.resource_group_for_managed_disk,
                                'data_destination_type': 'ManagedDisk'}
        namespace.destination_account_details.append(managed_disk_details)

    del namespace.staging_storage_account
    del namespace.resource_group_for_managed_disk


def _validate_expected_data_size_for_databoxdisk(namespace):
    if namespace.sku == 'DataBoxDisk' and not namespace.expected_data_size:
        raise ValueError(
            "You must provide '--expected-data-size' when the 'sku' is 'DataBoxDisk'.")


def _validate_destination_account_details(namespace):
    if not namespace.destination_account_details:
        raise ValueError(
            "You must provide at least one '--storage-account' or the combination of '--staging-storage-account' and "
            "'--resource-group-for-managed-disk'")
