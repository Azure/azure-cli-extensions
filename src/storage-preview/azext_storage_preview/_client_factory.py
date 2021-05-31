# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client, _get_add_headers_callback
from azure.cli.core.profiles import get_sdk
from knack.util import CLIError
from knack.log import get_logger


from .profiles import CUSTOM_DATA_STORAGE, CUSTOM_MGMT_PREVIEW_STORAGE, CUSTOM_DATA_STORAGE_FILESHARE, \
    CUSTOM_DATA_STORAGE_FILEDATALAKE

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


logger = get_logger(__name__)


# edited from azure.cli.core.commands.client_factory
def get_data_service_client(cli_ctx, service_type, account_name, account_key, connection_string=None,
                            sas_token=None, socket_timeout=None, token_credential=None, endpoint_suffix=None):
    logger.debug('Getting data service client service_type=%s', service_type.__name__)
    try:
        client_kwargs = {'account_name': account_name,
                         'account_key': account_key,
                         'connection_string': connection_string,
                         'sas_token': sas_token}
        if socket_timeout:
            client_kwargs['socket_timeout'] = socket_timeout
        if token_credential:
            client_kwargs['token_credential'] = token_credential
        if endpoint_suffix:
            client_kwargs['endpoint_suffix'] = endpoint_suffix
        client = service_type(**client_kwargs)
    except ValueError as exc:
        _ERROR_STORAGE_MISSING_INFO = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE,
                                              'common._error#_ERROR_STORAGE_MISSING_INFO')
        if _ERROR_STORAGE_MISSING_INFO in str(exc):
            raise ValueError(exc)
        raise CLIError('Unable to obtain data client. Check your connection parameters.')
    # TODO: enable Fiddler
    client.request_callback = _get_add_headers_callback(cli_ctx)
    return client


def get_storage_data_service_client(cli_ctx, service, name=None, key=None, connection_string=None, sas_token=None,
                                    socket_timeout=None, token_credential=None):
    return get_data_service_client(cli_ctx, service, name, key, connection_string, sas_token,
                                   socket_timeout=socket_timeout,
                                   token_credential=token_credential,
                                   endpoint_suffix=cli_ctx.cloud.suffixes.storage_endpoint)


def generic_data_service_factory(cli_ctx, service, name=None, key=None, connection_string=None, sas_token=None,
                                 socket_timeout=None, token_credential=None):
    try:
        return get_storage_data_service_client(cli_ctx, service, name, key, connection_string, sas_token,
                                               socket_timeout, token_credential)
    except ValueError as val_exception:
        _ERROR_STORAGE_MISSING_INFO = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE,
                                              'common._error#_ERROR_STORAGE_MISSING_INFO')
        message = str(val_exception)
        if message == _ERROR_STORAGE_MISSING_INFO:
            message = MISSING_CREDENTIALS_ERROR_MESSAGE
        raise CLIError(message)


def storage_client_factory(cli_ctx, **_):
    return get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_PREVIEW_STORAGE)


def blob_data_service_factory(cli_ctx, kwargs):
    from .sdkutil import get_blob_service_by_type
    blob_type = kwargs.get('blob_type')
    blob_service = get_blob_service_by_type(cli_ctx, blob_type) or get_blob_service_by_type(cli_ctx, 'block')

    return generic_data_service_factory(cli_ctx, blob_service, kwargs.pop('account_name', None),
                                        kwargs.pop('account_key', None),
                                        connection_string=kwargs.pop('connection_string', None),
                                        sas_token=kwargs.pop('sas_token', None),
                                        socket_timeout=kwargs.pop('socket_timeout', None),
                                        token_credential=kwargs.pop('token_credential', None))


