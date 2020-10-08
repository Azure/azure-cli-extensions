# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access

import argparse

from azure.cli.core.commands.validators import validate_key_value_pairs
from azure.cli.core.profiles import ResourceType, get_sdk

from azure.cli.command_modules.storage._client_factory import storage_client_factory
from azure.cli.command_modules.storage.util import guess_content_type
from azure.cli.command_modules.storage.sdkutil import get_table_data_type
from azure.cli.command_modules.storage.url_quote_util import encode_for_url
from azure.cli.command_modules.storage.oauth_token_util import TokenUpdater

from knack.log import get_logger
from knack.util import CLIError
from .profiles import CUSTOM_DATA_STORAGE_BLOB
from ._client_factory import cf_blob_client

storage_account_key_options = {'primary': 'key1', 'secondary': 'key2'}
logger = get_logger(__name__)


# Utilities


# pylint: disable=inconsistent-return-statements,too-many-lines
def _query_account_key(cli_ctx, account_name):
    """Query the storage account key. This is used when the customer doesn't offer account key but name."""
    rg, scf = _query_account_rg(cli_ctx, account_name)
    t_storage_account_keys = get_sdk(
        cli_ctx, ResourceType.MGMT_STORAGE, 'models.storage_account_keys#StorageAccountKeys')

    scf.config.enable_http_logger = False
    logger.debug('Disable HTTP logging to avoid having storage keys in debug logs')
    if t_storage_account_keys:
        return scf.storage_accounts.list_keys(rg, account_name).key1
    # of type: models.storage_account_list_keys_result#StorageAccountListKeysResult
    return scf.storage_accounts.list_keys(rg, account_name).keys[0].value  # pylint: disable=no-member


def _query_account_rg(cli_ctx, account_name):
    """Query the storage account's resource group, which the mgmt sdk requires."""
    scf = storage_client_factory(cli_ctx)
    acc = next((x for x in scf.storage_accounts.list() if x.name == account_name), None)
    if acc:
        from msrestazure.tools import parse_resource_id
        return parse_resource_id(acc.id)['resource_group'], scf
    raise ValueError("Storage account '{}' not found.".format(account_name))


def _create_token_credential(cli_ctx):
    from knack.cli import EVENT_CLI_POST_EXECUTE

    TokenCredential = get_sdk(cli_ctx, ResourceType.DATA_STORAGE, 'common#TokenCredential')

    token_credential = TokenCredential()
    updater = TokenUpdater(token_credential, cli_ctx)

    def _cancel_timer_event_handler(_, **__):
        updater.cancel()
    cli_ctx.register_event(EVENT_CLI_POST_EXECUTE, _cancel_timer_event_handler)
    return token_credential


# region PARAMETER VALIDATORS
def parse_storage_account(cmd, namespace):
    """Parse storage account which can be either account name or account id"""
    from msrestazure.tools import parse_resource_id, is_valid_resource_id

    if namespace.account_name and is_valid_resource_id(namespace.account_name):
        namespace.resource_group_name = parse_resource_id(namespace.account_name)['resource_group']
        namespace.account_name = parse_resource_id(namespace.account_name)['name']
    elif namespace.account_name and not is_valid_resource_id(namespace.account_name) and \
            not namespace.resource_group_name:
        namespace.resource_group_name = _query_account_rg(cmd.cli_ctx, namespace.account_name)[0]


def process_resource_group(cmd, namespace):
    """Processes the resource group parameter from the account name"""
    if namespace.account_name and not namespace.resource_group_name:
        namespace.resource_group_name = _query_account_rg(cmd.cli_ctx, namespace.account_name)[0]


def validate_table_payload_format(cmd, namespace):
    t_table_payload = get_table_data_type(cmd.cli_ctx, 'table', 'TablePayloadFormat')
    if namespace.accept:
        formats = {
            'none': t_table_payload.JSON_NO_METADATA,
            'minimal': t_table_payload.JSON_MINIMAL_METADATA,
            'full': t_table_payload.JSON_FULL_METADATA
        }
        namespace.accept = formats[namespace.accept.lower()]


def validate_bypass(namespace):
    if namespace.bypass:
        namespace.bypass = ', '.join(namespace.bypass) if isinstance(namespace.bypass, list) else namespace.bypass


def get_config_value(cmd, section, key, default):
    return cmd.cli_ctx.config.get(section, key, default)


def is_storagev2(import_prefix):
    return import_prefix.startswith('azure.multiapi.storagev2.')


