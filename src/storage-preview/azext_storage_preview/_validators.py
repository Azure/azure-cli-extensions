# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access, logging-format-interpolation
import os
import argparse

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.commands.validators import validate_key_value_pairs
from azure.cli.core.profiles import get_sdk
from knack.util import CLIError
from knack.log import get_logger
from ._client_factory import get_storage_data_service_client, blob_data_service_factory, cf_blob_service, \
    cf_share_service, cf_share_client
from .util import guess_content_type
from .oauth_token_util import TokenUpdater
from .profiles import CUSTOM_MGMT_STORAGE, CUSTOM_DATA_STORAGE_FILESHARE, CUSTOM_DATA_STORAGE_BLOB
from .url_quote_util import encode_for_url
logger = get_logger(__name__)


storage_account_key_options = {'primary': 'key1', 'secondary': 'key2'}


# Utilities


# pylint: disable=inconsistent-return-statements, too-many-lines
def _query_account_key(cli_ctx, account_name):
    """Query the storage account key. This is used when the customer doesn't offer account key but name."""
    rg, scf = _query_account_rg(cli_ctx, account_name)
    t_storage_account_keys = get_sdk(
        cli_ctx, CUSTOM_MGMT_STORAGE, 'models.storage_account_keys#StorageAccountKeys')

    if t_storage_account_keys:
        return scf.storage_accounts.list_keys(rg, account_name).key1
    # of type: models.storage_account_list_keys_result#StorageAccountListKeysResult
    return scf.storage_accounts.list_keys(rg, account_name).keys[0].value  # pylint: disable=no-member


def _query_account_rg(cli_ctx, account_name):
    """Query the storage account's resource group, which the mgmt sdk requires."""
    scf = get_mgmt_service_client(cli_ctx, CUSTOM_MGMT_STORAGE)
    acc = next((x for x in scf.storage_accounts.list() if x.name == account_name), None)
    if acc:
        from msrestazure.tools import parse_resource_id
        return parse_resource_id(acc.id)['resource_group'], scf
    raise ValueError("Storage account '{}' not found.".format(account_name))


def _create_token_credential(cli_ctx):
    from knack.cli import EVENT_CLI_POST_EXECUTE
    from .profiles import CUSTOM_DATA_STORAGE

    TokenCredential = get_sdk(cli_ctx, CUSTOM_DATA_STORAGE, 'common#TokenCredential')

    token_credential = TokenCredential()
    updater = TokenUpdater(token_credential, cli_ctx)

    def _cancel_timer_event_handler(_, **__):
        updater.cancel()
    cli_ctx.register_event(EVENT_CLI_POST_EXECUTE, _cancel_timer_event_handler)
    return token_credential


# region PARAMETER VALIDATORS

def process_resource_group(cmd, namespace):
    """Processes the resource group parameter from the account name"""
    if namespace.account_name and not namespace.resource_group_name:
        namespace.resource_group_name = _query_account_rg(cmd.cli_ctx, namespace.account_name)[0]


def validate_bypass(namespace):
    if namespace.bypass:
        namespace.bypass = ', '.join(namespace.bypass) if isinstance(namespace.bypass, list) else namespace.bypass


def get_config_value(cmd, section, key, default):
    return cmd.cli_ctx.config.get(section, key, default)


def is_storagev2(import_prefix):
    return import_prefix.startswith('azure.multiapi.storagev2.') or 'datalake' in import_prefix


