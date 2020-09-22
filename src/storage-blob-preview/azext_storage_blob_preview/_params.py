# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands.validators import validate_tags
from azure.cli.core.commands.parameters import (file_type, get_enum_type, get_three_state_flag)
from azure.cli.core.local_context import LocalContextAttribute, LocalContextAction

from ._validators import (validate_metadata, get_permission_validator, get_permission_help_string,
                          validate_blob_type, validate_included_datasets_v2, add_progress_callback,
                          validate_storage_data_plane_list, as_user_validator, blob_tier_validator,
                          validate_container_delete_retention_days, validate_delete_retention_days,
                          process_resource_group)

from .profiles import CUSTOM_DATA_STORAGE_BLOB, CUSTOM_MGMT_STORAGE


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements, too-many-lines
    from argcomplete.completers import FilesCompleter

    from knack.arguments import CLIArgumentType

    from azure.cli.core.commands.parameters import get_resource_name_completion_list

    from .sdkutil import get_table_data_type
    from .completers import get_storage_name_completion_list

    acct_name_type = CLIArgumentType(options_list=['--account-name', '-n'], help='The storage account name.',
                                     id_part='name',
                                     completer=get_resource_name_completion_list('Microsoft.Storage/storageAccounts'),
                                     local_context_attribute=LocalContextAttribute(
                                         name='storage_account_name', actions=[LocalContextAction.GET]))

    t_base_blob_service = self.get_sdk('blob.baseblobservice#BaseBlobService')
    t_file_service = self.get_sdk('file#FileService')
    t_table_service = get_table_data_type(self.cli_ctx, 'table', 'TableService')
    t_blob_tier = self.get_sdk('_generated.models._azure_blob_storage_enums#AccessTierOptional',
                               resource_type=CUSTOM_DATA_STORAGE_BLOB)
    t_rehydrate_priority = self.get_sdk('_generated.models._azure_blob_storage_enums#RehydratePriority',
                                        resource_type=CUSTOM_DATA_STORAGE_BLOB)

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
    share_name_type = CLIArgumentType(options_list=['--share-name', '-s'], help='The file share name.',
                                      completer=get_storage_name_completion_list(t_file_service, 'list_shares'))
    table_name_type = CLIArgumentType(options_list=['--table-name', '-t'],
                                      completer=get_storage_name_completion_list(t_table_service, 'list_tables'))
    progress_type = CLIArgumentType(help='Include this flag to disable progress reporting for the command.',
                                    action='store_true', validator=add_progress_callback)
    sas_help = 'The permissions the SAS grants. Allowed values: {}. Do not use if a stored access policy is ' \
               'referenced with --policy-name that specifies this value. Can be combined.'

    lease_type = CLIArgumentType(
        options_list='--lease-id', help='Required if the blob has an active lease.'
    )

    snapshot_type = CLIArgumentType(
        help='The snapshot parameter is an opaque DateTime value that, when present, specifies the blob snapshot '
        'to retrieve.'
    )

    tags_type = CLIArgumentType(
        nargs='*', validator=validate_tags, min_api='2019-12-12', is_preview=True,
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
        help='An optional blob version ID. This parameter is only for versioning enabled account. ',
        min_api='2019-12-12', is_preview=True
    )  # Fix preview display

    tier_type = CLIArgumentType(
        arg_type=get_enum_type(t_blob_tier), min_api='2019-02-02',
        help='The tier value to set the blob to. For page blob, the tier correlates to the size of the blob '
             'and number of allowed IOPS. Possible values are P10, P15, P20, P30, P4, P40, P50, P6, P60, P70, P80 '
             'and this is only applicable to page blobs on premium storage accounts; For block blob, possible '
             'values are Archive, Cool and Hot. This is only applicable to block blobs on standard storage accounts.'
    )

    rehydrate_priority_type = CLIArgumentType(
        arg_type=get_enum_type(t_rehydrate_priority), options_list=('--rehydrate-priority', '-r'),
        min_api='2019-02-02',
        help='Indicate the priority with which to rehydrate an archived blob.')

    tags_condition_type = CLIArgumentType(
        options_list='--tags-condition', min_api='2019-12-12',
        help='Specify a SQL where clause on blob tags to operate only on blobs with a matching value.')

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

    with self.argument_context('storage account blob-service-properties show',
                               resource_type=CUSTOM_MGMT_STORAGE) as c:
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('resource_group_name', required=False, validator=process_resource_group)

    with self.argument_context('storage account blob-service-properties update',
                               resource_type=CUSTOM_MGMT_STORAGE) as c:
        c.argument('account_name', acct_name_type, id_part=None)
        c.argument('resource_group_name', required=False, validator=process_resource_group)
        c.argument('enable_change_feed', arg_type=get_three_state_flag(), min_api='2019-04-01')
        c.argument('enable_container_delete_retention',
                   arg_type=get_three_state_flag(),
                   options_list=['--enable-container-delete-retention', '--container-retention'],
                   arg_group='Container Delete Retention Policy', min_api='2019-06-01',
                   help='Enable container delete retention policy for container soft delete when set to true. '
                        'Disable container delete retention policy when set to false.')
        c.argument('container_delete_retention_days',
                   options_list=['--container-delete-retention-days', '--container-days'],
                   type=int, arg_group='Container Delete Retention Policy',
                   min_api='2019-06-01', validator=validate_container_delete_retention_days,
                   help='Indicate the number of days that the deleted container should be retained. The minimum '
                        'specified value can be 1 and the maximum value can be 365.')
        c.argument('enable_delete_retention', arg_type=get_three_state_flag(), arg_group='Delete Retention Policy',
                   min_api='2018-07-01')
        c.argument('delete_retention_days', type=int, arg_group='Delete Retention Policy',
                   validator=validate_delete_retention_days, min_api='2018-07-01')
        c.argument('enable_restore_policy', arg_type=get_three_state_flag(), arg_group='Restore Policy',
                   min_api='2019-06-01', help="Enable blob restore policy when it set to true.")
        c.argument('restore_days', type=int, arg_group='Restore Policy',
                   min_api='2019-06-01', help="The number of days for the blob can be restored. It should be greater "
                   "than zero and less than Delete Retention Days.")
        c.argument('enable_versioning', arg_type=get_three_state_flag(), help='Versioning is enabled if set to true.',
                   min_api='2019-06-01')
        c.argument('enable_last_access_tracking', arg_type=get_three_state_flag(), min_api='2019-06-01',
                   options_list=['--enable-last-access-tracking', '-t'],
                   help='When set to true last access time based tracking policy is enabled.')

    with self.argument_context('storage account management-policy create') as c:
        c.argument('policy', type=file_type, completer=FilesCompleter(),
                   help='The Storage Account ManagementPolicies Rules, in JSON format. See more details in: '
                        'https://docs.microsoft.com/azure/storage/common/storage-lifecycle-managment-concepts.')
        c.argument('account_name', help='The name of the storage account within the specified resource group.')

    with self.argument_context('storage account management-policy update') as c:
        c.argument('account_name', help='The name of the storage account within the specified resource group.')

    with self.argument_context('storage blob') as c:
        c.argument('blob_name', options_list=('--name', '-n'), arg_type=blob_name_type)

    with self.argument_context('storage blob copy start') as c:
        from ._validators import validate_source_url

        c.register_blob_arguments()
        c.register_precondition_options()
        c.register_precondition_options(prefix='source_')
        c.register_source_uri_arguments(validator=validate_source_url)

        c.ignore('incremental_copy')
        c.argument('if_match', options_list=['--destination-if-match'])
        c.argument('if_modified_since', options_list=['--destination-if-modified-since'])
        c.argument('if_none_match', options_list=['--destination-if-none-match'])
        c.argument('if_unmodified_since', options_list=['--destination-if-unmodified-since'])
        c.argument('if_tags_match_condition', options_list=['--destination-tags-condition'])

        c.argument('blob_name', options_list=['--destination-blob', '-b'], required=True,
                   help='Name of the destination blob. If the exists, it will be overwritten.')
        c.argument('container_name', options_list=['--destination-container', '-c'], required=True,
                   help='The container name.')
        c.extra('destination_lease', options_list='--destination-lease-id',
                help='The lease ID specified for this header must match the lease ID of the estination blob. '
                'If the request does not include the lease ID or it is not valid, the operation fails with status '
                'code 412 (Precondition Failed).')
        c.extra('source_lease', options_list='--source-lease-id', arg_group='Copy Source',
                help='Specify this to perform the Copy Blob operation only if the lease ID given matches the '
                'active lease ID of the source blob.')
        c.extra('rehydrate_priority', rehydrate_priority_type)
        c.extra('requires_sync', arg_type=get_three_state_flag(),
                help='Enforce that the service will not return a response until the copy is complete.')
        c.extra('tier', tier_type)
        c.extra('tags', tags_type)

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
        c.argument('file_path', options_list=('--file', '-f'), type=file_type, completer=FilesCompleter(),
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

    with self.argument_context('storage blob exists') as c:
        c.register_blob_arguments()

    with self.argument_context('storage blob filter') as c:
        c.argument('filter_expression', options_list=['--tag-filter'])

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
                   help='Indicate that this command return the full blob URI and the shared access signature token.')
        c.argument('as_user', min_api='2018-11-09', action='store_true',
                   validator=as_user_validator,
                   help="Indicates that this command return the SAS signed with the user delegation key. "
                        "The expiry parameter and '--auth-mode login' are required if this argument is specified. ")
        c.argument('id', options_list='--policy-name',
                   help='The name of a stored access policy within the container\'s ACL.',
                   completer=get_storage_acl_name_completion_list(t_base_blob_service, 'container_name',
                                                                  'get_container_acl'))
        c.argument('ip', help='Specify an IP address or a range of IP addresses from which to accept requests. '
                   'If the IP address from which the request originates does not match the IP address or address range '
                   'specified on the SAS token, the request is not authenticated. For example, specifying ip=168.1.5.65'
                   ' or ip=168.1.5.60-168.1.5.70 on the SAS restricts the request to those IP addresses.')
        c.argument('permission', options_list='--permissions',
                   help=sas_help.format(get_permission_help_string(t_blob_permissions)),
                   validator=get_permission_validator(t_blob_permissions))
        c.argument('snapshot', snapshot_type)
        c.ignore('sas_token')
        c.argument('version_id', version_id_type)

    with self.argument_context('storage blob lease') as c:
        c.argument('blob_name', arg_type=blob_name_type)

    with self.argument_context('storage blob lease acquire') as c:
        c.register_precondition_options()
        c.register_blob_arguments()
        c.extra('lease_id', options_list='--proposed-lease-id', help='Proposed lease ID, in a GUID string format. '
                'The Blob service returns 400 (Invalid request) if the proposed lease ID is not in the correct format.')
        c.argument('lease_duration', help='Specify the duration of the lease, in seconds, or negative one (-1) for '
                   'a lease that never expires. A non-infinite lease can be between 15 and 60 seconds. A lease '
                   'duration cannot be changed using renew or change. Default is -1 (infinite lease)', type=int)
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob lease break') as c:
        c.register_precondition_options()
        c.register_blob_arguments()
        c.argument('lease_break_period', type=int,
                   help="This is the proposed duration of seconds that the lease should continue before it is broken, "
                   "between 0 and 60 seconds. This break period is only used if it is shorter than the time remaining "
                   "on the lease. If longer, the time remaining on the lease is used. A new lease will not be "
                   "available before the break period has expired, but the lease may be held for longer than the break "
                   "period. If this header does not appear with a break operation, a fixed-duration lease breaks after "
                   "the remaining lease period elapses, and an infinite lease breaks immediately.")
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob lease change') as c:
        c.register_precondition_options()
        c.register_blob_arguments()
        c.extra('proposed_lease_id', help='Proposed lease ID, in a GUID string format. The Blob service returns 400 '
                '(Invalid request) if the proposed lease ID is not in the correct format.', required=True)
        c.extra('lease_id', help='Required if the blob has an active lease.', required=True)
        c.extra('if_tags_match_condition', tags_condition_type)

    for item in ['release', 'renew']:
        with self.argument_context('storage blob lease {}'.format(item)) as c:
            c.register_precondition_options()
            c.register_blob_arguments()
            c.extra('lease_id', help='Required if the blob has an active lease.', required=True)
            c.extra('if_tags_match_condition', tags_condition_type)

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
                   help='Filter the results to return only blobs whose name begins with the specified prefix.')
        c.argument('show_next_marker', action='store_true',
                   help='Show nextMarker in result when specified.')

    for item in ['show', 'update']:
        with self.argument_context('storage blob metadata {}'.format(item), resource_type=CUSTOM_DATA_STORAGE_BLOB) \
                as c:
            c.register_blob_arguments()
            c.register_precondition_options()
            c.extra('lease', lease_type)
            c.extra('snapshot', snapshot_type)
            c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob set-tier', resource_type=CUSTOM_DATA_STORAGE_BLOB) as c:
        c.register_blob_arguments()

        c.argument('blob_type', options_list=('--type', '-t'), arg_type=get_enum_type(('block', 'page')))
        c.extra('tier', tier_type, validator=blob_tier_validator, required=True)
        c.argument('rehydrate_priority', rehydrate_priority_type, is_preview=True)
        c.extra('version_id', version_id_type)
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob show') as c:
        c.register_blob_arguments()
        c.register_precondition_options()
        c.extra('snapshot', snapshot_type)
        c.extra('lease', lease_type)
        c.argument('version_id', version_id_type)

    with self.argument_context('storage blob snapshot') as c:
        c.register_blob_arguments()
        c.register_precondition_options()
        c.extra('lease', lease_type)
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob undelete', resource_type=CUSTOM_DATA_STORAGE_BLOB) as c:
        c.register_blob_arguments()

    with self.argument_context('storage blob tag list') as c:
        c.register_blob_arguments()
        c.extra('version_id', version_id_type)
        c.extra('snapshot', snapshot_type)
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob tag set') as c:
        c.register_blob_arguments()
        c.extra('version_id', version_id_type)
        c.argument('tags', tags_type, required=True)
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob upload') as c:
        from ._validators import validate_encryption_scope_client_params, \
            add_progress_callback_v2
        from .sdkutil import get_blob_types

        t_blob_content_settings = self.get_sdk('_models#ContentSettings', resource_type=CUSTOM_DATA_STORAGE_BLOB)

        c.register_blob_arguments()
        c.register_precondition_options()
        c.register_content_settings_argument(t_blob_content_settings, update=False)

        c.argument('file_path', options_list=('--file', '-f'), type=file_type, completer=FilesCompleter(),
                   help='Path of the file to upload as the blob content.')
        c.argument('overwrite', arg_type=get_three_state_flag(),
                   help='Whether the blob to be uploaded should overwrite the current data. If True, upload_blob will '
                   'overwrite the existing data. If set to False, the operation will fail with ResourceExistsError. '
                   'The exception to the above is with Append blob types: if set to False and the data already exists, '
                   'an error will not be raised and the data will be appended to the existing blob. If set '
                   'overwrite=True, then the existing append blob will be deleted, and a new one created. '
                   'Defaults to False.', is_preview=True)
        c.argument('max_connections', type=int,
                   help='Maximum number of parallel connections to use when the blob size exceeds 64MB.')
        c.extra('maxsize_condition', type=int,
                help='The max length in bytes permitted for the append blob.')
        c.argument('blob_type', options_list=('--type', '-t'), validator=validate_blob_type,
                   arg_type=get_enum_type(get_blob_types()))
        c.argument('validate_content', action='store_true', min_api='2016-05-31')
        c.extra('no_progress', progress_type, validator=add_progress_callback_v2)
        c.argument('socket_timeout', deprecate_info=c.deprecate(hide=True),
                   help='The socket timeout(secs), used by the service to regulate data flow.')
        c.extra('tier', tier_type, validator=blob_tier_validator)
        c.argument('encryption_scope', validator=validate_encryption_scope_client_params,
                   help='A predefined encryption scope used to encrypt the data on the service.')
        c.argument('lease_id', help='Required if the blob has an active lease.')
        c.extra('tags', arg_type=tags_type)

    with self.argument_context('storage container') as c:
        c.argument('container_name', container_name_type, options_list=('--name', '-n'))

    with self.argument_context('storage container generate-sas') as c:
        from .completers import get_storage_acl_name_completion_list
        t_container_permissions = self.get_sdk('_models#ContainerSasPermissions',
                                               resource_type=CUSTOM_DATA_STORAGE_BLOB)
        c.register_sas_arguments()
        c.argument('id', options_list='--policy-name',
                   help='The name of a stored access policy within the container\'s ACL.',
                   completer=get_storage_acl_name_completion_list(t_container_permissions, 'container_name',
                                                                  'get_container_acl'))
        c.argument('permission', options_list='--permissions',
                   help=sas_help.format(get_permission_help_string(t_container_permissions)),
                   validator=get_permission_validator(t_container_permissions))
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
        c.argument('as_user', min_api='2018-11-09', action='store_true',
                   validator=as_user_validator,
                   help="Indicates that this command return the SAS signed with the user delegation key. "
                        "The expiry parameter and '--auth-mode login' are required if this argument is specified. ")
        c.ignore('sas_token')
        c.argument('full_uri', action='store_true', is_preview=True,
                   help='Indicate that this command return the full blob URI and the shared access signature token.')