def validate_client_parameters(cmd, namespace):
    """ Retrieves storage connection parameters from environment variables and parses out connection string into
    account name and key """
    n = namespace

    if hasattr(n, 'auth_mode'):
        auth_mode = n.auth_mode or get_config_value(cmd, 'storage', 'auth_mode', None)
        del n.auth_mode
        if not n.account_name:
            n.account_name = get_config_value(cmd, 'storage', 'account', None)
        if auth_mode == 'login':
            from azure.cli.core._profile import Profile
            profile = Profile(cli_ctx=cmd.cli_ctx)
            n.token_credential, _, _ = profile.get_login_credentials(
                resource="https://storage.azure.com", subscription_id=n._subscription)

    if hasattr(n, 'token_credential') and n.token_credential:
        # give warning if there are account key args being ignored
        account_key_args = [n.account_key and "--account-key", n.sas_token and "--sas-token",
                            n.connection_string and "--connection-string"]
        account_key_args = [arg for arg in account_key_args if arg]

        if account_key_args:
            logger.warning('In "login" auth mode, the following arguments are ignored: %s',
                           ' ,'.join(account_key_args))
        return

    if not n.connection_string:
        n.connection_string = get_config_value(cmd, 'storage', 'connection_string', None)

    # if connection string supplied or in environment variables, extract account key and name
    if n.connection_string:
        conn_dict = validate_key_value_pairs(n.connection_string)
        n.account_name = conn_dict.get('AccountName')
        n.account_key = conn_dict.get('AccountKey')
        n.sas_token = conn_dict.get('SharedAccessSignature')

    # otherwise, simply try to retrieve the remaining variables from environment variables
    if not n.account_name:
        n.account_name = get_config_value(cmd, 'storage', 'account', None)
    if not n.account_key:
        n.account_key = get_config_value(cmd, 'storage', 'key', None)
    if not n.sas_token:
        n.sas_token = get_config_value(cmd, 'storage', 'sas_token', None)

    # strip the '?' from sas token. the portal and command line are returns sas token in different
    # forms
    if n.sas_token:
        n.sas_token = n.sas_token.lstrip('?')

    # account name with secondary
    if n.account_name and n.account_name.endswith('-secondary'):
        n.location_mode = 'secondary'
        n.account_name = n.account_name[:-10]

    # if account name is specified but no key, attempt to query
    if n.account_name and not n.account_key and not n.sas_token:
        logger.warning('There is no credential provided in your command and environment, we will query account key '
                       'for your storage account. \nPlease provide --connection-string, --account-key or --sas-token '
                       'as credential, or use `--auth-mode login` if you have required RBAC roles in your command. '
                       'For more information about RBAC roles in storage, you can see '
                       'https://docs.microsoft.com/en-us/azure/storage/common/storage-auth-aad-rbac-cli. \n'
                       'Setting corresponding environment variable can avoid inputting credential in your command. '
                       'Please use --help to get more information.')
        n.account_key = _query_account_key(cmd.cli_ctx, n.account_name)


def validate_encryption_key(cmd, namespace):
    encryption_key_source = cmd.get_models('EncryptionScopeSource', resource_type=ResourceType.MGMT_STORAGE)
    if namespace.key_source == encryption_key_source.microsoft_key_vault and \
            not namespace.key_uri:
        raise CLIError("usage error: Please specify --key-uri when using {} as key source."
                       .format(encryption_key_source.microsoft_key_vault))
    if namespace.key_source != encryption_key_source.microsoft_key_vault and namespace.key_uri:
        raise CLIError("usage error: Specify `--key-source={}` and --key-uri to configure key vault properties."
                       .format(encryption_key_source.microsoft_key_vault))


def process_blob_source_uri(cmd, namespace):
    """
    Validate the parameters referenced to a blob source and create the source URI from them.
    """
    from .util import create_short_lived_blob_sas
    usage_string = \
        'Invalid usage: {}. Supply only one of the following argument sets to specify source:' \
        '\n\t   --source-uri' \
        '\n\tOR --source-container --source-blob --source-snapshot [--source-account-name & sas] ' \
        '\n\tOR --source-container --source-blob --source-snapshot [--source-account-name & key] '

    ns = vars(namespace)

    # source as blob
    container = ns.pop('source_container', None)
    blob = ns.pop('source_blob', None)
    snapshot = ns.pop('source_snapshot', None)

    # source credential clues
    source_account_name = ns.pop('source_account_name', None)
    source_account_key = ns.pop('source_account_key', None)
    sas = ns.pop('source_sas', None)

    # source in the form of an uri
    uri = ns.get('copy_source', None)
    if uri:
        if any([container, blob, sas, snapshot, source_account_name, source_account_key]):
            raise ValueError(usage_string.format('Unused parameters are given in addition to the '
                                                 'source URI'))
        # simplest scenario--no further processing necessary
        return

    validate_client_parameters(cmd, namespace)  # must run first to resolve storage account

    # determine if the copy will happen in the same storage account
    if not source_account_name and source_account_key:
        raise ValueError(usage_string.format('Source account key is given but account name is not'))
    if not source_account_name and not source_account_key:
        # neither source account name or key is given, assume that user intends to copy blob in
        # the same account
        source_account_name = ns.get('account_name', None)
        source_account_key = ns.get('account_key', None)
    elif source_account_name and not source_account_key:
        if source_account_name == ns.get('account_name', None):
            # the source account name is same as the destination account name
            source_account_key = ns.get('account_key', None)
        else:
            # the source account is different from destination account but the key is missing
            # try to query one.
            try:
                source_account_key = _query_account_key(cmd.cli_ctx, source_account_name)
            except ValueError:
                raise ValueError('Source storage account {} not found.'.format(source_account_name))
    # else: both source account name and key are given by user

    if not source_account_name:
        raise ValueError(usage_string.format('Storage account name not found'))

    if not sas:
        sas = create_short_lived_blob_sas(cmd, source_account_name, source_account_key, container, blob)

    query_params = []
    if sas:
        query_params.append(sas)
    if snapshot:
        query_params.append('snapshot={}'.format(snapshot))

    uri = 'https://{}.blob.{}/{}/{}{}{}'.format(source_account_name,
                                                cmd.cli_ctx.cloud.suffixes.storage_endpoint,
                                                container,
                                                blob,
                                                '?' if query_params else '',
                                                '&'.join(query_params))

    namespace.copy_source = uri