def validate_client_parameters(cmd, namespace):
    """ Retrieves storage connection parameters from environment variables and parses out connection string into
    account name and key """
    n = namespace

    if hasattr(n, 'auth_mode'):
        auth_mode = n.auth_mode or get_config_value(cmd, 'storage', 'auth_mode', None)
        del n.auth_mode
        if not n.account_name:
            if hasattr(n, 'account_url') and not n.account_url:
                n.account_name = get_config_value(cmd, 'storage', 'account', None)
                n.account_url = get_config_value(cmd, 'storage', 'account_url', None)
            else:
                n.account_name = get_config_value(cmd, 'storage', 'account', None)
        if auth_mode == 'login':
            # is_storagv2() is used to distinguish if the command is in track2 SDK
            # If yes, we will use get_login_credentials() as token credential
            from azure.cli.core._profile import Profile
            profile = Profile(cli_ctx=cmd.cli_ctx)
            n.token_credential, _, _ = profile.get_login_credentials(subscription_id=n._subscription)

    if hasattr(n, 'token_credential') and n.token_credential:
        # give warning if there are account key args being ignored
        account_key_args = [n.account_key and "--account-key", n.sas_token and "--sas-token",
                            n.connection_string and "--connection-string"]
        account_key_args = [arg for arg in account_key_args if arg]

        if account_key_args:
            logger.warning('In "login" auth mode, the following arguments are ignored: %s',
                           ' ,'.join(account_key_args))
        return

    # When there is no input for credential, we will read environment variable
    if not n.connection_string and not n.account_key and not n.sas_token:
        n.connection_string = get_config_value(cmd, 'storage', 'connection_string', None)

    # if connection string supplied or in environment variables, extract account key and name
    if n.connection_string:
        conn_dict = validate_key_value_pairs(n.connection_string)
        n.account_name = conn_dict.get('AccountName')
        n.account_key = conn_dict.get('AccountKey')
        n.sas_token = conn_dict.get('SharedAccessSignature')

    # otherwise, simply try to retrieve the remaining variables from environment variables
    if not n.account_name:
        if hasattr(n, 'account_url') and not n.account_url:
            n.account_name = get_config_value(cmd, 'storage', 'account', None)
            n.account_url = get_config_value(cmd, 'storage', 'account_url', None)
        else:
            n.account_name = get_config_value(cmd, 'storage', 'account', None)
    if not n.account_key and not n.sas_token:
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
        message = """
There are no credentials provided in your command and environment, we will query for account key for your storage account.
It is recommended to provide --connection-string, --account-key or --sas-token in your command as credentials.
"""
        if 'auth_mode' in cmd.arguments:
            message += """
You also can add `--auth-mode login` in your command to use Azure Active Directory (Azure AD) for authorization if your login account is assigned required RBAC roles.
For more information about RBAC roles in storage, visit https://docs.microsoft.com/azure/storage/common/storage-auth-aad-rbac-cli.
"""
        logger.warning('%s\nIn addition, setting the corresponding environment variables can avoid inputting '
                       'credentials in your command. Please use --help to get more information about environment '
                       'variable usage.', message)
        try:
            n.account_key = _query_account_key(cmd.cli_ctx, n.account_name)
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning("\nSkip querying account key due to failure: %s", ex)

    if hasattr(n, 'account_url') and n.account_url and not n.account_key and not n.sas_token:
        message = """
There are no credentials provided in your command and environment.
Please provide --connection-string, --account-key or --sas-token in your command as credentials.
        """

        if 'auth_mode' in cmd.arguments:
            message += """
You also can add `--auth-mode login` in your command to use Azure Active Directory (Azure AD) for authorization if your login account is assigned required RBAC roles.
For more information about RBAC roles in storage, visit https://docs.microsoft.com/azure/storage/common/storage-auth-aad-rbac-cli."
            """
        from azure.cli.core.azclierror import InvalidArgumentValueError
        raise InvalidArgumentValueError(message)


def validate_azcopy_blob_source_url(cmd, namespace):
    client = blob_data_service_factory(cmd.cli_ctx, {
        'account_name': namespace.account_name})
    blob_name = namespace.source_blob
    if not blob_name:
        blob_name = os.path.basename(namespace.destination)
    url = client.make_blob_url(namespace.source_container, blob_name)
    namespace.source = url
    del namespace.source_container
    del namespace.source_blob


def validate_azcopy_container_source_url(cmd, namespace):
    client = blob_data_service_factory(cmd.cli_ctx, {
        'account_name': namespace.account_name})
    url = client.make_blob_url(namespace.source, '')
    namespace.source = url[:-1]


