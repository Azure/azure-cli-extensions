# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.profiles import ResourceType
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import (tags_type, file_type, get_location_type, get_enum_type,
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

    timeout_type = CLIArgumentType(
        help='Request timeout in seconds. Applies to each call to the service.', type=int
    )

    snapshot_type = CLIArgumentType(
        help='The snapshot parameter is an opaque DateTime value that, when present, specifies the blob snapshot '
        'to retrieve.'
    )

    marker_type = CLIArgumentType(
        help='A string value that identifies the portion of the list of containers to be '
             'returned with the next listing operation. The operation returns the NextMarker value within '
             'the response body if the listing operation did not return all containers remaining to be listed '
             'with the current page. If specified, this generator will begin returning results from the point '
             'where the previous generator stopped.')

    num_results_type = CLIArgumentType(
        type=int, default=5000, help='Specify the maximum number to return. If the request does not specify '
        'num_results, or specifies a value greater than 5000, the server will return up to 5000 items. Note that '
        'if the listing operation crosses a partition boundary, then the service will return a continuation token '
        'for retrieving the remaining of the results. Provide "*" to return all.'
    )

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

    with self.argument_context('storage blob') as c:
        c.argument('blob_name', options_list=('--name', '-n'), arg_type=blob_name_type)
        c.argument('destination_path', help='The destination path that will be appended to the blob name.')

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
        c.extra('snapshot', help='The snapshot parameter is an opaque DateTime value that, when present, '
                                 'specifies the blob snapshot to retrieve.')
        c.argument('lease_id', help='Required if the blob has an active lease.')
        c.extra('version_id', min_api='2019-12-12',
                help='The version id parameter is an opaque DateTime value that, when present, '
                     'specifies the version of the blob to operate on.')


