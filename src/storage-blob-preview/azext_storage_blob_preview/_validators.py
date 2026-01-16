# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=protected-access, unnecessary-comprehension

import os
import argparse

from azure.cli.core.commands.validators import validate_key_value_pairs
from azure.cli.core.profiles import ResourceType, get_sdk

from azure.cli.command_modules.storage._client_factory import storage_client_factory
from azure.cli.command_modules.storage.util import guess_content_type
from azure.cli.command_modules.storage.url_quote_util import encode_for_url

from knack.log import get_logger
from knack.util import CLIError
from .profiles import CUSTOM_DATA_STORAGE_BLOB
from ._client_factory import cf_blob_service

storage_account_key_options = {'primary': 'key1', 'secondary': 'key2'}
logger = get_logger(__name__)


# Utilities


# pylint: disable=inconsistent-return-statements,too-many-lines
def _query_account_key(cli_ctx, account_name):
    """Query the storage account key. This is used when the customer doesn't offer account key but name."""
    rg, scf = _query_account_rg(cli_ctx, account_name)
    t_storage_account_keys = get_sdk(
        cli_ctx, ResourceType.MGMT_STORAGE, 'models.storage_account_keys#StorageAccountKeys')

    logger.debug('Disable HTTP logging to avoid having storage keys in debug logs')
    if t_storage_account_keys:
        return scf.storage_accounts.list_keys(rg, account_name, logging_enable=False).key1
    # of type: models.storage_account_list_keys_result#StorageAccountListKeysResult
    return scf.storage_accounts.list_keys(rg, account_name, logging_enable=False).keys[0].value  # pylint: disable=no-member


def _query_account_rg(cli_ctx, account_name):
    """Query the storage account's resource group, which the mgmt sdk requires."""
    scf = storage_client_factory(cli_ctx)
    acc = next((x for x in scf.storage_accounts.list() if x.name == account_name), None)
    if acc:
        from azure.mgmt.core.tools import parse_resource_id
        return parse_resource_id(acc.id)['resource_group'], scf
    raise ValueError("Storage account '{}' not found.".format(account_name))


# region PARAMETER VALIDATORS
def get_config_value(cmd, section, key, default):
    return cmd.cli_ctx.config.get(section, key, default)


# pylint: disable=too-many-branches, too-many-statements
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


def validate_source_url(cmd, namespace):  # pylint: disable=too-many-statements, too-many-locals
    from .util import create_short_lived_blob_sas_v2, create_short_lived_file_sas_v2
    from azure.cli.core.azclierror import InvalidArgumentValueError, RequiredArgumentMissingError, \
        MutuallyExclusiveArgumentError
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
    token_credential = ns.get('token_credential')
    is_oauth = token_credential is not None

    # source in the form of an uri
    uri = ns.get('source_url', None)
    if uri:
        if any([container, blob, snapshot, share, path, file_snapshot, source_account_name,
                source_account_key]):
            raise InvalidArgumentValueError(usage_string.format(
                'Unused parameters are given in addition to the source URI'))
        if source_sas:
            source_sas = source_sas.lstrip('?')
            uri = '{}{}{}'.format(uri, '?', source_sas)
            namespace.copy_source = uri
        return

    # ensure either a file or blob source is specified
    valid_blob_source = container and blob and not share and not path and not file_snapshot
    valid_file_source = share and path and not container and not blob and not snapshot

    if not valid_blob_source and not valid_file_source:
        raise RequiredArgumentMissingError(usage_string.format('Neither a valid blob or file source is specified'))
    if valid_blob_source and valid_file_source:
        raise MutuallyExclusiveArgumentError(usage_string.format(
            'Ambiguous parameters, both blob and file sources are specified'))

    validate_client_parameters(cmd, namespace)  # must run first to resolve storage account

    if not source_account_name:
        if source_account_key:
            raise RequiredArgumentMissingError(usage_string.format(
                'Source account key is given but account name is not'))
        # assume that user intends to copy blob in the same account
        source_account_name = ns.get('account_name', None)

    # determine if the copy will happen in the same storage account
    same_account = False

    if not source_account_key and not source_sas and not is_oauth:
        if source_account_name == ns.get('account_name', None):
            same_account = True
            source_account_key = ns.get('account_key', None)
            source_sas = ns.get('sas_token', None)
        else:
            # the source account is different from destination account but the key is missing try to query one.
            try:
                source_account_key = _query_account_key(cmd.cli_ctx, source_account_name)
            except ValueError:
                raise RequiredArgumentMissingError('Source storage account {} not found.'.format(source_account_name))

    # if oauth, use user delegation key to generate sas
    source_user_delegation_key = None
    if is_oauth:
        client_kwargs = {'account_name': source_account_name,
                         'token_credential': token_credential}
        if valid_blob_source:
            client = cf_blob_service(cmd.cli_ctx, client_kwargs)

            from datetime import datetime, timedelta
            start = datetime.utcnow()
            expiry = datetime.utcnow() + timedelta(days=1)
            source_user_delegation_key = client.get_user_delegation_key(start, expiry)

    # Both source account name and either key or sas (or both) are now available
    if not source_sas:
        # generate a sas token even in the same account when the source and destination are not the same kind.
        if valid_file_source and (ns.get('container_name', None) or not same_account):
            dir_name, file_name = os.path.split(path) if path else (None, '')
            if dir_name == '':
                dir_name = None
            source_sas = create_short_lived_file_sas_v2(cmd, source_account_name, source_account_key, share,
                                                        dir_name, file_name)
        elif valid_blob_source and (ns.get('share_name', None) or not same_account):
            source_sas = create_short_lived_blob_sas_v2(cmd, source_account_name, container, blob,
                                                        account_key=source_account_key,
                                                        user_delegation_key=source_user_delegation_key)

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


