# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client, prepare_client_kwargs_track2
from azure.cli.core.profiles import ResourceType, get_sdk
from .profiles import CUSTOM_DATA_STORAGE_BLOB

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


def get_account_url(cli_ctx, account_name, service):
    from knack.util import CLIError
    if account_name is None:
        raise CLIError("Please provide storage account name or connection string.")
    storage_endpoint = cli_ctx.cloud.suffixes.storage_endpoint
    return "https://{}.{}.{}".format(account_name, service, storage_endpoint)


def get_credential(kwargs):
    account_key = kwargs.pop('account_key', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    credential = account_key or sas_token or token_credential
    return credential


def _config_location_mode(kwargs, client_kwargs):
    location_mode = kwargs.pop('location_mode', None)
    if location_mode:
        client_kwargs['_location_mode'] = location_mode
    return client_kwargs


def cf_blob_service(cli_ctx, kwargs):
    client_kwargs = prepare_client_kwargs_track2(cli_ctx)
    client_kwargs = _config_location_mode(kwargs, client_kwargs)
    t_blob_service = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_BLOB,
                             '_blob_service_client#BlobServiceClient')
    connection_string = kwargs.pop('connection_string', None)
    account_name = kwargs.pop('account_name', None)
    account_url = kwargs.pop('account_url', None)
    account_key = kwargs.pop('account_key', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    if connection_string:
        try:
            return t_blob_service.from_connection_string(conn_str=connection_string, **client_kwargs)
        except ValueError as err:
            from azure.cli.core.azclierror import InvalidArgumentValueError
            raise InvalidArgumentValueError('Invalid connection string: {}, err detail: {}'
                                            .format(connection_string, str(err)),
                                            recommendation='Try `az storage account show-connection-string` '
                                                           'to get a valid connection string')
    if not account_url:
        account_url = get_account_url(cli_ctx, account_name=account_name, service='blob')
    credential = account_key or sas_token or token_credential

    return t_blob_service(account_url=account_url, credential=credential, **client_kwargs)


def cf_blob_client(cli_ctx, kwargs):
    if kwargs.get('blob_url'):
        t_blob_client = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_BLOB, '_blob_client#BlobClient')
        credential = get_credential(kwargs)
        # del unused kwargs
        kwargs.pop('connection_string')
        kwargs.pop('account_name')
        kwargs.pop('account_url')
        kwargs.pop('container_name')
        kwargs.pop('blob_name')
        return t_blob_client.from_blob_url(blob_url=kwargs.pop('blob_url'),
                                           credential=credential,
                                           snapshot=kwargs.pop('snapshot', None))
    kwargs.pop('blob_url')
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
    account_url = kwargs.pop('account_url', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    if connection_string:
        return t_adls_service.from_connection_string(connection_string=connection_string)

    if not account_url:
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
