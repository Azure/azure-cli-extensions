# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.commands.validators import validate_key_value_pairs
from azure.cli.core.profiles import get_sdk

from ._client_factory import get_storage_data_service_client
from .util import guess_content_type
from .oauth_token_util import TokenUpdater
from .profiles import CUSTOM_MGMT_STORAGE

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


def validate_client_parameters(cmd, namespace):
    """ Retrieves storage connection parameters from environment variables and parses out connection string into
    account name and key """
    n = namespace

    def get_config_value(section, key, default):
        return cmd.cli_ctx.config.get(section, key, default)

    if hasattr(n, 'auth_mode'):
        auth_mode = n.auth_mode or get_config_value('storage', 'auth_mode', None)
        del n.auth_mode
        if not n.account_name:
            n.account_name = get_config_value('storage', 'account', None)
        if auth_mode == 'login':
            n.token_credential = _create_token_credential(cmd.cli_ctx)

            # give warning if there are account key args being ignored
            account_key_args = [n.account_key and "--account-key", n.sas_token and "--sas-token",
                                n.connection_string and "--connection-string"]
            account_key_args = [arg for arg in account_key_args if arg]

            if account_key_args:
                from knack.log import get_logger

                logger = get_logger(__name__)
                logger.warning('In "login" auth mode, the following arguments are ignored: %s',
                               ' ,'.join(account_key_args))
            return

    if not n.connection_string:
        n.connection_string = get_config_value('storage', 'connection_string', None)

    # if connection string supplied or in environment variables, extract account key and name
    if n.connection_string:
        conn_dict = validate_key_value_pairs(n.connection_string)
        n.account_name = conn_dict.get('AccountName')
        n.account_key = conn_dict.get('AccountKey')
        if not n.account_name or not n.account_key:
            from knack.util import CLIError
            raise CLIError('Connection-string: %s, is malformed. Some shell environments require the '
                           'connection string to be surrounded by quotes.' % n.connection_string)

    # otherwise, simply try to retrieve the remaining variables from environment variables
    if not n.account_name:
        n.account_name = get_config_value('storage', 'account', None)
    if not n.account_key:
        n.account_key = get_config_value('storage', 'key', None)
    if not n.sas_token:
        n.sas_token = get_config_value('storage', 'sas_token', None)

    # strip the '?' from sas token. the portal and command line are returns sas token in different
    # forms
    if n.sas_token:
        n.sas_token = n.sas_token.lstrip('?')

    # if account name is specified but no key, attempt to query
    if n.account_name and not n.account_key and not n.sas_token:
        n.account_key = _query_account_key(cmd.cli_ctx, n.account_name)


def get_content_setting_validator(settings_class, update, guess_from_file=None):
    def _class_name(class_type):
        return class_type.__module__ + "." + class_type.__class__.__name__

    def validator(cmd, namespace):
        t_base_blob_service, t_file_service, t_blob_content_settings, t_file_content_settings = cmd.get_models(
            'blob.baseblobservice#BaseBlobService',
            'file#FileService',
            'blob.models#ContentSettings',
            'file.models#ContentSettings')

        # must run certain validators first for an update
        if update:
            validate_client_parameters(cmd, namespace)
        if update and _class_name(settings_class) == _class_name(t_file_content_settings):
            get_file_path_validator()(namespace)
        ns = vars(namespace)

        # retrieve the existing object properties for an update
        if update:
            account = ns.get('account_name')
            key = ns.get('account_key')
            cs = ns.get('connection_string')
            sas = ns.get('sas_token')
            if _class_name(settings_class) == _class_name(t_blob_content_settings):
                client = get_storage_data_service_client(cmd.cli_ctx,
                                                         t_base_blob_service,
                                                         account,
                                                         key,
                                                         cs,
                                                         sas)
                container = ns.get('container_name')
                blob = ns.get('blob_name')
                lease_id = ns.get('lease_id')
                props = client.get_blob_properties(container, blob, lease_id=lease_id).properties.content_settings
            elif _class_name(settings_class) == _class_name(t_file_content_settings):
                client = get_storage_data_service_client(cmd.cli_ctx, t_file_service, account, key, cs, sas)
                share = ns.get('share_name')
                directory = ns.get('directory_name')
                filename = ns.get('file_name')
                props = client.get_file_properties(share, directory, filename).properties.content_settings

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
            new_props.content_type = new_props.content_type or props.content_type
            new_props.content_disposition = new_props.content_disposition or props.content_disposition
            new_props.content_encoding = new_props.content_encoding or props.content_encoding
            new_props.content_language = new_props.content_language or props.content_language
            new_props.content_md5 = new_props.content_md5 or props.content_md5
            new_props.cache_control = new_props.cache_control or props.cache_control
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
        t_encryption_services, t_encryption_service = get_sdk(cmd.cli_ctx, CUSTOM_MGMT_STORAGE,
                                                              'EncryptionServices', 'EncryptionService', mod='models')
        services = {service: t_encryption_service(enabled=True) for service in namespace.encryption_services}

        namespace.encryption_services = t_encryption_services(**services)


def validate_encryption_source(cmd, namespace):
    ns = vars(namespace)

    key_name = ns.pop('encryption_key_name', None)
    key_version = ns.pop('encryption_key_version', None)
    key_vault_uri = ns.pop('encryption_key_vault', None)

    if namespace.encryption_key_source == 'Microsoft.Keyvault' and not (key_name and key_version and key_vault_uri):
        raise ValueError('--encryption-key-name, --encryption-key-vault, and --encryption-key-version are required '
                         'when --encryption-key-source=Microsoft.Keyvault is specified.')

    if key_name or key_version or key_vault_uri:
        if namespace.encryption_key_source != 'Microsoft.Keyvault':
            raise ValueError('--encryption-key-name, --encryption-key-vault, and --encryption-key-version are not '
                             'applicable when --encryption-key-source=Microsoft.Keyvault is not specified.')
        KeyVaultProperties = get_sdk(cmd.cli_ctx, CUSTOM_MGMT_STORAGE, 'KeyVaultProperties',
                                     mod='models')
        if not KeyVaultProperties:
            return

        kv_prop = KeyVaultProperties(key_name=key_name, key_version=key_version, key_vault_uri=key_vault_uri)
        namespace.encryption_key_vault_properties = kv_prop


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
        namespace.directory_name = dir_name
        namespace.file_name = file_name
        del namespace.path

    return validator


def validate_key(namespace):
    namespace.key_name = storage_account_key_options[namespace.key_name]


def validate_metadata(namespace):
    if namespace.metadata:
        namespace.metadata = dict(x.split('=', 1) for x in namespace.metadata)


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
        if not re.match("^{}-{}$".format(ip_format, ip_format), string):
            raise ValueError
    return string