def get_content_setting_validator(settings_class, update, guess_from_file=None, process_md5=False):
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
                account_kwargs = {'connection_string': cs,
                                  'account_name': account,
                                  'account_key': key,
                                  'token_credential': token_credential,
                                  'sas_token': sas}
                client = cf_blob_service(cmd.cli_ctx, account_kwargs).get_blob_client(container=container, blob=blob)
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

        # In track2 SDK, the content_md5 type should be bytearray. And then it will serialize to a string for request.
        # To keep consistent with track1 input and CLI will treat all parameter values as string. Here is to transform
        # content_md5 value to bytearray. And track2 SDK will serialize it into the right value with str type in header.
        if process_md5 and new_props.content_md5:
            from .track2_util import _str_to_bytearray
            new_props.content_md5 = _str_to_bytearray(new_props.content_md5)

        ns['content_settings'] = new_props

    return validator


def get_file_path_validator(default_file_param=None):
    """ Creates a namespace validator that splits out 'path' into 'directory_name' and 'file_name'.
    Allows another path-type parameter to be named which can supply a default filename. """

    def validator(namespace):
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


def page_blob_tier_validator(cmd, namespace):
    if not namespace.tier:
        return

    if namespace.blob_type != 'page' and namespace.tier:
        raise ValueError('Blob tier is only applicable to page blobs on premium storage accounts.')

    try:
        namespace.premium_page_blob_tier = getattr(cmd.get_models(
            '_generated.models._azure_blob_storage_enums#PremiumPageBlobAccessTier'), namespace.tier)
    except AttributeError:
        from azure.cli.command_modules.storage.sdkutil import get_blob_tier_names
        tier_names = get_blob_tier_names(
            cmd.cli_ctx, '_generated.models._azure_blob_storage_enums#PremiumPageBlobAccessTier')
        raise ValueError('Unknown premium page blob tier name. Choose among {}'.format(', '.join(tier_names)))


def block_blob_tier_validator(cmd, namespace):
    if not namespace.tier:
        return

    if namespace.blob_type != 'block' and namespace.tier:
        raise ValueError('Blob tier is only applicable to block blobs on standard storage accounts.')

    try:
        namespace.standard_blob_tier = getattr(cmd.get_models('_models#StandardBlobTier'), namespace.tier)
    except AttributeError:
        from azure.cli.command_modules.storage.sdkutil import get_blob_tier_names
        tier_names = get_blob_tier_names(cmd.cli_ctx, '_models#StandardBlobTier')
        raise ValueError('Unknown block blob tier name. Choose among {}'.format(', '.join(tier_names)))


def blob_tier_validator(cmd, namespace):
    if namespace.tier:
        if namespace.blob_type == 'page':
            page_blob_tier_validator(cmd, namespace)
        elif namespace.blob_type == 'block':
            block_blob_tier_validator(cmd, namespace)
        else:
            raise ValueError('Blob tier is only applicable to block or page blob.')
    del namespace.tier


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


def validate_blob_arguments(namespace):
    from azure.cli.core.azclierror import RequiredArgumentMissingError
    if not namespace.blob_url and not all([namespace.blob_name, namespace.container_name]):
        raise RequiredArgumentMissingError(
            "Please specify --blob-url or combination of blob name, container name and storage account arguments.")
