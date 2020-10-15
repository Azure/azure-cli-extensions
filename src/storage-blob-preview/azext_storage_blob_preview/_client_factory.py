# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType, get_sdk
from .profiles import CUSTOM_DATA_STORAGE_BLOB, CUSTOM_MGMT_STORAGE

MISSING_CREDENTIALS_ERROR_MESSAGE = """
Missing credentials to access storage service. The following variations are accepted:
    (1) account name and key (--account-name and --account-key options or
        set AZURE_STORAGE_ACCOUNT and AZURE_STORAGE_KEY environment variables)
    (2) account name and SAS token (--sas-token option used with either the --account-name
        option or AZURE_STORAGE_ACCOUNT environment variable)
    (3) account name (--account-name option or AZURE_STORAGE_ACCOUNT environment variable;
        this will make calls to query for a storage account key using login credentials)
    (4) connection string (--connection-string option or
        set AZURE_STORAGE_CONNECTION_STRING environment variable); some shells will require
        quoting to preserve literal character interpretation.
"""


def storage_client_factory(cli_ctx, **_):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_STORAGE)


def cf_mgmt_blob_services(cli_ctx, _):
    return storage_client_factory(cli_ctx).blob_services


def cf_mgmt_policy(cli_ctx, _):
    return storage_client_factory(cli_ctx).management_policies


def cf_sa(cli_ctx, _):
    return storage_client_factory(cli_ctx).storage_accounts


def cf_mgmt_policy(cli_ctx, _):
    return storage_client_factory(cli_ctx).management_policies


def get_account_url(cli_ctx, account_name, service):
    from knack.util import CLIError
    if account_name is None:
        raise CLIError("Please provide storage account name or connection string.")
    storage_endpoint = cli_ctx.cloud.suffixes.storage_endpoint
    return "https://{}.{}.{}".format(account_name, service, storage_endpoint)


def cf_blob_service(cli_ctx, kwargs):
    from knack.util import CLIError
    client_args = {}
    t_blob_service = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_BLOB,
                             '_blob_service_client#BlobServiceClient')
    connection_string = kwargs.pop('connection_string', None)
    account_name = kwargs.pop('account_name', None)
    account_key = kwargs.pop('account_key', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    location_mode = kwargs.pop('location_mode', None)
    if location_mode:
        client_args['_location_mode'] = location_mode

    if connection_string:
        return t_blob_service.from_connection_string(conn_str=connection_string)

    account_url = get_account_url(cli_ctx, account_name=account_name, service='blob')
    credential = account_key or sas_token or token_credential

    if account_url and credential:
        return t_blob_service(account_url=account_url, credential=credential, **client_args)
    raise CLIError("Please provide valid connection string, or account name with account key, "
                   "sas token or login auth mode.")


def cf_blob_client(cli_ctx, kwargs):
    return cf_blob_service(cli_ctx, kwargs).get_blob_client(container=kwargs.pop('container_name'),
                                                            blob=kwargs.pop('blob_name'),
                                                            snapshot=kwargs.pop('snapshot', None))


def cf_blob_lease_client(cli_ctx, kwargs):
    t_lease_service = get_sdk(cli_ctx, ResourceType.DATA_STORAGE_BLOB, '_lease#BlobLeaseClient')
    blob_client = cf_blob_service(cli_ctx, kwargs).get_blob_client(container=kwargs.pop('container_name', None),
                                                                   blob=kwargs.pop('blob_name', None))
    return t_lease_service(client=blob_client, lease_id=kwargs.pop('lease_id', None))


def cf_container_client(cli_ctx, kwargs):
    return cf_blob_service(cli_ctx, kwargs).get_container_client(container=kwargs.pop('container_name', None))


def cf_blob_sas(cli_ctx, kwargs):
    t_blob_sas = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_BLOB, '_shared_access_signature#BlobSharedAccessSignature')

    if kwargs.pop('as_user', None):
        from .operations.blob import _get_datetime_from_string
        from datetime import datetime
        service_client = cf_blob_service(cli_ctx, kwargs)
        user_delegation_key = service_client.get_user_delegation_key(
            _get_datetime_from_string(kwargs['start']) if kwargs['start'] else datetime.utcnow(),
            _get_datetime_from_string(kwargs['expiry']))
        return t_blob_sas(account_name=kwargs.pop('account_name', None),
                          user_delegation_key=user_delegation_key)

    return t_blob_sas(account_name=kwargs.pop('account_name', None),
                      account_key=kwargs.pop('account_key', None))


def cf_adls_service(cli_ctx, kwargs):
    t_adls_service = get_sdk(cli_ctx, ResourceType.DATA_STORAGE_FILEDATALAKE,
                             '_data_lake_service_client#DataLakeServiceClient')
    connection_string = kwargs.pop('connection_string', None)
    account_key = kwargs.pop('account_key', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    if connection_string:
        return t_adls_service.from_connection_string(connection_string=connection_string)

    account_url = get_account_url(cli_ctx, account_name=kwargs.pop('account_name', None), service='dfs')
    credential = account_key or sas_token or token_credential

    if account_url and credential:
        return t_adls_service(account_url=account_url, credential=credential)
    return None


def cf_adls_file_system(cli_ctx, kwargs):
    return cf_adls_service(cli_ctx, kwargs).get_file_system_client(file_system=kwargs.pop('file_system_name'))


def cf_adls_directory(cli_ctx, kwargs):
    return cf_adls_file_system(cli_ctx, kwargs).get_directory_client(directory=kwargs.pop('directory_path'))


def cf_adls_file(cli_ctx, kwargs):
    return cf_adls_service(cli_ctx, kwargs).get_file_client(file_system=kwargs.pop('file_system_name', None),
                                                            file_path=kwargs.pop('path', None))