def validate_source_url(cmd, namespace):  # pylint: disable=too-many-statements
    from .util import create_short_lived_blob_sas, create_short_lived_file_sas
    usage_string = \
        'Invalid usage: {}. Supply only one of the following argument sets to specify source:' \
        '\n\t   --source-uri [--source-sas]' \
        '\n\tOR --source-container --source-blob [--source-account-name & sas] [--source-snapshot]' \
        '\n\tOR --source-container --source-blob [--source-account-name & key] [--source-snapshot]' \
        '\n\tOR --source-share --source-path' \
        '\n\tOR --source-share --source-path [--source-account-name & sas]' \
        '\n\tOR --source-share --source-path [--source-account-name & key]'

    ns = vars(namespace)

    # source as blob
    container = ns.pop('source_container', None)
    blob = ns.pop('source_blob', None)
    snapshot = ns.pop('source_snapshot', None)

    # source as file
    share = ns.pop('source_share', None)
    path = ns.pop('source_path', None)
    file_snapshot = ns.pop('file_snapshot', None)

    # source credential clues
    source_account_name = ns.pop('source_account_name', None)
    source_account_key = ns.pop('source_account_key', None)
    source_sas = ns.pop('source_sas', None)

    # source in the form of an uri
    uri = ns.get('source_url', None)
    if uri:
        if any([container, blob, snapshot, share, path, file_snapshot, source_account_name,
                source_account_key]):
            raise ValueError(usage_string.format('Unused parameters are given in addition to the '
                                                 'source URI'))
        if source_sas:
            source_sas = source_sas.lstrip('?')
            uri = '{}{}{}'.format(uri, '?', source_sas)
            namespace.copy_source = uri
        return

    # ensure either a file or blob source is specified
    valid_blob_source = container and blob and not share and not path and not file_snapshot
    valid_file_source = share and path and not container and not blob and not snapshot

    if not valid_blob_source and not valid_file_source:
        raise ValueError(usage_string.format('Neither a valid blob or file source is specified'))
    if valid_blob_source and valid_file_source:
        raise ValueError(usage_string.format('Ambiguous parameters, both blob and file sources are '
                                             'specified'))

    validate_client_parameters(cmd, namespace)  # must run first to resolve storage account

    if not source_account_name:
        if source_account_key:
            raise ValueError(usage_string.format('Source account key is given but account name is not'))
        # assume that user intends to copy blob in the same account
        source_account_name = ns.get('account_name', None)

    # determine if the copy will happen in the same storage account
    same_account = False

    if not source_account_key and not source_sas:
        if source_account_name == ns.get('account_name', None):
            same_account = True
            source_account_key = ns.get('account_key', None)
            source_sas = ns.get('sas_token', None)
        else:
            # the source account is different from destination account but the key is missing try to query one.
            try:
                source_account_key = _query_account_key(cmd.cli_ctx, source_account_name)
            except ValueError:
                raise ValueError('Source storage account {} not found.'.format(source_account_name))

    # Both source account name and either key or sas (or both) are now available
    if not source_sas:
        # generate a sas token even in the same account when the source and destination are not the same kind.
        if valid_file_source and (ns.get('container_name', None) or not same_account):
            import os
            dir_name, file_name = os.path.split(path) if path else (None, '')
            source_sas = create_short_lived_file_sas(cmd, source_account_name, source_account_key, share,
                                                     dir_name, file_name)
        elif valid_blob_source and (ns.get('share_name', None) or not same_account):
            source_sas = create_short_lived_blob_sas(cmd, source_account_name, source_account_key, container, blob)

    query_params = []
    if source_sas:
        query_params.append(source_sas.lstrip('?'))
    if snapshot:
        query_params.append('snapshot={}'.format(snapshot))
    if file_snapshot:
        query_params.append('sharesnapshot={}'.format(file_snapshot))

    uri = 'https://{0}.{1}.{6}/{2}/{3}{4}{5}'.format(
        source_account_name,
        'blob' if valid_blob_source else 'file',
        container if valid_blob_source else share,
        encode_for_url(blob if valid_blob_source else path),
        '?' if query_params else '',
        '&'.join(query_params),
        cmd.cli_ctx.cloud.suffixes.storage_endpoint)

    namespace.source_url = uri