def adls_blob_data_service_factory(cli_ctx, kwargs):
    from .sdkutil import get_adls_blob_service_by_type
    blob_type = kwargs.get('blob_type')
    blob_service = get_adls_blob_service_by_type(cli_ctx, blob_type) or get_adls_blob_service_by_type(cli_ctx, 'block')

    return generic_data_service_factory(cli_ctx, blob_service, kwargs.pop('account_name', None),
                                        kwargs.pop('account_key', None),
                                        connection_string=kwargs.pop('connection_string', None),
                                        sas_token=kwargs.pop('sas_token', None),
                                        socket_timeout=kwargs.pop('socket_timeout', None),
                                        token_credential=kwargs.pop('token_credential', None))


def cloud_storage_account_service_factory(cli_ctx, kwargs):
    t_cloud_storage_account = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'common#CloudStorageAccount')
    account_name = kwargs.pop('account_name', None)
    account_key = kwargs.pop('account_key', None)
    sas_token = kwargs.pop('sas_token', None)
    kwargs.pop('connection_string', None)
    return t_cloud_storage_account(account_name, account_key, sas_token)


def cf_sa(cli_ctx, _):
    return storage_client_factory(cli_ctx).storage_accounts


def cf_sa_blob_inventory(cli_ctx, _):
    return storage_client_factory(cli_ctx).blob_inventory_policies


def cf_blob_container_mgmt(cli_ctx, _):
    return storage_client_factory(cli_ctx).blob_containers


def cf_blob_data_gen_update(cli_ctx, kwargs):
    return blob_data_service_factory(cli_ctx, kwargs.copy())


def cf_mgmt_file_services(cli_ctx, _):
    return storage_client_factory(cli_ctx).file_services


def get_account_url(cli_ctx, account_name, service):
    if account_name is None:
        raise CLIError("Please provide storage account name or connection string.")
    storage_endpoint = cli_ctx.cloud.suffixes.storage_endpoint
    return "https://{}.{}.{}".format(account_name, service, storage_endpoint)


def cf_share_service(cli_ctx, kwargs):
    t_share_service = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_FILESHARE, '_share_service_client#ShareServiceClient')
    connection_string = kwargs.pop('connection_string', None)
    account_key = kwargs.pop('account_key', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    account_name = kwargs.pop('account_name', None)
    if connection_string:
        return t_share_service.from_connection_string(conn_str=connection_string)

    account_url = get_account_url(cli_ctx, account_name=account_name, service='file')
    credential = account_key or sas_token or token_credential

    if account_url and credential:
        return t_share_service(account_url=account_url, credential=credential)
    return None


def cf_share_client(cli_ctx, kwargs):
    return cf_share_service(cli_ctx, kwargs).get_share_client(share=kwargs.pop('share_name'),
                                                              snapshot=kwargs.pop('snapshot', None))


def cf_share_directory_client(cli_ctx, kwargs):
    return cf_share_client(cli_ctx, kwargs).get_directory_client(directory_path=kwargs.pop('directory_path'))


def cf_share_file_client(cli_ctx, kwargs):
    return cf_share_client(cli_ctx, kwargs).get_file_client(file_path=kwargs.pop('file_path'))


def cf_adls_service(cli_ctx, kwargs):
    client_kwargs = {}
    t_adls_service = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE_FILEDATALAKE,
                             '_data_lake_service_client#DataLakeServiceClient')
    connection_string = kwargs.pop('connection_string', None)
    account_name = kwargs.pop('account_name', None)
    account_key = kwargs.pop('account_key', None)
    token_credential = kwargs.pop('token_credential', None)
    sas_token = kwargs.pop('sas_token', None)
    # Enable NetworkTraceLoggingPolicy which logs all headers (except Authorization) without being redacted
    client_kwargs['logging_enable'] = True
    if connection_string:
        return t_adls_service.from_connection_string(conn_str=connection_string, **client_kwargs)

    account_url = get_account_url(cli_ctx, account_name=account_name, service='dfs')
    credential = account_key or sas_token or token_credential

    if account_url and credential:
        return t_adls_service(account_url=account_url, credential=credential, **client_kwargs)
    return None


def cf_adls_file_system(cli_ctx, kwargs):
    return cf_adls_service(cli_ctx, kwargs).get_file_system_client(file_system=kwargs.pop('file_system_name'))
