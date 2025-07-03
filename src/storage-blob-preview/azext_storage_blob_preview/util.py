# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.profiles import ResourceType
from .profiles import CUSTOM_DATA_STORAGE_BLOB


def create_short_lived_blob_sas_v2(cmd, account_name, container, blob, account_key=None, user_delegation_key=None):
    from datetime import datetime, timedelta

    t_sas = cmd.get_models('_shared_access_signature#BlobSharedAccessSignature',
                           resource_type=CUSTOM_DATA_STORAGE_BLOB)

    t_blob_permissions = cmd.get_models('_models#BlobSasPermissions', resource_type=CUSTOM_DATA_STORAGE_BLOB)
    expiry = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    if account_key:
        sas = t_sas(account_name, account_key=account_key)
    elif user_delegation_key:
        sas = t_sas(account_name, user_delegation_key=user_delegation_key)
    else:
        raise ValueError("Either account key or user delegation key need to be provided.")
    return sas.generate_blob(container, blob, permission=t_blob_permissions(read=True), expiry=expiry, protocol='https')


def create_short_lived_file_sas_v2(cmd, account_name, account_key, share, directory_name, file_name):
    from datetime import datetime, timedelta

    t_sas = cmd.get_models('_shared_access_signature#FileSharedAccessSignature',
                           resource_type=ResourceType.DATA_STORAGE_FILESHARE)

    t_file_permissions = cmd.get_models('_models#FileSasPermissions', resource_type=ResourceType.DATA_STORAGE_FILESHARE)
    expiry = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    sas = t_sas(account_name, account_key)
    return sas.generate_file(share, directory_name=directory_name, file_name=file_name,
                             permission=t_file_permissions(read=True), expiry=expiry, protocol='https')


def guess_content_type(file_path, original, settings_class):
    if original.content_encoding or original.content_type:
        return original

    import mimetypes
    mimetypes.add_type('application/json', '.json')
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('application/wasm', '.wasm')

    content_type, _ = mimetypes.guess_type(file_path)
    return settings_class(
        content_type=content_type,
        content_encoding=original.content_encoding,
        content_disposition=original.content_disposition,
        content_language=original.content_language,
        content_md5=original.content_md5,
        cache_control=original.cache_control)


def get_storage_client(cli_ctx, service_type, namespace):
    from azure.cli.command_modules.storage._client_factory import get_storage_data_service_client

    az_config = cli_ctx.config

    name = getattr(namespace, 'account_name', az_config.get('storage', 'account', None))
    key = getattr(namespace, 'account_key', az_config.get('storage', 'key', None))
    connection_string = getattr(namespace, 'connection_string', az_config.get('storage', 'connection_string', None))
    sas_token = getattr(namespace, 'sas_token', az_config.get('storage', 'sas_token', None))

    return get_storage_data_service_client(cli_ctx, service_type, name, key, connection_string, sas_token)