def validate_blob_type(namespace):
    if not namespace.blob_type:
        namespace.blob_type = 'page' if namespace.file_path.endswith('.vhd') else 'block'


def validate_storage_data_plane_list(namespace):
    if namespace.num_results == '*':
        namespace.num_results = None
    else:
        namespace.num_results = int(namespace.num_results)


def get_content_setting_validator(settings_class, update, guess_from_file=None):
    def _class_name(class_type):
        return class_type.__module__ + "." + class_type.__class__.__name__

    def validator(cmd, namespace):
        t_blob_content_settings = cmd.get_models('_models#ContentSettings', resource_type=CUSTOM_DATA_STORAGE_BLOB)

        # must run certain validators first for an update
        if update:
            validate_client_parameters(cmd, namespace)

        ns = vars(namespace)
        clear_content_settings = ns.pop('clear_content_settings', False)

        # retrieve the existing object properties for an update
        if update and not clear_content_settings:
            account = ns.get('account_name')
            key = ns.get('account_key')
            cs = ns.get('connection_string')
            sas = ns.get('sas_token')
            token_credential = ns.get('token_credential')
            if _class_name(settings_class) == _class_name(t_blob_content_settings):
                container = ns.get('container_name')
                blob = ns.get('blob_name')
                lease_id = ns.get('lease_id')
                client = cf_blob_client(cmd.cli_ctx, connection_string=cs, account_name=account, account_key=key,
                                        token_credential=token_credential, sas_token=sas, container=container,
                                        blob=blob)

                props = client.get_blob_properties(lease=lease_id).content_settings

        # create new properties
        new_props = settings_class(
            content_type=ns.pop('content_type', None),
            content_disposition=ns.pop('content_disposition', None),
            content_encoding=ns.pop('content_encoding', None),
            content_language=ns.pop('content_language', None),
            content_md5=ns.pop('content_md5', None),
            cache_control=ns.pop('content_cache_control', None)
        )

        # if update, fill in any None values with existing
        if update:
            if not clear_content_settings:
                for attr in ['content_type', 'content_disposition', 'content_encoding', 'content_language',
                             'content_md5', 'cache_control']:
                    if getattr(new_props, attr) is None:
                        setattr(new_props, attr, getattr(props, attr))
        else:
            if guess_from_file:
                new_props = guess_content_type(ns[guess_from_file], new_props, settings_class)

        ns['content_settings'] = new_props

    return validator


def validate_custom_domain(namespace):
    if namespace.use_subdomain and not namespace.custom_domain:
        raise ValueError('usage error: --custom-domain DOMAIN [--use-subdomain]')


def validate_encryption_services(cmd, namespace):
    """
    Builds up the encryption services object for storage account operations based on the list of services passed in.
    """
    if namespace.encryption_services:
        t_encryption_services, t_encryption_service = get_sdk(cmd.cli_ctx, ResourceType.MGMT_STORAGE,
                                                              'EncryptionServices', 'EncryptionService', mod='models')
        services = {service: t_encryption_service(enabled=True) for service in namespace.encryption_services}

        namespace.encryption_services = t_encryption_services(**services)


def validate_encryption_source(namespace):
    if namespace.encryption_key_source == 'Microsoft.Keyvault' and \
            not (namespace.encryption_key_name and namespace.encryption_key_vault):
        raise ValueError('--encryption-key-name and --encryption-key-vault are required '
                         'when --encryption-key-source=Microsoft.Keyvault is specified.')

    if namespace.encryption_key_name or namespace.encryption_key_version is not None or namespace.encryption_key_vault:
        if namespace.encryption_key_source and namespace.encryption_key_source != 'Microsoft.Keyvault':
            raise ValueError('--encryption-key-name, --encryption-key-vault, and --encryption-key-version are not '
                             'applicable without Microsoft.Keyvault key-source.')


