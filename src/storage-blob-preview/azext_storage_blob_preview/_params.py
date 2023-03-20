# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands.validators import validate_tags
from azure.cli.core.commands.parameters import (file_type, get_enum_type, get_three_state_flag)

from ._validators import (validate_metadata, get_permission_validator, get_permission_help_string,
                          validate_blob_type, validate_included_datasets_v2, get_datetime_type,
                          add_download_progress_callback, add_progress_callback,
                          validate_storage_data_plane_list, as_user_validator,
                          blob_tier_validator, validate_blob_name_for_upload)

from .profiles import CUSTOM_DATA_STORAGE_BLOB


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements, too-many-lines
    from argcomplete.completers import FilesCompleter

    from knack.arguments import ignore_type, CLIArgumentType

    from .sdkutil import get_table_data_type
    from .completers import get_storage_name_completion_list

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
                                    action='store_true')
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
        default=5000, validator=validate_storage_data_plane_list, options_list='--num-results',
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
             'values are Archive, Cold, Cool and Hot. This is only applicable to block blobs on standard '
             'storage accounts.'
    )

    rehydrate_priority_type = CLIArgumentType(
        arg_type=get_enum_type(t_rehydrate_priority), options_list=('--rehydrate-priority', '-r'),
        min_api='2019-02-02',
        help='Indicate the priority with which to rehydrate an archived blob.')

    tags_condition_type = CLIArgumentType(
        options_list='--tags-condition', min_api='2019-12-12',
        help='Specify a SQL where clause on blob tags to operate only on blobs with a matching value.')
    timeout_type = CLIArgumentType(
        help='Request timeout in seconds. Applies to each call to the service.', type=int
    )
    t_delete_snapshots = self.get_sdk('_generated.models#DeleteSnapshotsOptionType',
                                      resource_type=CUSTOM_DATA_STORAGE_BLOB)
    delete_snapshots_type = CLIArgumentType(
        arg_type=get_enum_type(t_delete_snapshots),
        help='Required if the blob has associated snapshots. "only": Deletes only the blobs snapshots. '
             '"include": Deletes the blob along with all snapshots.')
    overwrite_type = CLIArgumentType(
        arg_type=get_three_state_flag(),
        help='Whether the blob to be uploaded should overwrite the current data. If True, upload_blob will '
        'overwrite the existing data. If set to False, the operation will fail with ResourceExistsError. '
        'The exception to the above is with Append blob types: if set to False and the data already exists, '
        'an error will not be raised and the data will be appended to the existing blob. If set '
        'overwrite=True, then the existing append blob will be deleted, and a new one created. '
        'Defaults to False.')

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
        c.argument('socket_timeout', deprecate_info=c.deprecate(hide=True),
                   help='The socket timeout(secs), used by the service to regulate data flow.')

    with self.argument_context('storage blob copy') as c:
        c.argument('container_name', container_name_type, options_list=('--destination-container', '-c'))
        c.argument('blob_name', blob_name_type, options_list=('--destination-blob', '-b'),
                   help='Name of the destination blob. If the exists, it will be overwritten.')

    with self.argument_context('storage blob copy start', resource_type=CUSTOM_DATA_STORAGE_BLOB) as c:
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

        c.ignore('blob_url')
        c.argument('blob_name', options_list=['--destination-blob', '-b'], required=True,
                   help='Name of the destination blob. If it exists, it will be overwritten.')
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
        c.extra('destination_blob_type', arg_type=get_enum_type(['Detect', 'BlockBlob', 'PageBlob', 'AppendBlob']),
                help='Defines the type of blob at the destination. '
                     'Value of "Detect" determines the type based on source blob type.')

    with self.argument_context('storage blob copy start-batch', arg_group='Copy Source') as c:
        from ._validators import get_source_file_or_blob_service_client

        c.argument('source_client', ignore_type, validator=get_source_file_or_blob_service_client)

        c.extra('source_account_name')
        c.extra('source_account_key')
        c.extra('source_uri')
        c.argument('source_sas')
        c.argument('source_container')
        c.argument('source_share')

    with self.argument_context('storage blob delete') as c:
        c.register_blob_arguments()
        c.register_precondition_options()

        c.extra('lease', lease_type)
        c.extra('snapshot', snapshot_type)
        c.extra('version_id', version_id_type)
        c.argument('delete_snapshots', delete_snapshots_type)

    with self.argument_context('storage blob delete-batch') as c:
        c.register_precondition_options()

        c.ignore('container_name')
        c.argument('source', options_list=('--source', '-s'))
        c.argument('delete_snapshots', delete_snapshots_type)
        c.argument('lease_id', help='The active lease id for the blob.')

    with self.argument_context('storage blob download') as c:
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
        c.extra('no_progress', progress_type, validator=add_download_progress_callback)
        c.extra('snapshot', snapshot_type)
        c.extra('lease', lease_type)
        c.extra('version_id', version_id_type)
        c.extra('max_concurrency', options_list='--max-connections', type=int, default=2,
                help='The number of parallel connections with which to download.')
        c.argument('open_mode', help='Mode to use when opening the file. Note that specifying append only open_mode '
                   'prevents parallel download. So, max_connections must be set to 1 if this open_mode is used.')
        c.extra('validate_content', action='store_true', min_api='2016-05-31',
                help='If true, calculates an MD5 hash for each chunk of the blob. The storage service checks the '
                'hash of the content that has arrived with the hash that was sent. This is primarily valuable for '
                'detecting bitflips on the wire if using http instead of https, as https (the default), will already '
                'validate. Note that this MD5 hash is not stored with the blob. Also note that if enabled, the '
                'memory-efficient algorithm will not be used because computing the MD5 hash requires buffering '
                'entire blocks, and doing so defeats the purpose of the memory-efficient algorithm.')

    with self.argument_context('storage blob download-batch') as c:
        # c.register_precondition_options()
        c.ignore('container_name')
        c.argument('destination', options_list=('--destination', '-d'))
        c.argument('source', options_list=('--source', '-s'))
        c.extra('max_concurrency', options_list='--max-connections', type=int, default=2,
                help='The number of parallel connections with which to download.')
        c.extra('no_progress', progress_type)

    with self.argument_context('storage blob exists') as c:
        c.register_blob_arguments()

    with self.argument_context('storage blob set-legal-hold') as c:
        c.register_blob_arguments()
        c.argument('legal_hold', arg_type=get_three_state_flag(),
                   help='Specified if a legal hold should be set on the blob.')

    with self.argument_context('storage blob immutability-policy delete') as c:
        c.register_blob_arguments()

    with self.argument_context('storage blob immutability-policy set') as c:
        c.register_blob_arguments()
        c.argument('expiry_time', type=get_datetime_type(False),
                   help='expiration UTC datetime in (Y-m-d\'T\'H:M:S\'Z\')')
        c.argument('policy_mode', arg_type=get_enum_type(['Locked', 'Unlocked']), help='Lock or Unlock the policy')

    with self.argument_context('storage blob filter') as c:
        c.argument('filter_expression', options_list=['--tag-filter'])
        c.argument('container_name', container_name_type,
                   help='Used when you want to list blobs under a specified container')

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
        c.register_lease_blob_arguments()
        c.extra('lease_id', options_list='--proposed-lease-id', help='Proposed lease ID, in a GUID string format. '
                'The Blob service returns 400 (Invalid request) if the proposed lease ID is not in the correct format.')
        c.argument('lease_duration', help='Specify the duration of the lease, in seconds, or negative one (-1) for '
                   'a lease that never expires. A non-infinite lease can be between 15 and 60 seconds. A lease '
                   'duration cannot be changed using renew or change. Default is -1 (infinite lease)', type=int)
        c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob lease break') as c:
        c.register_precondition_options()
        c.register_lease_blob_arguments()
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
        c.register_lease_blob_arguments()
        c.extra('proposed_lease_id', help='Proposed lease ID, in a GUID string format. The Blob service returns 400 '
                '(Invalid request) if the proposed lease ID is not in the correct format.', required=True)
        c.extra('lease_id', help='Required if the blob has an active lease.', required=True)
        c.extra('if_tags_match_condition', tags_condition_type)

    for item in ['release', 'renew']:
        with self.argument_context('storage blob lease {}'.format(item)) as c:
            c.register_precondition_options()
            c.register_lease_blob_arguments()
            c.extra('lease_id', help='Required if the blob has an active lease.', required=True)
            c.extra('if_tags_match_condition', tags_condition_type)

    for item in ['show', 'update']:
        with self.argument_context('storage blob metadata {}'.format(item), resource_type=CUSTOM_DATA_STORAGE_BLOB) \
                as c:
            c.register_blob_arguments()
            c.register_precondition_options()
            c.extra('lease', lease_type)
            c.extra('snapshot', snapshot_type)
            c.extra('if_tags_match_condition', tags_condition_type)

    with self.argument_context('storage blob service-properties delete-policy update') as c:
        c.argument('enable', arg_type=get_enum_type(['true', 'false']), help='Enables/disables soft-delete.')
        c.argument('days_retained', type=int,
                   help='Number of days that soft-deleted blob will be retained. Must be in range [1,365].')

    with self.argument_context('storage blob service-properties update', min_api='2018-03-28') as c:
        c.argument('delete_retention', arg_type=get_three_state_flag(), arg_group='Soft Delete',
                   help='Enables soft-delete.')
        c.argument('delete_retention_period', type=int, arg_group='Soft Delete',
                   help='Number of days that soft-deleted blob will be retained. Must be in range [1,365].')
        c.argument('static_website', arg_group='Static Website', arg_type=get_three_state_flag(),
                   help='Enables static-website.')
        c.argument('index_document', help='The default name of the index page under each directory.',
                   arg_group='Static Website')
        c.argument('error_document_404_path', options_list=['--404-document'], arg_group='Static Website',
                   help='The absolute path of the custom 404 page.')
        c.argument('default_index_document_path', options_list='--default-index-path', is_preview=True,
                   help='Absolute path of the default index page.',
                   arg_group='Static Website')

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
        from ._validators import validate_encryption_scope_client_params, validate_upload_blob

        from .sdkutil import get_blob_types

        t_blob_content_settings = self.get_sdk('_models#ContentSettings', resource_type=CUSTOM_DATA_STORAGE_BLOB)

        c.register_blob_arguments()
        c.register_precondition_options()
        c.register_content_settings_argument(t_blob_content_settings, update=False, arg_group="Content Control")

        c.extra('blob_name', validator=validate_blob_name_for_upload)

        c.argument('file_path', options_list=('--file', '-f'), type=file_type, completer=FilesCompleter(),
                   help='Path of the file to upload as the blob content.', validator=validate_upload_blob)
        c.argument('data', help='The blob data to upload.', required=False, is_preview=True, min_api='2019-02-02')
        c.argument('length', type=int, help='Number of bytes to read from the stream. This is optional, but should be '
                                            'supplied for optimal performance. Cooperate with --data.', is_preview=True,
                   min_api='2019-02-02')
        c.argument('overwrite', arg_type=get_three_state_flag(), arg_group="Additional Flags", is_preview=True,
                   help='Whether the blob to be uploaded should overwrite the current data. If True, blob upload '
                        'operation will overwrite the existing data. If set to False, the operation will fail with '
                        'ResourceExistsError. The exception to the above is with Append blob types: if set to False and the '
                        'data already exists, an error will not be raised and the data will be appended to the existing '
                        'blob. If set overwrite=True, then the existing append blob will be deleted, and a new one created. '
                        'Defaults to False.')
        c.argument('max_connections', type=int, arg_group="Additional Flags",
                   help='Maximum number of parallel connections to use when the blob size exceeds 64MB.')
        c.extra('maxsize_condition', type=int, arg_group="Content Control",
                help='The max length in bytes permitted for the append blob.')
        c.argument('blob_type', options_list=('--type', '-t'), validator=validate_blob_type,
                   arg_type=get_enum_type(get_blob_types()), arg_group="Additional Flags")
        c.argument('validate_content', action='store_true', min_api='2016-05-31', arg_group="Content Control")
        c.extra('no_progress', progress_type, validator=add_progress_callback, arg_group="Additional Flags")
        c.extra('tier', tier_type, validator=blob_tier_validator, arg_group="Additional Flags")
        c.argument('encryption_scope', validator=validate_encryption_scope_client_params,
                   help='A predefined encryption scope used to encrypt the data on the service.',
                   arg_group="Additional Flags")
        c.argument('lease_id', help='Required if the blob has an active lease.')
        c.extra('tags', arg_type=tags_type, arg_group="Additional Flags")
        c.argument('metadata', arg_group="Additional Flags")
        c.argument('timeout', arg_group="Additional Flags")
        c.extra('connection_timeout', options_list=('--socket-timeout'), type=int,
                help='The socket timeout(secs), used by the service to regulate data flow.')

    with self.argument_context('storage blob upload-batch') as c:
        from .sdkutil import get_blob_types

        t_blob_content_settings = self.get_sdk('_models#ContentSettings', resource_type=CUSTOM_DATA_STORAGE_BLOB)
        c.register_precondition_options()
        c.register_content_settings_argument(t_blob_content_settings, update=False, arg_group='Content Control')
        c.ignore('source_files', 'destination_container_name')

        c.argument('source', options_list=('--source', '-s'))
        c.argument('destination', options_list=('--destination', '-d'))
        c.argument('max_connections', type=int,
                   help='Maximum number of parallel connections to use when the blob size exceeds 64MB.')
        c.argument('maxsize_condition', arg_group='Content Control')
        c.argument('validate_content', action='store_true', min_api='2016-05-31', arg_group='Content Control')
        c.argument('blob_type', options_list=('--type', '-t'), arg_type=get_enum_type(get_blob_types()))
        c.extra('no_progress', progress_type)
        c.extra('tier', tier_type, is_preview=True)
        c.extra('overwrite', overwrite_type, is_preview=True)

    with self.argument_context('storage blob query') as c:
        from ._validators import validate_text_configuration
        c.register_blob_arguments()
        c.register_precondition_options()
        line_separator = CLIArgumentType(help="The string used to separate records.", default='\n')
        column_separator = CLIArgumentType(help="The string used to separate columns.", default=',')
        quote_char = CLIArgumentType(help="The string used to quote a specific field.", default='"')
        record_separator = CLIArgumentType(help="The string used to separate records.", default='\n')
        escape_char = CLIArgumentType(help="The string used as an escape character. Default to empty.", default="")
        has_header = CLIArgumentType(
            arg_type=get_three_state_flag(),
            help="Whether the blob data includes headers in the first line. "
            "The default value is False, meaning that the data will be returned inclusive of the first line. "
            "If set to True, the data will be returned exclusive of the first line.", default=False)
        c.extra('lease', options_list='--lease-id',
                help='Required if the blob has an active lease.')
        c.argument('query_expression', help='The query expression in SQL. The maximum size of the query expression '
                   'is 256KiB. For more information about the expression syntax, please see '
                   'https://docs.microsoft.com/azure/storage/blobs/query-acceleration-sql-reference')
        c.extra('input_format', arg_type=get_enum_type(['csv', 'json', 'parquet']), validator=validate_text_configuration,
                min_api='2020-10-02',
                help='Serialization type of the data currently stored in the blob. '
                'The default is to treat the blob data as CSV data formatted in the default dialect.'
                'The blob data will be reformatted according to that profile when blob format is specified. '
                'If you choose `json`, please specify `Input Json Text Configuration Arguments` accordingly; '
                'If you choose `csv`, please specify `Input Delimited Text Configuration Arguments`.')
        c.extra('output_format', arg_type=get_enum_type(['csv', 'json']),
                help='Output serialization type for the data stream. '
                'By default the data will be returned as it is represented in the blob. '
                'By providing an output format, the blob data will be reformatted according to that profile. '
                'If you choose `json`, please specify `Output Json Text Configuration Arguments` accordingly; '
                'If you choose `csv`, please specify `Output Delimited Text Configuration Arguments`.'
                'By default data with input_format of `parquet` will have the output_format of `csv`')
        c.extra('in_line_separator',
                arg_group='Input Json Text Configuration',
                arg_type=line_separator)
        c.extra('in_column_separator', arg_group='Input Delimited Text Configuration',
                arg_type=column_separator)
        c.extra('in_quote_char', arg_group='Input Delimited Text Configuration',
                arg_type=quote_char)
        c.extra('in_record_separator', arg_group='Input Delimited Text Configuration',
                arg_type=record_separator)
        c.extra('in_escape_char', arg_group='Input Delimited Text Configuration',
                arg_type=escape_char)
        c.extra('in_has_header', arg_group='Input Delimited Text Configuration',
                arg_type=has_header)
        c.extra('out_line_separator',
                arg_group='Output Json Text Configuration',
                arg_type=line_separator)
        c.extra('out_column_separator', arg_group='Output Delimited Text Configuration',
                arg_type=column_separator)
        c.extra('out_quote_char', arg_group='Output Delimited Text Configuration',
                arg_type=quote_char)
        c.extra('out_record_separator', arg_group='Output Delimited Text Configuration',
                arg_type=record_separator)
        c.extra('out_escape_char', arg_group='Output Delimited Text Configuration',
                arg_type=escape_char)
        c.extra('out_has_header', arg_group='Output Delimited Text Configuration',
                arg_type=has_header)
        c.extra('result_file', help='Specify the file path to save result.')
        c.ignore('input_config')
        c.ignore('output_config')

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

    with self.argument_context('storage container list') as c:
        c.extra('timeout', timeout_type)
        c.argument('marker', arg_type=marker_type)
        c.argument('num_results', arg_type=num_results_type)
        c.argument('prefix',
                   help='Filter the results to return only blobs whose name begins with the specified prefix.')
        c.argument('include_metadata', arg_type=get_three_state_flag(),
                   help='Specify that container metadata to be returned in the response.')
        c.argument('show_next_marker', action='store_true', is_preview=True,
                   help='Show nextMarker in result when specified.')
        c.argument('include_deleted', arg_type=get_three_state_flag(), min_api='2020-02-10',
                   help='Specify that deleted containers to be returned in the response. This is for container restore '
                   'enabled account. The default value is `False`')

    with self.argument_context('storage container restore') as c:
        c.argument('deleted_container_name', options_list=['--name', '-n'],
                   help='Specify the name of the deleted container to restore.')
        c.argument('deleted_container_version', options_list=['--deleted-version'],
                   help='Specify the version of the deleted container to restore.')
        c.argument('new_name', help='The new name for the deleted container to be restored to.')
        c.extra('timeout', timeout_type)