def validate_azcopy_upload_destination_url(cmd, namespace):
    client = blob_data_service_factory(cmd.cli_ctx, {
        'account_name': namespace.account_name})
    destination_path = namespace.destination_path
    if not destination_path:
        destination_path = ''
    url = client.make_blob_url(namespace.destination_container, destination_path)
    namespace.destination = url
    del namespace.destination_container
    del namespace.destination_path


def validate_blob_directory_download_source_url(cmd, namespace):
    client = blob_data_service_factory(cmd.cli_ctx, {
        'account_name': namespace.account_name})
    source_path = namespace.source_path
    url = client.make_blob_url(namespace.source_container, source_path)
    namespace.source = url
    del namespace.source_container
    del namespace.source_path


def validate_blob_directory_upload_destination_url(cmd, namespace):
    ns = vars(namespace)
    destination = ns.get('destination_path')
    container = ns.get('destination_container')
    client = get_blob_client(cmd, ns)
    destination = destination[1:] if destination.startswith('/') else destination
    from azure.common import AzureException
    try:
        props = client.get_blob_properties(container, destination)
        if not is_directory(props):
            raise ValueError('usage error: You are specifying --destination-path with a blob name, not directory name. '
                             'Please change to a valid blob directory name. If you want to upload to a blob file, '
                             'please use `az storage blob upload` command.')
    except AzureException:
        pass

    if not destination.endswith('/'):
        destination += '/'
    url = client.make_blob_url(container, destination)
    namespace.destination = url
    del namespace.destination_container
    del namespace.destination_path


def validate_azcopy_download_source_url(cmd, namespace):
    client = blob_data_service_factory(cmd.cli_ctx, {
        'account_name': namespace.account_name})
    source_path = namespace.source_path
    if not source_path:
        source_path = ''
    url = client.make_blob_url(namespace.source_container, source_path)
    namespace.source = url
    del namespace.source_container
    del namespace.source_path
    print(namespace)


def validate_azcopy_target_url(cmd, namespace):
    client = blob_data_service_factory(cmd.cli_ctx, {
        'account_name': namespace.account_name})
    target_path = namespace.target_path
    if not target_path:
        target_path = ''
    url = client.make_blob_url(namespace.target_container, target_path)
    namespace.target = url
    del namespace.target_container
    del namespace.target_path