def validate_entity(namespace):
    """ Converts a list of key value pairs into a dictionary. Ensures that required
    RowKey and PartitionKey are converted to the correct case and included. """
    values = dict(x.split('=', 1) for x in namespace.entity)
    keys = values.keys()
    for key in list(keys):
        if key.lower() == 'rowkey':
            val = values[key]
            del values[key]
            values['RowKey'] = val
        elif key.lower() == 'partitionkey':
            val = values[key]
            del values[key]
            values['PartitionKey'] = val
    keys = values.keys()
    missing_keys = 'RowKey ' if 'RowKey' not in keys else ''
    missing_keys = '{}PartitionKey'.format(missing_keys) \
        if 'PartitionKey' not in keys else missing_keys
    if missing_keys:
        raise argparse.ArgumentError(
            None, 'incorrect usage: entity requires: {}'.format(missing_keys))

    def cast_val(key, val):
        """ Attempts to cast numeric values (except RowKey and PartitionKey) to numbers so they
        can be queried correctly. """
        if key in ['PartitionKey', 'RowKey']:
            return val

        def try_cast(to_type):
            try:
                return to_type(val)
            except ValueError:
                return None

        return try_cast(int) or try_cast(float) or val

    # ensure numbers are converted from strings so querying will work correctly
    values = {key: cast_val(key, val) for key, val in values.items()}
    namespace.entity = values


def validate_marker(namespace):
    """ Converts a list of key value pairs into a dictionary. Ensures that required
    nextrowkey and nextpartitionkey are included. """
    if not namespace.marker:
        return
    marker = dict(x.split('=', 1) for x in namespace.marker)
    expected_keys = {'nextrowkey', 'nextpartitionkey'}

    for key in list(marker.keys()):
        new_key = key.lower()
        if new_key in expected_keys:
            expected_keys.remove(key.lower())
            val = marker[key]
            del marker[key]
            marker[new_key] = val
    if expected_keys:
        raise argparse.ArgumentError(
            None, 'incorrect usage: marker requires: {}'.format(' '.join(expected_keys)))

    namespace.marker = marker


def get_file_path_validator(default_file_param=None):
    """ Creates a namespace validator that splits out 'path' into 'directory_name' and 'file_name'.
    Allows another path-type parameter to be named which can supply a default filename. """

    def validator(namespace):
        import os
        if not hasattr(namespace, 'path'):
            return

        path = namespace.path
        dir_name, file_name = os.path.split(path) if path else (None, '')

        if default_file_param and '.' not in file_name:
            dir_name = path
            file_name = os.path.split(getattr(namespace, default_file_param))[1]
        dir_name = None if dir_name in ('', '.') else dir_name
        namespace.directory_name = dir_name
        namespace.file_name = file_name
        del namespace.path

    return validator


def validate_included_datasets_v2(cmd, namespace):
    if namespace.include:
        short_include = namespace.include
        if set(short_include) - set('cmsdvt'):
            help_string = '(c)opy-info (m)etadata (s)napshots (d)eleted (v)ersions (t)ags'
            raise ValueError('valid values are {} or a combination thereof.'.format(help_string))
        t_blob_include = cmd.get_models('_generated.models._azure_blob_storage_enums#ListBlobsIncludeItem')
        include = []
        if short_include.startswith('s'):
            include.append(t_blob_include.snapshots)
        if short_include.startswith('m'):
            include.append(t_blob_include.metadata)
        if short_include.startswith('c'):
            include.append(t_blob_include.copy)
        if short_include.startswith('d'):
            include.append(t_blob_include.deleted)
        if short_include.startswith('v'):
            include.append(t_blob_include.versions)
        if short_include.startswith('t'):
            include.append(t_blob_include.tags)
        namespace.include = include


def validate_key_name(namespace):
    key_options = {'primary': '1', 'secondary': '2'}
    if hasattr(namespace, 'key_type') and namespace.key_type:
        namespace.key_name = namespace.key_type + key_options[namespace.key_name]
    else:
        namespace.key_name = storage_account_key_options[namespace.key_name]


def validate_metadata(namespace):
    if namespace.metadata:
        namespace.metadata = dict(x.split('=', 1) for x in namespace.metadata)


def get_permission_allowed_values(permission_class):
    if permission_class:
        instance = permission_class()

        allowed_values = [x.lower() for x in dir(instance) if not x.startswith('_')]
        allowed_values.remove('from_string')
        for i, item in enumerate(allowed_values):
            if item == 'delete_previous_version':
                allowed_values[i] = 'x' + item
        return allowed_values
    return None


def get_permission_help_string(permission_class):
    allowed_values = get_permission_allowed_values(permission_class)

    return ' '.join(['({}){}'.format(x[0], x[1:]) for x in allowed_values])


def get_permission_validator(permission_class):
    allowed_values = get_permission_allowed_values(permission_class)
    allowed_string = ''.join(x[0] for x in allowed_values)

    def validator(namespace):
        if namespace.permission:
            if set(namespace.permission) - set(allowed_string):
                help_string = get_permission_help_string(permission_class)
                raise ValueError(
                    'valid values are {} or a combination thereof.'.format(help_string))
            namespace.permission = permission_class.from_string(namespace.permission)

    return validator


