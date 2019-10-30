# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (tags_type, file_type, get_location_type, get_enum_type,
                                                get_three_state_flag)

from ._validators import (get_datetime_type, validate_metadata, validate_custom_domain, process_resource_group,
                          validate_bypass, validate_encryption_source, storage_account_key_options, validate_key,
                          validate_azcopy_upload_destination_url, validate_azcopy_download_source_url,
                          validate_azcopy_target_url)
from .profiles import CUSTOM_MGMT_STORAGE


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements
    from argcomplete.completers import FilesCompleter
    from knack.arguments import CLIArgumentType

    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    from .sdkutil import get_table_data_type
    from .completers import get_storage_name_completion_list, get_container_name_completions

    t_file_service = self.get_sdk('file#FileService')
    t_table_service = get_table_data_type(self.cli_ctx, 'table', 'TableService')

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'))
    container_name_type = CLIArgumentType(options_list=['--container-name', '-c'], help='The container name.',
                                          completer=get_container_name_completions)
    directory_type = CLIArgumentType(options_list=['--directory-name', '-d'], help='The directory name.',
                                     completer=get_storage_name_completion_list(t_file_service,
                                                                                'list_directories_and_files',
                                                                                parent='share_name'))
    share_name_type = CLIArgumentType(options_list=['--share-name', '-s'], help='The file share name.',
                                      completer=get_storage_name_completion_list(t_file_service, 'list_shares'))
    table_name_type = CLIArgumentType(options_list=['--table-name', '-t'],
                                      completer=get_storage_name_completion_list(t_table_service, 'list_tables'))

    with self.argument_context('storage') as c:
        c.argument('container_name', container_name_type)
        c.argument('directory_name', directory_type)
        c.argument('share_name', share_name_type)
        c.argument('table_name', table_name_type)
        c.argument('retry_wait', options_list=('--retry-interval',))
        c.ignore('progress_callback')
        c.argument('metadata', nargs='+',
                   help='Metadata in space-separated key=value pairs. This overwrites any existing metadata.',
                   validator=validate_metadata)
        c.argument('timeout', help='Request timeout in seconds. Applies to each call to the service.', type=int)

    with self.argument_context('storage', arg_group='Precondition') as c:
        c.argument('if_modified_since', help='Alter only if modified since supplied UTC datetime (Y-m-d\'T\'H:M\'Z\')',
                   type=get_datetime_type(False))
        c.argument('if_unmodified_since',
                   help='Alter only if unmodified since supplied UTC datetime (Y-m-d\'T\'H:M\'Z\')',
                   type=get_datetime_type(False))
        c.argument('if_match')
        c.argument('if_none_match')

    for item in ['delete', 'show', 'update', 'keys', 'network-rule', 'failover']:
        with self.argument_context('storage account {}'.format(item)) as c:
            c.argument('account_name', acct_name_type, options_list=['--name', '-n'])
            c.argument('resource_group_name', required=False, validator=process_resource_group)

    with self.argument_context('storage account check-name') as c:
        c.argument('name', options_list=['--name', '-n'])

    with self.argument_context('storage account create') as c:
        t_account_type, t_sku_name, t_kind = self.get_models('AccountType', 'SkuName', 'Kind',
                                                             resource_type=CUSTOM_MGMT_STORAGE)
        c.register_common_storage_account_options()
        c.argument('hierarchical_namespace', help='Allows the blob service to exhibit filesystem semantics.',
                   arg_type=get_three_state_flag())
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('account_type', help='The storage account type', arg_type=get_enum_type(t_account_type))
        c.argument('account_name', acct_name_type, options_list=['--name', '-n'], completer=None)
        c.argument('kind', help='Indicates the type of storage account.',
                   arg_type=get_enum_type(t_kind, default='storage'))
        c.argument('tags', tags_type)
        c.argument('custom_domain', help='User domain assigned to the storage account. Name is the CNAME source.')
        c.argument('sku', help='The storage account SKU.', arg_type=get_enum_type(t_sku_name, default='standard_ragrs'))

    with self.argument_context('storage account update') as c:
        c.register_common_storage_account_options()
        c.argument('custom_domain',
                   help='User domain assigned to the storage account. Name is the CNAME source. Use "" to clear '
                        'existing value.',
                   validator=validate_custom_domain)
        c.argument('use_subdomain', help='Specify whether to use indirect CNAME validation.',
                   arg_type=get_enum_type(['true', 'false']))
        c.argument('tags', tags_type, default=None)

    with self.argument_context('storage account update', arg_group='Customer managed key', min_api='2017-06-01') as c:
        c.extra('encryption_key_name', help='The name of the KeyVault key', )
        c.extra('encryption_key_vault', help='The Uri of the KeyVault')
        c.extra('encryption_key_version', help='The version of the KeyVault key')
        c.argument('encryption_key_source',
                   arg_type=get_enum_type(['Microsoft.Storage', 'Microsoft.Keyvault'], 'Microsoft.Storage'),
                   help='The default encryption service',
                   validator=validate_encryption_source)
        c.ignore('encryption_key_vault_properties')

    for scope in ['storage account create', 'storage account update']:
        with self.argument_context(scope, resource_type=CUSTOM_MGMT_STORAGE, min_api='2017-06-01',
                                   arg_group='Network Rule') as c:
            t_bypass, t_default_action = self.get_models('Bypass', 'DefaultAction',
                                                         resource_type=CUSTOM_MGMT_STORAGE)

            c.argument('bypass', nargs='+', validator=validate_bypass, arg_type=get_enum_type(t_bypass),
                       help='Bypass traffic for space-separated uses.')
            c.argument('default_action', arg_type=get_enum_type(t_default_action),
                       help='Default action to apply when no rule matches.')

    with self.argument_context('storage account show') as c:
        c.argument('expand', arg_type=get_enum_type(
            self.get_models('StorageAccountExpand', resource_type=CUSTOM_MGMT_STORAGE)))

    with self.argument_context('storage account keys renew') as c:
        c.argument('key_name', options_list=['--key'], help='The key to regenerate.', validator=validate_key,
                   arg_type=get_enum_type(list(storage_account_key_options.keys())))
        c.argument('account_name', acct_name_type, id_part=None)

    with self.argument_context('storage account keys list') as c:
        c.argument('account_name', acct_name_type, id_part=None)

    with self.argument_context('storage account network-rule') as c:
        from ._validators import validate_subnet
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('ip_address', help='IPv4 address or CIDR range.')
        c.argument('subnet', help='Name or ID of subnet. If name is supplied, `--vnet-name` must be supplied.')
        c.argument('vnet_name', help='Name of a virtual network.', validator=validate_subnet)
        c.argument('action', help='The action of virtual network rule.')

    with self.argument_context('storage account management-policy create') as c:
        c.argument('policy', type=file_type, completer=FilesCompleter(),
                   help='The Storage Account ManagementPolicies Rules, in JSON format. See more details in: '
                        'https://docs.microsoft.com/azure/storage/common/storage-lifecycle-managment-concepts.')
        c.argument('account_name', help='The name of the storage account within the specified resource group.')

    with self.argument_context('storage account management-policy update') as c:
        c.argument('account_name', help='The name of the storage account within the specified resource group.')

    with self.argument_context('storage blob service-properties update') as c:
        c.argument('delete_retention', arg_type=get_three_state_flag(), arg_group='Soft Delete',
                   help='Enables soft-delete.')
        c.argument('days_retained', type=int, arg_group='Soft Delete',
                   help='Number of days that soft-deleted blob will be retained. Must be in range [1,365].')
        c.argument('static_website', arg_group='Static Website', arg_type=get_three_state_flag(),
                   help='Enables static-website.')
        c.argument('index_document', help='Represents the name of the index document. This is commonly "index.html".',
                   arg_group='Static Website')
        c.argument('error_document_404_path', options_list=['--404-document'], arg_group='Static Website',
                   help='Represents the path to the error document that should be shown when an error 404 is issued,'
                        ' in other words, when a browser requests a page that does not exist.')

    with self.argument_context('storage azcopy blob upload') as c:
        c.extra('destination_container', options_list=['--container', '-c'], required=True,
                help='The upload destination container.')
        c.extra('destination_path', options_list=['--destination', '-d'],
                validator=validate_azcopy_upload_destination_url,
                help='The upload destination path.')
        c.argument('source', options_list=['--source', '-s'],
                   help='The source file path to upload from.')
        c.argument('recursive', options_list=['--recursive', '-r'], action='store_true',
                   help='Recursively upload blobs.')
        c.ignore('destination')

    with self.argument_context('storage azcopy blob download') as c:
        c.extra('source_container', options_list=['--container', '-c'], required=True,
                help='The download source container.')
        c.extra('source_path', options_list=['--source', '-s'],
                validator=validate_azcopy_download_source_url,
                help='The download source path.')
        c.argument('destination', options_list=['--destination', '-d'],
                   help='The destination file path to download to.')
        c.argument('recursive', options_list=['--recursive', '-r'], action='store_true',
                   help='Recursively download blobs.')
        c.ignore('source')

    with self.argument_context('storage azcopy blob delete') as c:
        c.extra('target_container', options_list=['--container', '-c'], required=True,
                help='The delete target container.')
        c.extra('target_path', options_list=['--target', '-t'],
                validator=validate_azcopy_target_url,
                help='The delete target path.')
        c.argument('recursive', options_list=['--recursive', '-r'], action='store_true',
                   help='Recursively delete blobs.')
        c.ignore('target')

    with self.argument_context('storage azcopy blob sync') as c:
        c.extra('destination_container', options_list=['--container', '-c'], required=True,
                help='The sync destination container.')
        c.extra('destination_path', options_list=['--destination', '-d'],
                validator=validate_azcopy_upload_destination_url,
                help='The sync destination path.')
        c.argument('source', options_list=['--source', '-s'],
                   help='The source file path to sync from.')
        c.ignore('destination')

    with self.argument_context('storage azcopy run-command') as c:
        c.positional('command_args', help='Command to run using azcopy. Please start commands with "azcopy ".')