def get_content_setting_validator(settings_class, update, guess_from_file=None, process_md5=False):
    def _class_name(class_type):
        return class_type.__module__ + "." + class_type.__class__.__name__

    def validator(cmd, namespace):
        t_blob_content_settings = get_sdk(cmd.cli_ctx, CUSTOM_DATA_STORAGE_BLOB, '_models#ContentSettings')
        t_file_content_settings = get_sdk(cmd.cli_ctx, CUSTOM_DATA_STORAGE_FILESHARE, '_models#ContentSettings')

        # must run certain validators first for an update
        if update:
            validate_client_parameters(cmd, namespace)
        if update and _class_name(settings_class) == _class_name(t_file_content_settings):
            get_file_path_validator()(namespace)

        ns = vars(namespace)
        clear_content_settings = ns.pop('clear_content_settings', False)

        # retrieve the existing object properties for an update
        if update and not clear_content_settings:
            account = ns.get('account_name')
            key = ns.get('account_key')
            cs = ns.get('connection_string')
            sas = ns.get('sas_token')
            token_credential = ns.get('token_credential')
            account_kwargs = {'connection_string': cs,
                              'account_name': account,
                              'account_key': key,
                              'token_credential': token_credential,
                              'sas_token': sas}
            if _class_name(settings_class) == _class_name(t_blob_content_settings):
                container = ns.get('container_name')
                blob = ns.get('blob_name')
                lease_id = ns.get('lease_id')
                client = cf_blob_service(cmd.cli_ctx, account_kwargs).get_blob_client(container=container,
                                                                                      blob=blob)
                props = client.get_blob_properties(lease=lease_id).content_settings
            elif _class_name(settings_class) == _class_name(t_file_content_settings):
                share = ns.get('share_name')
                directory = ns.get('directory_name')
                filename = ns.get('file_name')
                account_kwargs["share_name"] = share
                account_kwargs["snapshot"] = ns.get('snapshot')
                if ns.get('enable_file_backup_request_intent', None):
                    account_kwargs["enable_file_backup_request_intent"] = ns.get("enable_file_backup_request_intent")
                client = cf_share_client(cmd.cli_ctx, account_kwargs). \
                    get_directory_client(directory_path=directory). \
                    get_file_client(file_name=filename)
                props = client.get_file_properties().content_settings

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

        # In track2 SDK, the content_md5 type should be bytearray. And then it will serialize to a string for request.
        # To keep consistent with track1 input and CLI will treat all parameter values as string. Here is to transform
        # content_md5 value to bytearray. And track2 SDK will serialize it into the right value with str type in header.
        if process_md5 and new_props.content_md5:
            if not isinstance(new_props.content_md5, bytearray):
                from .track2_util import _str_to_bytearray
                new_props.content_md5 = _str_to_bytearray(new_props.content_md5)

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
        t_encryption_services, t_encryption_service = get_sdk(cmd.cli_ctx, CUSTOM_MGMT_STORAGE,
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


def get_file_path_validator(default_file_param=None):
    """ Creates a namespace validator that splits out 'path' into 'directory_name' and 'file_name'.
    Allows another path-type parameter to be named which can supply a default filename. """

    def validator(namespace):
        if not hasattr(namespace, 'path'):
            return

        path = namespace.path
        dir_name, file_name = os.path.split(path) if path else (None, '')
        if dir_name and dir_name.startswith('./'):
            dir_name = dir_name.replace('./', '', 1)

        if default_file_param and '.' not in file_name:
            dir_name = path
            file_name = os.path.split(getattr(namespace, default_file_param))[1]
        dir_name = None if dir_name in ('', '.') else dir_name
        namespace.directory_name = dir_name
        namespace.file_name = file_name
        del namespace.path

    return validator


def validate_key(namespace):
    namespace.key_name = storage_account_key_options[namespace.key_name]


def validate_metadata(namespace):
    if namespace.metadata:
        namespace.metadata = dict(x.split('=', 1) for x in namespace.metadata)


def validate_storage_account(cmd, namespace):
    n = namespace
    rg, scf = _query_account_rg(cmd.cli_ctx, n.account_name)

    storage_account_property = scf.storage_accounts.get_properties(rg, n.account_name)  # pylint: disable=no-member
    if "access" in cmd.name:
        if not storage_account_property.is_hns_enabled:
            raise CLIError("You storage account doesn't enable HNS property.")


def validate_immutability_arguments(namespace):
    from azure.cli.core.azclierror import InvalidArgumentValueError
    if not namespace.enable_alw:
        if any([namespace.immutability_period_since_creation_in_days,
                namespace.immutability_policy_state, namespace.allow_protected_append_writes is not None]):
            raise InvalidArgumentValueError("Incorrect usage: To enable account level immutability, "
                                            "need to specify --enable-alw true. "
                                            "Cannot set --enable_alw to false and specify "
                                            "--immutability-period --immutability-state "
                                            "--allow-append")


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


def validate_included_datasets(cmd, namespace):
    if namespace.include:
        include = namespace.include
        if set(include) - set('cmsd'):
            help_string = '(c)opy-info (m)etadata (s)napshots (d)eleted'
            raise ValueError('valid values are {} or a combination thereof.'.format(help_string))
        t_blob_include = cmd.get_models('blob#Include')
        namespace.include = t_blob_include('s' in include, 'm' in include, False, 'c' in include, 'd' in include)


def validate_storage_data_plane_list(namespace):
    if namespace.num_results == '*':
        namespace.num_results = None
    else:
        namespace.num_results = int(namespace.num_results)


def get_blob_client(cmd, ns):
    t_base_blob_service = cmd.get_models('blob.baseblobservice#BaseBlobService')
    account = ns.get('account_name')
    key = ns.get('account_key')
    cs = ns.get('connection_string')
    sas = ns.get('sas_token')
    client = get_storage_data_service_client(cmd.cli_ctx,
                                             t_base_blob_service,
                                             account,
                                             key,
                                             cs,
                                             sas)
    return client


def is_directory(props):
    return 'hdi_isfolder' in props.metadata.keys() and props.metadata['hdi_isfolder'] == 'true'


def validate_move_file(cmd, namespace):
    ns = vars(namespace)
    client = get_blob_client(cmd, ns)
    source = ns.get('source_path')
    container = ns.get('container_name')
    lease_id = ns.get('lease_id')
    # Check Source
    props = client.get_blob_properties(container, source, lease_id=lease_id)
    if is_directory(props):
        raise ValueError('usage error: You are specifying --source-blob with a blob directory name. '
                         'Please change to a valid blob name. If you want to move a blob directory, '
                         'please use `az storage blob directory move` command.')
    # Check Destination
    destination = ns.get('new_path')
    if client.exists(container, destination):
        logger.warning('The destination blob name already exists in current container. '
                       'The existing blob "{}" will be overwritten.'.format(destination))


def validate_move_directory(cmd, namespace):
    ns = vars(namespace)
    client = get_blob_client(cmd, ns)
    source = ns.get('source_path')
    container = ns.get('container_name')
    lease_id = ns.get('lease_id')
    # Check Source
    props = client.get_blob_properties(container, source, lease_id=lease_id)
    if not is_directory(props):
        raise ValueError('usage error: You are specifying --source-path with a blob name, not directory name. '
                         'Please change to a valid blob directory name. If you want to move a blob file, '
                         'please use `az storage blob move` command.')
    # Check Destination
    destination = ns.get('new_path')
    if client.exists(container, destination):
        logger.warning('The destination directory already exists in current container. If continue, '
                       'the existing directory "{}" will be overwritten.'.format(destination))


def validate_directory_name(cmd, namespace):
    ns = vars(namespace)
    client = get_blob_client(cmd, ns)
    source = ns.get('directory_path')
    container = ns.get('container_name')

    # Check Source
    if client.exists(container, source):
        raise ValueError('usage error: The specified --directory-path already exists in current container. '
                         'Please change to a valid blob directory name. If you want to rename a directory, '
                         'please use `az storage blob directory move` command.')


def add_upload_progress_callback(cmd, namespace):
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


def process_file_upload_batch_parameters(cmd, namespace):
    """Process the parameters of storage file batch upload command"""
    # 1. quick check
    if not os.path.exists(namespace.source):
        raise ValueError('incorrect usage: source {} does not exist'.format(namespace.source))

    if not os.path.isdir(namespace.source):
        raise ValueError('incorrect usage: source must be a directory')

    # 2. try to extract account name and container name from destination string
    from .storage_url_helpers import StorageResourceIdentifier
    identifier = StorageResourceIdentifier(cmd.cli_ctx.cloud, namespace.destination)
    if identifier.is_url():
        if identifier.filename or identifier.directory:
            raise ValueError('incorrect usage: destination must be a file share url')

        namespace.destination = identifier.share

        if not namespace.account_name:
            namespace.account_name = identifier.account_name

    namespace.source = os.path.realpath(namespace.source)
    namespace.share_name = namespace.destination


# pylint: disable=too-few-public-methods
class PermissionScopeAddAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace.permission_scope:
            namespace.permission_scope = []
        PermissionScope = namespace._cmd.get_models('PermissionScope')
        try:
            permissions, service, resource_name = '', '', ''
            for s in values:
                if "permissions" in s:
                    permissions = s.split('=')[1]
                elif "service" in s:
                    service = s.split('=')[1]
                elif "resource-name" in s:
                    resource_name = s.split('=')[1]
        except (ValueError, TypeError):
            raise CLIError('usage error: --permission-scope VARIABLE OPERATOR VALUE')
        namespace.permission_scope.append(PermissionScope(
            permissions=permissions,
            service=service,
            resource_name=resource_name
        ))


# pylint: disable=too-few-public-methods
class SshPublicKeyAddAction(argparse._AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        if not namespace.ssh_authorized_key:
            namespace.ssh_authorized_key = []
        SshPublicKey = namespace._cmd.get_models('SshPublicKey')
        try:
            description, key = '', ''
            for k in values:
                if "description" in k:
                    description = k.split('=')[1]
                elif "key" in k:
                    key = k.split('=')[1]
        except (ValueError, TypeError):
            raise CLIError('usage error: --ssh-authorized-key VARIABLE OPERATOR VALUE')
        namespace.ssh_authorized_key.append(SshPublicKey(description=description, key=key))


def get_permission_help_string(permission_class):
    allowed_values = get_permission_allowed_values(permission_class)
    return ' '.join(['({}){}'.format(x[0], x[1:]) for x in allowed_values])


def get_permission_allowed_values(permission_class):
    if permission_class:
        instance = permission_class()

        allowed_values = [x.lower() for x in dir(instance) if not x.startswith('_')]
        if 'from_string' in allowed_values:
            allowed_values.remove('from_string')
        for i, item in enumerate(allowed_values):
            if item == 'delete_previous_version':
                allowed_values[i] = 'x' + item
            if item == 'permanent_delete':
                allowed_values[i] = 'y' + item
            if item == 'set_immutability_policy':
                allowed_values[i] = 'i' + item
            if item == 'manage_access_control':
                allowed_values[i] = 'permissions'
            if item == 'manage_ownership':
                allowed_values[i] = 'ownership'
        return sorted(allowed_values)
    return None


def get_permission_validator(permission_class):
    allowed_values = get_permission_allowed_values(permission_class)
    allowed_string = ''.join(x[0] for x in allowed_values)

    def validator(namespace):
        if namespace.permission:
            if set(namespace.permission) - set(allowed_string):
                help_string = get_permission_help_string(permission_class)
                raise ValueError(
                    'valid values are {} or a combination thereof.'.format(help_string))
            if hasattr(permission_class, 'from_string'):
                namespace.permission = permission_class.from_string(namespace.permission)
            else:
                namespace.permission = permission_class(_str=namespace.permission)

    return validator


def get_source_file_or_blob_service_client_track2(cmd, namespace):
    """
    Create the second file service or blob service client for batch copy command, which is used to
    list the source files or blobs. If both the source account and source URI are omitted, it
    indicates that user want to copy files or blobs in the same storage account.
    """

    usage_string = 'invalid usage: supply only one of the following argument sets:' + \
                   '\n\t   --source-uri  [--source-sas]' + \
                   '\n\tOR --source-container' + \
                   '\n\tOR --source-container --source-account-name --source-account-key' + \
                   '\n\tOR --source-container --source-account-name --source-sas' + \
                   '\n\tOR --source-share' + \
                   '\n\tOR --source-share --source-account-name --source-account-key' + \
                   '\n\tOR --source-share --source-account-name --source-account-sas'

    ns = vars(namespace)
    source_account = ns.pop('source_account_name', None)
    source_key = ns.pop('source_account_key', None)
    source_uri = ns.pop('source_uri', None)
    source_sas = ns.get('source_sas', None)
    source_container = ns.get('source_container', None)
    source_share = ns.get('source_share', None)

    if source_uri and source_account:
        raise ValueError(usage_string)
    if not source_uri and bool(source_container) == bool(source_share):  # must be container or share
        raise ValueError(usage_string)

    if (not source_account) and (not source_uri):
        # Set the source_client to None if neither source_account nor source_uri is given. This
        # indicates the command that the source files share or blob container is in the same storage
        # account as the destination file share or blob container.
        #
        # The command itself should create the source service client since the validator can't
        # access the destination client through the namespace.
        #
        # A few arguments check will be made as well so as not to cause ambiguity.
        if source_key or source_sas:
            raise ValueError('invalid usage: --source-account-name is missing; the source account is assumed to be the'
                             ' same as the destination account. Do not provide --source-sas or --source-account-key')

        source_account, source_key, source_sas = ns['account_name'], ns['account_key'], ns['sas_token']

    if source_account:
        if not (source_key or source_sas):
            # when neither storage account key nor SAS is given, try to fetch the key in the current
            # subscription
            source_key = _query_account_key(cmd.cli_ctx, source_account)

    elif source_uri:
        if source_key or source_container or source_share:
            raise ValueError(usage_string)

        from .storage_url_helpers import StorageResourceIdentifier
        if source_sas:
            source_uri = '{}{}{}'.format(source_uri, '?', source_sas.lstrip('?'))
        identifier = StorageResourceIdentifier(cmd.cli_ctx.cloud, source_uri)
        nor_container_or_share = not identifier.container and not identifier.share
        if not identifier.is_url():
            raise ValueError('incorrect usage: --source-uri expects a URI')
        if identifier.blob or identifier.directory or identifier.filename or nor_container_or_share:
            raise ValueError('incorrect usage: --source-uri has to be blob container or file share')

        source_account = identifier.account_name
        source_container = identifier.container
        source_share = identifier.share

        if identifier.sas_token:
            source_sas = identifier.sas_token
        else:
            source_key = _query_account_key(cmd.cli_ctx, identifier.account_name)

    # config source account credential
    ns['source_account_name'] = source_account
    ns['source_account_key'] = source_key
    ns['source_container'] = source_container
    ns['source_share'] = source_share
    # get sas token for source
    if not source_sas:
        from .util import create_short_lived_container_sas_track2, create_short_lived_share_sas_track2
        if source_container:
            source_sas = create_short_lived_container_sas_track2(cmd, account_name=source_account,
                                                                 account_key=source_key,
                                                                 container=source_container)
        if source_share:
            source_sas = create_short_lived_share_sas_track2(cmd, account_name=source_account,
                                                             account_key=source_key,
                                                             share=source_share)
    ns['source_sas'] = source_sas
    client_kwargs = {'account_name': ns['source_account_name'],
                     'account_key': ns['source_account_key'],
                     'sas_token': ns['source_sas']}
    if source_container:
        ns['source_client'] = cf_blob_service(cmd.cli_ctx, client_kwargs)
    if source_share:
        ns['source_client'] = cf_share_service(cmd.cli_ctx, client_kwargs)


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


def process_file_download_batch_parameters(cmd, namespace):
    """Process the parameters for storage file batch download command"""
    # 1. quick check
    if not os.path.exists(namespace.destination) or not os.path.isdir(namespace.destination):
        raise ValueError('incorrect usage: destination must be an existing directory')

    # 2. try to extract account name and share name from source string
    process_file_batch_source_parameters(cmd, namespace)


def process_file_batch_source_parameters(cmd, namespace):
    from .storage_url_helpers import StorageResourceIdentifier
    identifier = StorageResourceIdentifier(cmd.cli_ctx.cloud, namespace.source)
    if identifier.is_url():
        if identifier.filename or identifier.directory:
            raise ValueError('incorrect usage: source should be either share URL or name')

        namespace.source = identifier.share

        if not namespace.account_name:
            namespace.account_name = identifier.account_name

    namespace.share_name = namespace.source


def validate_source_uri(cmd, namespace):  # pylint: disable=too-many-statements
    from .util import create_short_lived_blob_sas, create_short_lived_blob_sas_v2, \
        create_short_lived_file_sas, create_short_lived_file_sas_v2
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
    uri = ns.get('copy_source', None)
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
            dir_name, file_name = os.path.split(path) if path else (None, '')
            source_sas = create_short_lived_file_sas_v2(cmd, source_account_name, source_account_key, share,
                                                        dir_name, file_name)
        elif valid_blob_source and (ns.get('share_name', None) or not same_account):
            source_sas = create_short_lived_blob_sas_v2(cmd, source_account_name, source_account_key, container,
                                                        blob)

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

    namespace.copy_source = uri


def validate_share_close_handle(namespace):
    from azure.cli.core.azclierror import InvalidArgumentValueError
    if namespace.close_all and namespace.handle:
        raise InvalidArgumentValueError("usage error: Please only specify either --handle-id or --close-all, not both.")
    if not namespace.close_all and not namespace.handle:
        raise InvalidArgumentValueError("usage error: Please specify either --handle-id or --close-all.")
