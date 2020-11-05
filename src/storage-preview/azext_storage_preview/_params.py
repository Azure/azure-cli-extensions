# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (tags_type, file_type, get_location_type, get_enum_type,
                                                get_three_state_flag)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction, ALL

from ._validators import (get_datetime_type, validate_metadata,
                          validate_azcopy_upload_destination_url, validate_azcopy_download_source_url,
                          validate_azcopy_target_url, validate_included_datasets,
                          validate_blob_directory_download_source_url, validate_blob_directory_upload_destination_url,
                          validate_storage_data_plane_list, process_resource_group)
from .profiles import CUSTOM_DATA_STORAGE, CUSTOM_DATA_STORAGE_ADLS, CUSTOM_MGMT_PREVIEW_STORAGE


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements
    from argcomplete.completers import FilesCompleter
    from knack.arguments import CLIArgumentType
    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    from .sdkutil import get_table_data_type
    from .completers import get_storage_name_completion_list, get_container_name_completions

    t_base_blob_service = self.get_sdk('blob.baseblobservice#BaseBlobService')
    t_file_service = self.get_sdk('file#FileService')
    t_table_service = get_table_data_type(self.cli_ctx, 'table', 'TableService')

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'),
                                     local_context_attribute=LocalContextAttribute(
                                         name='storage_account_name', actions=[LocalContextAction.GET]))
    blob_name_type = CLIArgumentType(options_list=['--blob-name', '-b'], help='The blob name.',
                                     completer=get_storage_name_completion_list(t_base_blob_service, 'list_blobs',
                                                                                parent='container_name'))
    container_name_type = CLIArgumentType(options_list=['--container-name', '-c'], help='The container name.',
                                          completer=get_container_name_completions)
    directory_path_type = CLIArgumentType(options_list=['--directory-path', '-d'], help='The directory path name.',
                                          parent='container_name')
    share_name_type = CLIArgumentType(options_list=['--share-name', '-s'], help='The file share name.',
                                      completer=get_storage_name_completion_list(t_file_service, 'list_shares'))
    table_name_type = CLIArgumentType(options_list=['--table-name', '-t'],
                                      completer=get_storage_name_completion_list(t_table_service, 'list_tables'))
    num_results_type = CLIArgumentType(
        default=5000, help='Specifies the maximum number of results to return. Provide "*" to return all.',
        validator=validate_storage_data_plane_list)
    acl_type = CLIArgumentType(options_list=['--acl-spec', '-a'],
                               help='The ACL specification to set on the path in the format '
                                    '"[default:]user|group|other|mask:[entity id or UPN]:r|-w|-x|-,'
                                    '[default:]user|group|other|mask:[entity id or UPN]:r|-w|-x|-,...". '
                                    'e.g."user::rwx,user:john.doe@contoso:rwx,group::r--,other::---,mask::rwx".')
    large_file_share_type = CLIArgumentType(
        action='store_true', min_api='2019-04-01',
        help='Enable the capability to support large file shares with more than 5 TiB capacity for storage account.'
             'Once the property is enabled, the feature cannot be disabled. Currently only supported for LRS and '
             'ZRS replication types, hence account conversions to geo-redundant accounts would not be possible. '
             'For more information, please refer to https://go.microsoft.com/fwlink/?linkid=2086047.')
    adds_type = CLIArgumentType(arg_type=get_three_state_flag(), min_api='2019-04-01',
                                help='Enable Azure Files Active Directory Domain Service Authentication for '
                                     'storage account. When --enable-files-adds is set to true, Azure Active '
                                     'Directory Properties arguments must be provided.')
    aadds_type = CLIArgumentType(arg_type=get_three_state_flag(), min_api='2018-11-01',
                                 help='Enable Azure Active Directory Domain Services authentication for Azure Files')
    domain_name_type = CLIArgumentType(min_api='2019-04-01', arg_group="Azure Active Directory Properties",
                                       help="Specify the primary domain that the AD DNS server is authoritative for. "
                                            "Required when --enable-files-adds is set to True")
    net_bios_domain_name_type = CLIArgumentType(min_api='2019-04-01', arg_group="Azure Active Directory Properties",
                                                help="Specify the NetBIOS domain name. "
                                                     "Required when --enable-files-adds is set to True")
    forest_name_type = CLIArgumentType(min_api='2019-04-01', arg_group="Azure Active Directory Properties",
                                       help="Specify the Active Directory forest to get. "
                                            "Required when --enable-files-adds is set to True")
    domain_guid_type = CLIArgumentType(min_api='2019-04-01', arg_group="Azure Active Directory Properties",
                                       help="Specify the domain GUID. Required when --enable-files-adds is set to True")
    domain_sid_type = CLIArgumentType(min_api='2019-04-01', arg_group="Azure Active Directory Properties",
                                      help="Specify the security identifier (SID). Required when --enable-files-adds "
                                           "is set to True")
    azure_storage_sid_type = CLIArgumentType(min_api='2019-04-01', arg_group="Azure Active Directory Properties",
                                             help="Specify the security identifier (SID) for Azure Storage. "
                                                  "Required when --enable-files-adds is set to True")
    t_routing_choice = self.get_models('RoutingChoice', resource_type=CUSTOM_MGMT_PREVIEW_STORAGE)
    routing_choice_type = CLIArgumentType(
        arg_group='Routing Preference', arg_type=get_enum_type(t_routing_choice),
        help='Routing Choice defines the kind of network routing opted by the user.',
        is_preview=True, min_api='2019-06-01')
    publish_microsoft_endpoints_type = CLIArgumentType(
        arg_group='Routing Preference', arg_type=get_three_state_flag(), is_preview=True, min_api='2019-06-01',
        help='A boolean flag which indicates whether microsoft routing storage endpoints are to be published.')
    publish_internet_endpoints_type = CLIArgumentType(
        arg_group='Routing Preference', arg_type=get_three_state_flag(), is_preview=True, min_api='2019-06-01',
        help='A boolean flag which indicates whether internet routing storage endpoints are to be published.')

    with self.argument_context('storage') as c:
        c.argument('container_name', container_name_type)
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

    with self.argument_context('storage account create', resource_type=CUSTOM_MGMT_PREVIEW_STORAGE) as c:
        t_account_type, t_sku_name, t_kind, t_tls_version, t_extended_location = \
            self.get_models('AccountType', 'SkuName', 'Kind', 'MinimumTlsVersion', 'ExtendedLocationTypes',
                            resource_type=CUSTOM_MGMT_PREVIEW_STORAGE)

        c.register_common_storage_account_options()
        c.argument('location', get_location_type(self.cli_ctx), validator=get_default_location_from_resource_group)
        c.argument('account_type', help='The storage account type', arg_type=get_enum_type(t_account_type))
        c.argument('account_name', acct_name_type, options_list=['--name', '-n'], completer=None,
                   local_context_attribute=LocalContextAttribute(
                       name='storage_account_name', actions=[LocalContextAction.SET], scopes=[ALL]))
        c.argument('kind', help='Indicates the type of storage account.', min_api="2018-02-01",
                   arg_type=get_enum_type(t_kind), default='StorageV2')
        c.argument('kind', help='Indicates the type of storage account.', max_api="2017-10-01",
                   arg_type=get_enum_type(t_kind), default='Storage')
        c.argument('https_only', arg_type=get_three_state_flag(), min_api='2019-04-01',
                   help='Allow https traffic only to storage service if set to true. The default value is true.')
        c.argument('https_only', arg_type=get_three_state_flag(), max_api='2018-11-01',
                   help='Allow https traffic only to storage service if set to true. The default value is false.')
        c.argument('tags', tags_type)
        c.argument('custom_domain', help='User domain assigned to the storage account. Name is the CNAME source.')
        c.argument('sku', help='The storage account SKU.', arg_type=get_enum_type(t_sku_name, default='standard_ragrs'))
        c.argument('enable_files_aadds', aadds_type)
        c.argument('enable_files_adds', adds_type)
        c.argument('enable_large_file_share', arg_type=large_file_share_type)
        c.argument('domain_name', domain_name_type)
        c.argument('net_bios_domain_name', net_bios_domain_name_type)
        c.argument('forest_name', forest_name_type)
        c.argument('domain_guid', domain_guid_type)
        c.argument('domain_sid', domain_sid_type)
        c.argument('azure_storage_sid', azure_storage_sid_type)
        c.argument('enable_hierarchical_namespace', arg_type=get_three_state_flag(),
                   options_list=['--enable-hierarchical-namespace', '--hns',
                                 c.deprecate(target='--hierarchical-namespace', redirect='--hns', hide=True)],
                   help=" Allow the blob service to exhibit filesystem semantics. This property can be enabled only "
                   "when storage account kind is StorageV2.",
                   min_api='2018-02-01')
        c.argument('encryption_key_type_for_table', arg_type=get_enum_type(['Account', 'Service']),
                   help='Set the encryption key type for Table service. "Account": Table will be encrypted '
                        'with account-scoped encryption key. "Service": Table will always be encrypted with '
                        'service-scoped keys. Currently the default encryption key type is "Service".',
                   min_api='2019-06-01', options_list=['--encryption-key-type-for-table', '-t'])
        c.argument('encryption_key_type_for_queue', arg_type=get_enum_type(['Account', 'Service']),
                   help='Set the encryption key type for Queue service. "Account": Queue will be encrypted '
                        'with account-scoped encryption key. "Service": Queue will always be encrypted with '
                        'service-scoped keys. Currently the default encryption key type is "Service".',
                   min_api='2019-06-01', options_list=['--encryption-key-type-for-queue', '-q'])
        c.argument('routing_choice', routing_choice_type)
        c.argument('publish_microsoft_endpoints', publish_microsoft_endpoints_type)
        c.argument('publish_internet_endpoints', publish_internet_endpoints_type)
        c.argument('require_infrastructure_encryption', options_list=['--require-infrastructure-encryption', '-i'],
                   arg_type=get_three_state_flag(),
                   help='A boolean indicating whether or not the service applies a secondary layer of encryption with '
                   'platform managed keys for data at rest.')
        c.argument('allow_blob_public_access', arg_type=get_three_state_flag(), min_api='2019-04-01',
                   help='Allow or disallow public access to all blobs or containers in the storage account. '
                   'The default value for this property is null, which is equivalent to true. When true, containers '
                   'in the account may be configured for public access. Note that setting this property to true does '
                   'not enable anonymous access to any data in the account. The additional step of configuring the '
                   'public access setting for a container is required to enable anonymous access.')
        c.argument('min_tls_version', arg_type=get_enum_type(t_tls_version),
                   help='The minimum TLS version to be permitted on requests to storage. '
                        'The default interpretation is TLS 1.0 for this property')
        c.argument('extended_location_name', options_list=['--extended-location-name', '--ext-name'],
                   arg_group='Extended Location', is_preview=True,
                   help='The name of the extended location.')
        c.argument('extended_location_type', options_list=['--extended-location-type', '--ext-type'],
                   arg_group='Extended Location', is_preview=True,
                   arg_type=get_enum_type(t_extended_location, default=t_extended_location.EDGE_ZONE),
                   help='The type of the extended location.')

    with self.argument_context('storage account blob-inventory-policy') as c:
        t_blob_inventory_name = self.get_models('BlobInventoryPolicyName', resource_type=CUSTOM_MGMT_PREVIEW_STORAGE)
        c.argument('blob_inventory_policy_name', options_list=['--name', '-n'],
                   arg_type=get_enum_type(t_blob_inventory_name), default='default', required=False,
                   help="The name of the storage account blob inventory policy. It should always be 'default'.")
        c.argument('resource_group_name', required=False, validator=process_resource_group)
        c.argument('account_name',
                   help='The name of the storage account within the specified resource group. Storage account names '
                        'must be between 3 and 24 characters in length and use numbers and lower-case letters only.')

    with self.argument_context('storage account blob-inventory-policy create') as c:
        t_inventory_rule_type = self.get_models('InventoryRuleType', resource_type=CUSTOM_MGMT_PREVIEW_STORAGE)
        c.argument('policy', type=file_type, completer=FilesCompleter(),
                   help='The Storage Account Blob Inventory Policy, string in JSON format or json file path. '
                        'See more details in: {https://review.docs.microsoft.com/en-us/azure/storage/blobs/blob-inventory?branch=pr-en-us-135665}.')
        c.argument('destination',
                   help='Container name where blob inventory files are stored. Must be pre-created.')
        c.argument('enabled', arg_type=get_three_state_flag(), help='Policy is enabled if set to true.')
        c.argument('type', arg_type=get_enum_type(t_inventory_rule_type), default='Inventory', required=False,
                   help='The valid value is Inventory. Possible values include: "Inventory".')
        c.argument('rule_name', arg_group='Blob Inventory Policy Rule',
                   help='A rule name can contain any combination of alpha numeric characters. Rule name is '
                   'case-sensitive. It must be unique within a policy.')
        c.argument('prefix_match', arg_group='Blob Inventory Policy Rule', nargs='+',
                   help='An array of strings for blob prefixes to be matched.')
        c.argument('blob_types',  arg_group='Blob Inventory Policy Rule', nargs='+',
                   help='An array of predefined enum values. Valid values include blockBlob, appendBlob, pageBlob. '
                        'Hns accounts does not support pageBlobs.')
        c.argument('include_blob_versions', arg_group='Blob Inventory Policy Rule', arg_type=get_three_state_flag(),
                   help='Include blob versions in blob inventory when value set to true.')
        c.argument('include_snapshots', arg_group='Blob Inventory Policy Rule', arg_type=get_three_state_flag(),
                   help='Include blob snapshots in blob inventory when value set to true.')

    # with self.argument_context('storage account blob-inventory-policy rule') as c:
    #     c.argument('destination', help='')
    #     c.argument('enabled', help='')
    #     c.argument('type', help='')

    with self.argument_context('storage account network-rule') as c:
        from ._validators import validate_subnet
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('ip_address', help='IPv4 address or CIDR range.')
        c.argument('subnet', help='Name or ID of subnet. If name is supplied, `--vnet-name` must be supplied.')
        c.argument('vnet_name', help='Name of a virtual network.', validator=validate_subnet)
        c.argument('action', help='The action of virtual network rule.')
        c.argument('resource_id', help='The resource id to add in network rule.')
        c.argument('tenant_id', help='The tenant id to add in network rule.')

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

    with self.argument_context('storage blob access') as c:
        c.argument('path', blob_name_type)

    with self.argument_context('storage blob access set') as c:
        c.argument('acl', acl_type, required=True,)
        c.ignore('owner', 'group', 'permissions')

    with self.argument_context('storage blob access update') as c:
        c.argument('acl', acl_type)
        c.argument('owner', help='The owning user for the directory.')
        c.argument('group', help='The owning group for the directory.')
        c.argument('permissions', help='The POSIX access permissions for the file owner,'
                   'the file owning group, and others. Both symbolic (rwxrw-rw-) and 4-digit '
                   'octal notation (e.g. 0766) are supported.')

    with self.argument_context('storage blob list') as c:
        c.argument('include', validator=validate_included_datasets, default='mc')
        c.argument('num_results', arg_type=num_results_type)

    with self.argument_context('storage blob move') as c:
        from ._validators import validate_move_file
        c.argument('source_path', options_list=['--source-blob', '-s'], validator=validate_move_file,
                   help="The source blob name. It should be an absolute path under the container. e.g."
                        "'topdir1/dirsubfoo'.")
        c.argument('new_path', options_list=['--destination-blob', '-d'],
                   help="The destination blob name. It should be an absolute path under the container. e.g."
                        "'topdir1/dirbar'.")
        c.argument('container_name', container_name_type)
        c.ignore('mode')
        c.ignore('marker')

    with self.argument_context('storage blob directory') as c:
        c.argument('directory_path', directory_path_type)
        c.argument('container_name', container_name_type)

    with self.argument_context('storage blob directory access') as c:
        c.argument('path', directory_path_type)

    with self.argument_context('storage blob directory access set') as c:
        c.argument('acl', acl_type, required=True)
        c.ignore('owner', 'group', 'permissions')

    with self.argument_context('storage blob directory access update') as c:
        c.argument('acl', acl_type)
        c.argument('owner', help='The owning user for the directory.')
        c.argument('group', help='The owning group for the directory.')
        c.argument('permissions', help='The POSIX access permissions for the file owner,'
                   'the file owning group, and others. Both symbolic (rwxrw-rw-) and 4-digit '
                   'octal notation (e.g. 0766) are supported.')

    with self.argument_context('storage blob directory create') as c:
        from ._validators import validate_directory_name
        c.argument('posix_permissions', options_list=['--permissions'])
        c.argument('posix_umask', options_list=['--umask'], default='0027',
                   help='Optional and only valid if Hierarchical Namespace is enabled for the account. '
                        'The umask restricts permission settings for file and directory, and will only be applied when '
                        'default Acl does not exist in parent directory. If the umask bit has set, it means that the '
                        'corresponding permission will be disabled. In this way, the resulting permission is given by '
                        'p & ^u, where p is the permission and u is the umask. Only 4-digit octal notation (e.g. 0022) '
                        'is supported here.')
        c.argument('directory_path', directory_path_type, validator=validate_directory_name)

    with self.argument_context('storage blob directory download') as c:
        c.extra('source_container', options_list=['--container', '-c'], required=True,
                help='The download source container.')
        c.extra('source_path', options_list=['--source-path', '-s'], required=True,
                validator=validate_blob_directory_download_source_url,
                help='The download source directory path. It should be an absolute path to container.')
        c.argument('destination', options_list=['--destination-path', '-d'],
                   help='The destination local directory path to download.')
        c.argument('recursive', options_list=['--recursive', '-r'], action='store_true',
                   help='Recursively download blobs. If enabled, all the blobs including the blobs in subdirectories '
                        'will be downloaded.')
        c.ignore('source')

    with self.argument_context('storage blob directory exists') as c:
        c.argument('blob_name', directory_path_type, required=True)

    with self.argument_context('storage blob directory list') as c:
        c.argument('include', validator=validate_included_datasets, default='mc')
        c.argument('num_results', arg_type=num_results_type)

    with self.argument_context('storage blob directory metadata') as c:
        c.argument('blob_name', directory_path_type)

    with self.argument_context('storage blob directory move') as c:
        from ._validators import validate_move_directory
        c.argument('new_path', options_list=['--destination-path', '-d'],
                   help='The destination blob directory path. It can be a directory or subdirectory name, e.g. dir, '
                        'dir/subdir. If the destination path exists and is empty, the source will be moved into the '
                        'destination path. If the destination path does not exist, the destination path will be created'
                        ' and overwritten by the source. To control the move operation for nonempty path, you can use '
                        '--move-mode to determine its behavior.')
        c.argument('source_path', options_list=['--source-path', '-s'],
                   help='The source blob directory path.', validator=validate_move_directory)
        c.argument('lease_id', options_list=['--lease-id'],
                   help='A lease ID for destination directory_path. The destination directory_path must have an active '
                        'lease and the lease ID must match.')
        c.argument('mode', options_list=['--move-mode'], arg_type=get_enum_type(["legacy", "posix"]), default="posix",
                   help="Valid only when namespace is enabled. This parameter determines the behavior "
                        "of the move operation. If the destination directory is empty, for both two mode, "
                        "the destination directory will be overwritten. But if the destination directory is not empty, "
                        "in legacy mode the move operation will fail and in posix mode, the source directory will be "
                        "moved into the destination directory. ")

    with self.argument_context('storage blob directory show') as c:
        c.argument('directory_name', directory_path_type)
        c.argument('container_name', container_name_type)
        # c.argument('snapshot', help='The snapshot parameter is an opaque DateTime value that, '
        #                            'when present, specifies the directory snapshot to retrieve.')
        c.ignore('snapshot')
        c.argument('lease_id', help='Required if the blob has an active lease.')
        c.argument('if_match', help="An ETag value, or the wildcard character (*). Specify this header to perform the"
                   "operation only if the resource's ETag matches the value specified")
        c.argument('if_none_match', help="An ETag value, or the wildcard character (*). Specify this header to perform"
                   "the operation only if the resource's ETag does not match the value specified. Specify the wildcard"
                   "character (*) to perform the operation only if the resource does not exist, and fail the operation"
                   "if it does exist.")

    with self.argument_context('storage blob directory upload') as c:
        c.extra('destination_container', options_list=['--container', '-c'], required=True,
                help='The upload destination container.')
        c.extra('destination_path', options_list=['--destination-path', '-d'], required=True,
                validator=validate_blob_directory_upload_destination_url,
                help='The upload destination directory path. It should be an absolute path to container. If the '
                     'specified destination path does not exist, a new directory path will be created.')
        c.argument('source', options_list=['--source', '-s'],
                   help='The source file path to upload from.')
        c.argument('recursive', options_list=['--recursive', '-r'], action='store_true',
                   help='Recursively upload blobs. If enabled, all the blobs including the blobs in subdirectories will'
                        ' be uploaded.')
        c.ignore('destination')
