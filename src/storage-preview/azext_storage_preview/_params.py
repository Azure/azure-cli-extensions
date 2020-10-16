# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands.parameters import (get_enum_type, get_three_state_flag)

from ._validators import (get_datetime_type, validate_metadata,
                          validate_azcopy_upload_destination_url, validate_azcopy_download_source_url,
                          validate_azcopy_target_url, validate_included_datasets,
                          validate_blob_directory_download_source_url, validate_blob_directory_upload_destination_url,
                          validate_storage_data_plane_list)


def load_arguments(self, _):  # pylint: disable=too-many-locals, too-many-statements
    from knack.arguments import CLIArgumentType

    from .sdkutil import get_table_data_type
    from .completers import get_storage_name_completion_list, get_container_name_completions

    t_base_blob_service = self.get_sdk('blob.baseblobservice#BaseBlobService')
    t_file_service = self.get_sdk('file#FileService')
    t_table_service = get_table_data_type(self.cli_ctx, 'table', 'TableService')

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