def table_permission_validator(cmd, namespace):
    """ A special case for table because the SDK associates the QUERY permission with 'r' """
    t_table_permissions = get_table_data_type(cmd.cli_ctx, 'table', 'TablePermissions')
    if namespace.permission:
        if set(namespace.permission) - set('raud'):
            help_string = '(r)ead/query (a)dd (u)pdate (d)elete'
            raise ValueError('valid values are {} or a combination thereof.'.format(help_string))
        namespace.permission = t_table_permissions(_str=namespace.permission)


def validate_fs_public_access(cmd, namespace):
    from .sdkutil import get_fs_access_type

    if namespace.public_access:
        namespace.public_access = get_fs_access_type(cmd.cli_ctx, namespace.public_access.lower())


def validate_select(namespace):
    if namespace.select:
        namespace.select = ','.join(namespace.select)


def add_progress_callback(cmd, namespace):
    def _update_progress(current, total):
        message = getattr(_update_progress, 'message', 'Alive')
        reuse = getattr(_update_progress, 'reuse', False)

        if total:
            hook.add(message=message, value=current, total_val=total)
            if total == current and not reuse:
                hook.end()

    hook = cmd.cli_ctx.get_progress_controller(det=True)
    _update_progress.hook = hook

    if not namespace.no_progress:
        namespace.progress_callback = _update_progress
    del namespace.no_progress


def add_progress_callback_v2(cmd, namespace):
    def _update_progress(response):
        if response.http_response.status_code not in [200, 201]:
            return

        message = getattr(_update_progress, 'message', 'Alive')
        reuse = getattr(_update_progress, 'reuse', False)
        current = response.context['upload_stream_current']
        total = response.context['data_stream_total']

        if total:
            hook.add(message=message, value=current, total_val=total)
            if total == current and not reuse:
                hook.end()

    hook = cmd.cli_ctx.get_progress_controller(det=True)
    _update_progress.hook = hook

    if not namespace.no_progress:
        namespace.progress_callback = _update_progress
    del namespace.no_progress


def process_container_delete_parameters(cmd, namespace):
    """Process the parameters for storage container delete command"""
    # check whether to use mgmt or data-plane
    if namespace.bypass_immutability_policy:
        # use management-plane
        namespace.processed_account_name = namespace.account_name
        namespace.processed_resource_group, namespace.mgmt_client = _query_account_rg(
            cmd.cli_ctx, namespace.account_name)
        del namespace.auth_mode
    else:
        # use data-plane, like before
        validate_client_parameters(cmd, namespace)


def process_file_download_namespace(namespace):
    import os

    get_file_path_validator()(namespace)

    dest = namespace.file_path
    if not dest or os.path.isdir(dest):
        namespace.file_path = os.path.join(dest, namespace.file_name) \
            if dest else namespace.file_name


def process_metric_update_namespace(namespace):
    namespace.hour = namespace.hour == 'true'
    namespace.minute = namespace.minute == 'true'
    namespace.api = namespace.api == 'true' if namespace.api else None
    if namespace.hour is None and namespace.minute is None:
        raise argparse.ArgumentError(
            None, 'incorrect usage: must specify --hour and/or --minute')
    if (namespace.hour or namespace.minute) and namespace.api is None:
        raise argparse.ArgumentError(
            None, 'incorrect usage: specify --api when hour or minute metrics are enabled')


def validate_subnet(cmd, namespace):
    from msrestazure.tools import resource_id, is_valid_resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id

    subnet = namespace.subnet
    subnet_is_id = is_valid_resource_id(subnet)
    vnet = namespace.vnet_name

    if (subnet_is_id and not vnet) or (not subnet and not vnet):
        return
    if subnet and not subnet_is_id and vnet:
        namespace.subnet = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network',
            type='virtualNetworks',
            name=vnet,
            child_type_1='subnets',
            child_name_1=subnet)
    else:
        raise CLIError('incorrect usage: [--subnet ID | --subnet NAME --vnet-name NAME]')


def get_datetime_type(to_string):
    """ Validates UTC datetime. Examples of accepted forms:
    2017-12-31T01:11:59Z,2017-12-31T01:11Z or 2017-12-31T01Z or 2017-12-31 """
    from datetime import datetime

    def datetime_type(string):
        """ Validates UTC datetime. Examples of accepted forms:
        2017-12-31T01:11:59Z,2017-12-31T01:11Z or 2017-12-31T01Z or 2017-12-31 """
        accepted_date_formats = ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%MZ',
                                 '%Y-%m-%dT%HZ', '%Y-%m-%d']
        for form in accepted_date_formats:
            try:
                if to_string:
                    return datetime.strptime(string, form).strftime(form)

                return datetime.strptime(string, form)
            except ValueError:
                continue
        raise ValueError("Input '{}' not valid. Valid example: 2000-12-31T12:59:59Z".format(string))

    return datetime_type


