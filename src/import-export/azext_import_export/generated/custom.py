# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=too-many-lines


def import_export_job_list(cmd, client, resource_group_name=None):
    if resource_group_name is not None:
        return client.list_by_resource_group(resource_group_name=resource_group_name)
    return client.list_by_subscription()


def import_export_job_show(cmd, client, name, resource_group_name):
    return client.get(job_name=name, resource_group_name=resource_group_name)


def import_export_job_create(cmd, client, name, resource_group_name, client_tenant_id=None, location=None, tags=None,
                             storage_account=None, type=None, return_address=None, return_shipping=None,
                             shipping_information=None, delivery_package=None,
                             return_package=None, diagnostics_path=None, log_level=None, backup_drive_manifest=None,
                             state=None, cancel_requested=None, percent_complete=None, incomplete_blob_list_uri=None,
                             drive_list=None, export=None):
    # pylint: disable=redefined-builtin
    from msrestazure.tools import resource_id, is_valid_resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id
    storage_account_id = storage_account
    if not is_valid_resource_id(storage_account_id):
        storage_account_id = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx), resource_group=resource_group_name,
            namespace='Microsoft.Storage', type='storageAccounts', name=storage_account)

    return client.create(job_name=name, resource_group_name=resource_group_name, client_tenant_id=client_tenant_id,
                         location=location, tags=tags, storage_account_id=storage_account_id, job_type=type,
                         return_address=return_address, return_shipping=return_shipping,
                         shipping_information=shipping_information, delivery_package=delivery_package,
                         return_package=return_package, diagnostics_path=diagnostics_path, log_level=log_level,
                         backup_drive_manifest=backup_drive_manifest, state=state, cancel_requested=cancel_requested,
                         percent_complete=percent_complete, incomplete_blob_list_uri=incomplete_blob_list_uri,
                         drive_list=drive_list, export=export)


def import_export_job_update(cmd, client, name, resource_group_name, tags=None, cancel_requested=None, state=None,
                             return_address=None, return_shipping=None, delivery_package=None, log_level=None,
                             backup_drive_manifest=None, drive_list=None):
    return client.update(job_name=name, resource_group_name=resource_group_name, tags=tags,
                         cancel_requested=cancel_requested, state=state, return_address=return_address,
                         return_shipping=return_shipping, delivery_package=delivery_package, log_level=log_level,
                         backup_drive_manifest=backup_drive_manifest, drive_list=drive_list)


def import_export_job_delete(cmd, client, name, resource_group_name):
    return client.delete(job_name=name, resource_group_name=resource_group_name)


def import_export_bit_locker_key_list(cmd, client, job_name, resource_group_name):
    return client.list(job_name=job_name, resource_group_name=resource_group_name)


def import_export_location_list(cmd, client):
    return client.list()


def import_export_location_show(cmd, client, location):
    return client.get(location_name=location)
