# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.core.commands.validators import validate_tags
from azure.cli.core.commands.parameters import (get_enum_type, get_three_state_flag)

from ._validators import (validate_metadata, get_permission_validator, get_permission_help_string,
                          as_user_validator, blob_tier_validator)

from .profiles import CUSTOM_DATA_STORAGE_BLOB


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements, too-many-lines
    from knack.arguments import CLIArgumentType

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

    t_delete_snapshots = self.get_sdk('_generated.models#DeleteSnapshotsOptionType',
                                      resource_type=CUSTOM_DATA_STORAGE_BLOB)
    delete_snapshots_type = CLIArgumentType(
        arg_type=get_enum_type(t_delete_snapshots),
        help='Required if the blob has associated snapshots. "only": Deletes only the blobs snapshots. '
             '"include": Deletes the blob along with all snapshots.')

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

    with self.argument_context('storage blob delete') as c:
        c.register_blob_arguments()
        c.register_precondition_options()

        c.extra('lease', lease_type)
        c.extra('snapshot', snapshot_type)
        c.extra('version_id', version_id_type)
        c.argument('delete_snapshots', delete_snapshots_type)

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