def ipv4_range_type(string):
    """ Validates an IPv4 address or address range. """
    import re
    ip_format = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    if not re.match("^{}$".format(ip_format), string):
        if not re.match("^{ip_format}-{ip_format}$".format(ip_format=ip_format), string):
            raise ValueError
    return string


def resource_type_type(loader):
    """ Returns a function which validates that resource types string contains only a combination of service,
    container, and object. Their shorthand representations are s, c, and o. """

    def impl(string):
        t_resources = loader.get_models('common.models#ResourceTypes')
        if set(string) - set("sco"):
            raise ValueError
        return t_resources(_str=''.join(set(string)))

    return impl


def services_type(loader):
    """ Returns a function which validates that services string contains only a combination of blob, queue, table,
    and file. Their shorthand representations are b, q, t, and f. """

    def impl(string):
        t_services = loader.get_models('common.models#Services')
        if set(string) - set("bqtf"):
            raise ValueError
        return t_services(_str=''.join(set(string)))

    return impl


def get_char_options_validator(types, property_name):
    def _validator(namespace):
        service_types = set(getattr(namespace, property_name, list()))

        if not service_types:
            raise ValueError('Missing options --{}.'.format(property_name.replace('_', '-')))

        if service_types - set(types):
            raise ValueError(
                '--{}: only valid values are: {}.'.format(property_name.replace('_', '-'), ', '.join(types)))

        setattr(namespace, property_name, service_types)

    return _validator


def page_blob_tier_validator(cmd, namespace):
    if not namespace.tier:
        return

    if namespace.blob_type != 'page' and namespace.tier:
        raise ValueError('Blob tier is only applicable to page blobs on premium storage accounts.')

    try:
        namespace.premium_page_blob_tier = getattr(cmd.get_models('_models#PremiumPageBlobTier'), namespace.tier)
    except AttributeError:
        from azure.cli.command_modules.storage.sdkutil import get_blob_tier_names
        raise ValueError('Unknown premium page blob tier name. Choose among {}'.format(', '.join(
            get_blob_tier_names(cmd.cli_ctx, 'PremiumPageBlobTier'))))


def block_blob_tier_validator(cmd, namespace):
    if not namespace.tier:
        return

    if namespace.blob_type != 'block' and namespace.tier:
        raise ValueError('Blob tier is only applicable to block blobs on standard storage accounts.')

    try:
        namespace.standard_blob_tier = getattr(cmd.get_models('_models#StandardBlobTier'), namespace.tier)
    except AttributeError:
        from azure.cli.command_modules.storage.sdkutil import get_blob_tier_names
        raise ValueError('Unknown block blob tier name. Choose among {}'.format(', '.join(
            get_blob_tier_names(cmd.cli_ctx, 'StandardBlobTier'))))


def blob_tier_validator(cmd, namespace):
    if namespace.tier:
        if namespace.blob_type == 'page':
            page_blob_tier_validator(cmd, namespace)
        elif namespace.blob_type == 'block':
            block_blob_tier_validator(cmd, namespace)
        else:
            raise ValueError('Blob tier is only applicable to block or page blob.')
    del namespace.tier


def blob_rehydrate_priority_validator(namespace):
    if namespace.blob_type == 'page' and namespace.rehydrate_priority:
        raise ValueError('--rehydrate-priority is only applicable to block blob.')
    if namespace.tier == 'Archive' and namespace.rehydrate_priority:
        raise ValueError('--rehydrate-priority is only applicable to rehydrate blob data from the archive tier.')
    if namespace.rehydrate_priority is None:
        namespace.rehydrate_priority = 'Standard'


def as_user_validator(namespace):
    if hasattr(namespace, 'token_credential') and not namespace.as_user:
        raise CLIError('incorrect usage: specify --as-user when --auth-mode login is used to get user delegation key.')
    if namespace.as_user:
        if namespace.expiry is None:
            raise argparse.ArgumentError(
                None, 'incorrect usage: specify --expiry when as-user is enabled')

        expiry = get_datetime_type(False)(namespace.expiry)

        from datetime import datetime, timedelta
        if expiry > datetime.utcnow() + timedelta(days=7):
            raise argparse.ArgumentError(
                None, 'incorrect usage: --expiry should be within 7 days from now')

        if ((not hasattr(namespace, 'token_credential') or namespace.token_credential is None) and
                (not hasattr(namespace, 'auth_mode') or namespace.auth_mode != 'login')):
            raise argparse.ArgumentError(
                None, "incorrect usage: specify '--auth-mode login' when as-user is enabled")


