# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def validate_destination_account_details(namespace):
    if namespace.storage_account_id:
        namespace.storage_account_details = {'storage_account_id': namespace.storage_account_id,
                                             'data_destination_type': 'StorageAccount'}
    del namespace.storage_account_id

    if namespace.staging_storage_account_id and namespace.resource_group_id:
        namespace.managed_disk_details = {'staging_storage_account_id': namespace.staging_storage_account_id,
                                          'resource_group_id': namespace.resource_group_id,
                                          'data_destination_type': 'ManagedDisk'}
    del namespace.staging_storage_account_id
    del namespace.resource_group_id

    if not namespace.storage_account_details and not namespace.managed_disk_details:
        raise ValueError(
            "You must provide '--storage-account-id' or the combination of '--staging-storage-account-id' and "
            "'--resource-group-id' or all the three parameters.")
