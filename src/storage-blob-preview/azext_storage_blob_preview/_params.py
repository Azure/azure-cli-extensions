# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands.validators import get_default_location_from_resource_group, validate_tags
from azure.cli.core.commands.parameters import (file_type, get_location_type, get_enum_type,
                                                get_three_state_flag)
from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction, ALL

from ._validators import (get_datetime_type, validate_metadata, get_permission_validator, get_permission_help_string,
                          resource_type_type, services_type, validate_entity, validate_select, validate_blob_type,
                          validate_included_datasets_v2, validate_custom_domain, validate_container_public_access,
                          validate_table_payload_format, add_progress_callback, process_resource_group,
                          storage_account_key_options, process_file_download_namespace, process_metric_update_namespace,
                          get_char_options_validator, validate_bypass, validate_encryption_source, validate_marker,
                          validate_storage_data_plane_list, validate_azcopy_upload_destination_url,
                          validate_azcopy_remove_arguments, as_user_validator, parse_storage_account,
                          validator_delete_retention_days, validate_delete_retention_days,
                          validate_fs_public_access, validate_logging_version)
from .profiles import CUSTOM_DATA_STORAGE_BLOB


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements, too-many-lines
    from argcomplete.completers import FilesCompleter
    from six import u as unicode_string

    from knack.arguments import ignore_type, CLIArgumentType

    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    from .sdkutil import get_table_data_type
    from .completers import get_storage_name_completion_list

    t_base_blob_service = self.get_sdk('blob.baseblobservice#BaseBlobService')
    t_file_service = self.get_sdk('file#FileService')
    t_queue_service = self.get_sdk('queue#QueueService')
    t_table_service = get_table_data_type(self.cli_ctx, 'table', 'TableService')

    storage_account_type = CLIArgumentType(options_list='--storage-account',
                                           help='The name or ID of the storage account.',
                                           validator=parse_storage_account, id_part='name')

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'),
                                     local_context_attribute=LocalContextAttribute(
                                         name='storage_account_name', actions=[LocalContextAction.GET]))
    blob_name_type = CLIArgumentType(options_list=['--blob-name', '-b'], help='The blob name.',
                                     completer=get_storage_name_completion_list(t_base_blob_service, 'list_blobs',
                                                                                parent='container_name'))

    container_name_type = CLIArgumentType(options_list=['--container-name', '-c'], help='The container name.',
                                          completer=get_storage_name_completion_list(t_base_blob_service,
                                                                                     'list_containers'))
    directory_type = CLIArgumentType(options_list=['--directory-name', '-d'], help='The directory name.',
                                     completer=get_storage_name_completion_list(t_file_service,
                                                                                'list_directories_and_files',
                                                                                parent='share_name'))
    file_name_type = CLIArgumentType(options_list=['--file-name', '-f'],
                                     completer=get_storage_name_completion_list(t_file_service,
                                                                                'list_directories_and_files',
                                                                                parent='share_name'))
    share_name_type = CLIArgumentType(options_list=['--share-name', '-s'], help='The file share name.',
                                      completer=get_storage_name_completion_list(t_file_service, 'list_shares'))
    table_name_type = CLIArgumentType(options_list=['--table-name', '-t'],
                                      completer=get_storage_name_completion_list(t_table_service, 'list_tables'))
    queue_name_type = CLIArgumentType(options_list=['--queue-name', '-q'], help='The queue name.',
                                      completer=get_storage_name_completion_list(t_queue_service, 'list_queues'))
    progress_type = CLIArgumentType(help='Include this flag to disable progress reporting for the command.',
                                    action='store_true', validator=add_progress_callback)
    socket_timeout_type = CLIArgumentType(help='The socket timeout(secs), used by the service to regulate data flow.',
                                          type=int)
    num_results_type = CLIArgumentType(
        default=5000, help='Specifies the maximum number of results to return. Provide "*" to return all.',
        validator=validate_storage_data_plane_list)

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
    exclude_pattern_type = CLIArgumentType(arg_group='Additional Flags', help='Exclude these files where the name '
                                           'matches the pattern list. For example: *.jpg;*.pdf;exactName. This '
                                           'option supports wildcard characters (*)')
    include_pattern_type = CLIArgumentType(arg_group='Additional Flags', help='Include only these files where the name '
                                           'matches the pattern list. For example: *.jpg;*.pdf;exactName. This '
                                           'option supports wildcard characters (*)')
    exclude_path_type = CLIArgumentType(arg_group='Additional Flags', help='Exclude these paths. This option does not '
                                        'support wildcard characters (*). Checks relative path prefix. For example: '
                                        'myFolder;myFolder/subDirName/file.pdf.')
    include_path_type = CLIArgumentType(arg_group='Additional Flags', help='Include only these paths. This option does '
                                        'not support wildcard characters (*). Checks relative path prefix. For example:'
                                        'myFolder;myFolder/subDirName/file.pdf')
    recursive_type = CLIArgumentType(options_list=['--recursive', '-r'], action='store_true',
                                     help='Look into sub-directories recursively.')
    sas_help = 'The permissions the SAS grants. Allowed values: {}. Do not use if a stored access policy is ' \
               'referenced with --id that specifies this value. Can be combined.'
    t_routing_choice = self.get_models('RoutingChoice', resource_type=ResourceType.MGMT_STORAGE)
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

    umask_type = CLIArgumentType(
        help='When creating a file or directory and the parent folder does not have a default ACL, the umask restricts '
             'the permissions of the file or directory to be created. The resulting permission is given by p & ^u, '
             'where p is the permission and u is the umask. For more information, please refer to '
             'https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control#umask.')
    permissions_type = CLIArgumentType(
        help='POSIX access permissions for the file owner, the file owning group, and others. Each class may be '
             'granted read, write, or execute permission. The sticky bit is also supported. Both symbolic (rwxrw-rw-) '
             'and 4-digit octal notation (e.g. 0766) are supported. For more information, please refer to https://'
             'docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-access-control#levels-of-permission.')

    lease_type = CLIArgumentType(
        options_list='--lease-id', help='Required if the blob has an active lease.'
    )

    snapshot_type = CLIArgumentType(
        help='The snapshot parameter is an opaque DateTime value that, when present, specifies the blob snapshot '
        'to retrieve.'
    )

    tags_type = CLIArgumentType(
        nargs='*', validator=validate_tags, min_api='2019-12-12',
        help='space-separated tags: key[=value] [key[=value] ...]. Tags are case-sensitive. The tag set may '
        'contain at most 10 tags.  Tag keys must be between 1 and 128 characters, and tag values must be '
        'between 0 and 256 characters. Valid tag key and value characters include: lowercase and uppercase '
        'letters, digits (0-9), space (` `), plus (+), minus (-), period (.), solidus (/), colon (:), equals '
        '(=), underscore (_).'
    )

    marker_type = CLIArgumentType(
        help='A string value that identifies the portion of the list of containers to be '
             'returned with the next listing operation. The operation returns the NextMarker value within '
             'the response body if the listing operation did not return all containers remaining to be listed '
             'with the current page. If specified, this generator will begin returning results from the point '
             'where the previous generator stopped.')

    num_results_type = CLIArgumentType(
        default=5000, validator=validate_storage_data_plane_list,
        help='Specify the maximum number to return. If the request does not specify '
        'num_results, or specifies a value greater than 5000, the server will return up to 5000 items. Note that '
        'if the listing operation crosses a partition boundary, then the service will return a continuation token '
        'for retrieving the remaining of the results. Provide "*" to return all.'
    )

    version_id_type = CLIArgumentType(
        help='The version id parameter is an opaque DateTime value that, when present, specifies the version of '
        'the blob to delete.', min_api='2019-12-12'
    )
    with self.argument_context('storage') as c:
        c.argument('container_name', container_name_type)

    with self.argument_context('storage blob') as c:
        c.argument('blob_name', options_list=('--name', '-n'), arg_type=blob_name_type)

    with self.argument_context('storage blob copy start') as c:
        from ._validators import validate_source_url
        t_rehydrate_priority = self.get_sdk('_generated.models._azure_blob_storage_enums#RehydratePriority',
                                            resource_type=CUSTOM_DATA_STORAGE_BLOB)
        c.register_blob_arguments()
        c.register_precondition_options(prefix='source_')
        c.register_precondition_options(prefix='destination_')
        c.register_source_uri_arguments(validator=validate_source_url)

        c.ignore('incremental_copy')
        c.argument('blob_name', options_list=['--destination-blob', '-b'], required=True,
                   help='Name of the destination blob. If the exists, it will be overwritten.')
        c.argument('container_name', options_list=['--destination-container', '-c'], required=True,
                   help='The container name.')
        c.extra('timeout', help='Request timeout in seconds. Applies to each call to the service.', type=int)
        c.extra('destination_lease', options_list='--destination-lease-id',
                help='The lease ID specified for this header must match the lease ID of the estination blob. '
                'If the request does not include the lease ID or it is not valid, the operation fails with status '
                'code 412 (Precondition Failed).')
        c.extra('source_lease', options_list='--source-lease-id', arg_group='Copy Source',
                help='Specify this to perform the Copy Blob operation only if the lease ID given matches the '
                'active lease ID of the source blob.')
        c.extra('rehydrate_priority', arg_type=get_enum_type(t_rehydrate_priority),
                help=' Indicate the priority with which to rehydrate an archived blob.')
        c.extra('requires_sync', arg_type=get_three_state_flag(),
                help='Enforce that the service will not return a response until the copy is complete.')
        c.extra('tags', arg_type=tags_type)

    with self.argument_context('storage blob delete') as c:
        c.register_blob_arguments()
        c.register_precondition_options()

        c.extra('lease', lease_type)
        c.extra('snapshot', snapshot_type)
        c.extra('version_id', version_id_type)

    with self.argument_context('storage blob download') as c:
        from ._validators import add_progress_callback_v2
        c.register_blob_arguments()
        c.register_precondition_options()
        c.argument('file_path',  options_list=('--file', '-f'), type=file_type, completer=FilesCompleter(),
                   help='Path of file to write out to.')
        c.extra('start_range', type=int,
                help='Start of byte range to use for downloading a section of the blob. If no end_range is given, '
                'all bytes after the start_range will be downloaded. The start_range and end_range params are '
                'inclusive. Ex: start_range=0, end_range=511 will download first 512 bytes of blob.')
        c.extra('end_range', type=int,
                help='End of byte range to use for downloading a section of the blob. If end_range is given, '
                'start_range must be provided. The start_range and end_range params are inclusive. Ex: start_range=0, '
                'end_range=511 will download first 512 bytes of blob.')
        c.extra('no_progress', progress_type, validator=add_progress_callback_v2)
        c.extra('snapshot', snapshot_type)
        c.extra('lease', lease_type)
        c.extra('version_id', version_id_type)
        c.extra('max_concurrency', options_list='--max-connections', type=int, default=2,
                help='The number of parallel connections with which to download.')
        c.argument('open_mode', help='Mode to use when opening the file. Note that specifying append only open_mode '
                   'prevents parallel download. So, max_connections must be set to 1 if this open_mode is used.')
        c.argument('socket_timeout', deprecate_info=c.deprecate(hide=True),
                   help='The socket timeout(secs), used by the service to regulate data flow.')
        c.extra('validate_content', action='store_true', min_api='2016-05-31',
                help='If true, calculates an MD5 hash for each chunk of the blob. The storage service checks the '
                'hash of the content that has arrived with the hash that was sent. This is primarily valuable for '
                'detecting bitflips on the wire if using http instead of https, as https (the default), will already '
                'validate. Note that this MD5 hash is not stored with the blob. Also note that if enabled, the '
                'memory-efficient algorithm will not be used because computing the MD5 hash requires buffering '
                'entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.')

    with self.argument_context('storage blob generate-sas') as c:
        from .completers import get_storage_acl_name_completion_list

        t_blob_permissions = self.get_sdk('_models#BlobSasPermissions', resource_type=CUSTOM_DATA_STORAGE_BLOB)
        c.register_sas_arguments()
        c.argument('cache_control', help='Response header value for Cache-Control when resource is accessed'
                                         'using this shared access signature.')
        c.argument('content_disposition', help='Response header value for Content-Disposition when resource is accessed'
                                               'using this shared access signature.')
        c.argument('content_encoding', help='Response header value for Content-Encoding when resource is accessed'
                                            'using this shared access signature.')
        c.argument('content_language', help='Response header value for Content-Language when resource is accessed'
                                            'using this shared access signature.')
        c.argument('content_type', help='Response header value for Content-Type when resource is accessed'
                                        'using this shared access signature.')
        c.argument('full_uri', action='store_true',
                   help='Indicates that this command return the full blob URI and the shared access signature token.')
        c.argument('as_user', min_api='2018-11-09', action='store_true',
                   validator=as_user_validator,
                   help="Indicates that this command return the SAS signed with the user delegation key. "
                        "The expiry parameter and '--auth-mode login' are required if this argument is specified. ")
        c.argument('id', options_list='--policy-name',
                   help='The name of a stored access policy within the container\'s ACL.',
                   completer=get_storage_acl_name_completion_list(t_base_blob_service, 'container_name',
                                                                  'get_container_acl'))
        c.argument('permission', options_list='--permissions',
                   help=sas_help.format(get_permission_help_string(t_blob_permissions)),
                   validator=get_permission_validator(t_blob_permissions))
        c.ignore('sas_token')

    with self.argument_context('storage blob list') as c:
        from .track2_util import get_include_help_string
        t_blob_include = self.get_sdk('_generated.models._azure_blob_storage_enums#ListBlobsIncludeItem',
                                      resource_type=CUSTOM_DATA_STORAGE_BLOB)
        c.register_container_arguments()
        c.argument('delimiter',
                   help='When the request includes this parameter, the operation returns a BlobPrefix element in the '
                   'result list that acts as a placeholder for all blobs whose names begin with the same substring '
                   'up to the appearance of the delimiter character. The delimiter may be a single character or a '
                   'string.')
        c.argument('include', help="Specify one or more additional datasets to include in the response. "
                   "Options include: {}. Can be combined.".format(get_include_help_string(t_blob_include)),
                   validator=validate_included_datasets_v2)
        c.argument('marker', arg_type=marker_type)
        c.argument('num_results', arg_type=num_results_type)
        c.argument('prefix',
                   help='Filters the results to return only blobs whose name begins with the specified prefix.')
        c.argument('show_next_marker', action='store_true',
                   help='Show nextMarker in result when specified.')

    with self.argument_context('storage blob show') as c:
        c.register_blob_arguments()
        c.register_precondition_options()
        c.extra('snapshot', snapshot_type)
        c.extra('lease', lease_type)
        c.extra('version_id', version_id_type)

    with self.argument_context('storage blob upload') as c:
        from ._validators import page_blob_tier_validator, blob_tier_validator, validate_encryption_scope_client_params, \
            add_progress_callback_v2
        from .sdkutil import get_blob_types, get_blob_tier_names

        t_blob_content_settings = self.get_sdk('_models#ContentSettings', resource_type=CUSTOM_DATA_STORAGE_BLOB)
        t_premium_blob_tier = self.get_sdk('_models#PremiumPageBlobTier', resource_type=CUSTOM_DATA_STORAGE_BLOB)
        t_standard_blob_tier = self.get_sdk('_models#StandardBlobTier', resource_type=CUSTOM_DATA_STORAGE_BLOB)

        c.register_blob_arguments()
        c.register_precondition_options()
        c.register_content_settings_argument(t_blob_content_settings, update=False)

        c.argument('file_path', options_list=('--file', '-f'), type=file_type, completer=FilesCompleter(),
                   help='Path of the file to upload as the blob content.')
        c.argument('max_connections', type=int,
                   help='Maximum number of parallel connections to use when the blob size exceeds 64MB.')
        c.argument('maxsize_condition', type=int,
                   help='The max length in bytes permitted for the append blob.')
        c.argument('blob_type', options_list=('--type', '-t'), validator=validate_blob_type,
                   arg_type=get_enum_type(get_blob_types()))
        c.argument('validate_content', action='store_true', min_api='2016-05-31')
        c.extra('no_progress', progress_type, validator=add_progress_callback_v2)
        c.argument('socket_timeout', deprecate_info=c.deprecate(hide=True),
                   help='The socket timeout(secs), used by the service to regulate data flow.')
        c.extra('premium_page_blob_tier', options_list=['--premium-page-tier', '--tier'],
                arg_type=get_enum_type(t_premium_blob_tier), min_api='2017-04-17', validator=page_blob_tier_validator,
                help='A page blob tier value to set the blob to. The tier correlates to the size of the blob and '
                'number of allowed IOPS. This is only applicable to page blobs on premium storage accounts.')
        c.extra('standard_blob_tier', validator=blob_tier_validator,
                arg_type=get_enum_type(t_standard_blob_tier), min_api='2019-02-02',
                help='A standard blob tier value to set the blob to. For this version of the '
                'library, this is only applicable to block blobs on standard storage accounts.')
        c.argument('encryption_scope', validator=validate_encryption_scope_client_params,
                   help='A predefined encryption scope used to encrypt the data on the service.')
        c.argument('lease_id', help='Required if the blob has an active lease.')
        c.extra('tags', arg_type=tags_type)