def validator_delete_retention_days(namespace, enable=None, days=None):
    enable_param = '--' + enable.replace('_', '-')
    days_param = '--' + enable.replace('_', '-')
    enable = getattr(namespace, enable)
    days = getattr(namespace, days)

    if enable is True and days is None:
        raise ValueError(
            "incorrect usage: you have to provide value for '{}' when '{}' "
            "is set to true".format(days_param, enable_param))

    if enable is False and days is not None:
        raise ValueError(
            "incorrect usage: '{}' is invalid when '{}' is set to false".format(days_param, enable_param))

    if enable is None and days is not None:
        raise ValueError(
            "incorrect usage: please specify '{} true' if you want to set the value for "
            "'{}'".format(enable_param, days_param))

    if days or days == 0:
        if days < 1:
            raise ValueError(
                "incorrect usage: '{}' must be greater than or equal to 1".format(days_param))
        if days > 365:
            raise ValueError(
                "incorrect usage: '{}' must be less than or equal to 365".format(days_param))


def validate_container_delete_retention_days(namespace):
    validator_delete_retention_days(namespace, enable='enable_container_delete_retention',
                                    days='container_delete_retention_days')


def validate_delete_retention_days(namespace):
    validator_delete_retention_days(namespace, enable='enable_delete_retention',
                                    days='delete_retention_days')


# pylint: disable=too-few-public-methods
class BlobRangeAddAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace.blob_ranges:
            namespace.blob_ranges = []
        if isinstance(values, list):
            values = ' '.join(values)
        BlobRange = namespace._cmd.get_models('BlobRestoreRange', resource_type=ResourceType.MGMT_STORAGE)
        try:
            start_range, end_range = values.split(' ')
        except (ValueError, TypeError):
            raise CLIError('usage error: --blob-range VARIABLE OPERATOR VALUE')
        namespace.blob_ranges.append(BlobRange(
            start_range=start_range,
            end_range=end_range
        ))


def validate_private_endpoint_connection_id(cmd, namespace):
    if namespace.connection_id:
        from azure.cli.core.util import parse_proxy_resource_id
        result = parse_proxy_resource_id(namespace.connection_id)
        namespace.resource_group_name = result['resource_group']
        namespace.account_name = result['name']
        namespace.private_endpoint_connection_name = result['child_name_1']

    if namespace.account_name and not namespace.resource_group_name:
        namespace.resource_group_name = _query_account_rg(cmd.cli_ctx, namespace.account_name)[0]

    if not all([namespace.account_name, namespace.resource_group_name, namespace.private_endpoint_connection_name]):
        raise CLIError('incorrect usage: [--id ID | --name NAME --account-name NAME]')

    del namespace.connection_id


def pop_data_client_auth(ns):
    del ns.auth_mode
    del ns.account_key
    del ns.connection_string
    del ns.sas_token


def validate_client_auth_parameter(cmd, ns):
    from .sdkutil import get_container_access_type
    if ns.public_access:
        ns.public_access = get_container_access_type(cmd.cli_ctx, ns.public_access.lower())
    if ns.default_encryption_scope and ns.prevent_encryption_scope_override is not None:
        # simply try to retrieve the remaining variables from environment variables
        if not ns.account_name:
            ns.account_name = get_config_value(cmd, 'storage', 'account', None)
        if ns.account_name and not ns.resource_group_name:
            ns.resource_group_name = _query_account_rg(cmd.cli_ctx, account_name=ns.account_name)[0]
        pop_data_client_auth(ns)
    elif (ns.default_encryption_scope and ns.prevent_encryption_scope_override is None) or \
         (not ns.default_encryption_scope and ns.prevent_encryption_scope_override is not None):
        raise CLIError("usage error: You need to specify both --default-encryption-scope and "
                       "--prevent-encryption-scope-override to set encryption scope information "
                       "when creating container.")
    else:
        validate_client_parameters(cmd, ns)


def validate_encryption_scope_client_params(ns):
    if ns.encryption_scope:
        # will use track2 client and socket_timeout is unused
        del ns.socket_timeout


def validate_access_control(namespace):
    if namespace.acl and namespace.permissions:
        raise CLIError('usage error: invalid when specifying both --acl and --permissions.')


def validate_service_type(services, service_type):
    if service_type == 'table':
        return 't' in services
    if service_type == 'blob':
        return 'b' in services
    if service_type == 'queue':
        return 'q' in services


def validate_logging_version(namespace):
    if validate_service_type(namespace.services, 'table') and namespace.version != 1.0:
        raise CLIError(
            'incorrect usage: for table service, the supported version for logging is `1.0`. For more information, '
            'please refer to https://docs.microsoft.com/en-us/rest/api/storageservices/storage-analytics-log-format.')


def validate_match_condition(namespace):
    from .track2_util import _if_match, _if_none_match
    if namespace.if_match:
        namespace = _if_match(if_match=namespace.if_match, **namespace)
        del namespace.if_match
    if namespace.if_none_match:
        namespace = _if_none_match(if_none_match=namespace.if_none_match, **namespace)
        del namespace.if_none_match
