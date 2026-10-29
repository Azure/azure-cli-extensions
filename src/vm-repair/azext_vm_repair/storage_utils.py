# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.command_modules.storage._client_factory import cf_blob_service, cf_sa_for_keys


def get_unmanaged_blob_service_client(cmd, resource_group_name, account_name):
    storage_accounts = cf_sa_for_keys(cmd.cli_ctx, None)
    keys = storage_accounts.list_keys(resource_group_name, account_name, logging_enable=False)
    try:
        account_key = keys.keys_property[0].value
    except AttributeError:
        account_key = keys.key1

    account = storage_accounts.get_properties(resource_group_name, account_name)
    endpoints = getattr(account, 'primary_endpoints', None)
    blob_endpoint = getattr(endpoints, 'blob', None) if endpoints else None

    client_args = {
        'account_name': account_name,
        'account_key': account_key,
    }
    if blob_endpoint:
        client_args['account_url'] = blob_endpoint

    return cf_blob_service(cmd.cli_ctx, client_args)


def get_unmanaged_blob_client(blob_service_client, container, blob_name):
    return blob_service_client.get_blob_client(container=container, blob=blob_name)


def create_unmanaged_blob_snapshot(blob_client):
    result = blob_client.create_snapshot()
    return _get_value(result, 'snapshot')


def start_unmanaged_blob_copy(blob_client, source_uri):
    return blob_client.start_copy_from_url(source_uri)


def get_unmanaged_blob_copy_status(blob_client):
    properties = blob_client.get_blob_properties()
    copy_properties = _get_value(properties, 'copy')
    status = _get_value(copy_properties, 'status')
    return getattr(status, 'value', status)


def _get_value(obj, name):
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)
