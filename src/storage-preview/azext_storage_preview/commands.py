# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.arm import show_exception_handler
from ._client_factory import (cf_sa, blob_data_service_factory, adls_blob_data_service_factory,
                              cf_share_client, cf_share_service, cf_share_file_client, cf_share_directory_client)
from .profiles import (CUSTOM_DATA_STORAGE, CUSTOM_DATA_STORAGE_ADLS, CUSTOM_MGMT_STORAGE,
                       CUSTOM_DATA_STORAGE_FILESHARE)


def load_command_table(self, _):  # pylint: disable=too-many-locals, too-many-statements

    def get_custom_sdk(custom_module, client_factory, resource_type=CUSTOM_DATA_STORAGE):
        """Returns a CliCommandType instance with specified operation template based on the given custom module name.
        This is useful when the command is not defined in the default 'custom' module but instead in a module under
        'operations' package."""
        return CliCommandType(
            operations_tmpl='azext_storage_preview.operations.{}#'.format(custom_module) + '{}',
            client_factory=client_factory,
            resource_type=resource_type
        )

    storage_account_sdk = CliCommandType(
        operations_tmpl='azext_storage_preview.vendored_sdks.azure_mgmt_storage.operations#'
                        'StorageAccountsOperations.{}',
        client_factory=cf_sa,
        resource_type=CUSTOM_MGMT_STORAGE
    )

    storage_account_custom_type = CliCommandType(
        operations_tmpl='azext_storage_preview.operations.account#{}',
        client_factory=cf_sa,
        resource_type=CUSTOM_MGMT_STORAGE
    )

    with self.command_group('storage account', storage_account_sdk, resource_type=CUSTOM_MGMT_STORAGE,
                            custom_command_type=storage_account_custom_type) as g:
        g.custom_command('create', 'create_storage_account')
        g.generic_update_command('update', getter_name='get_properties', setter_name='update',
                                 custom_func_name='update_storage_account')

    block_blob_sdk = CliCommandType(
        operations_tmpl='azure.multiapi.storage.blob.blockblobservice#BlockBlobService.{}',
        client_factory=blob_data_service_factory,
        resource_type=CUSTOM_DATA_STORAGE)

    with self.command_group('storage azcopy blob', command_type=block_blob_sdk,
                            custom_command_type=get_custom_sdk('azcopy', blob_data_service_factory)) as g:
        g.storage_custom_command_oauth('upload', 'storage_blob_upload')
        g.storage_custom_command_oauth('download', 'storage_blob_download')
        g.storage_custom_command_oauth('delete', 'storage_blob_remove')
        g.storage_custom_command_oauth('sync', 'storage_blob_sync')

    with self.command_group('storage azcopy', custom_command_type=get_custom_sdk('azcopy', None)) as g:
        g.custom_command('run-command', 'storage_run_command', validator=lambda namespace: None)

    # pylint: disable=line-too-long
    adls_base_blob_sdk = CliCommandType(
        operations_tmpl='azext_storage_preview.vendored_sdks.azure_adls_storage_preview.blob.baseblobservice'
                        '#BaseBlobService.{}',
        client_factory=adls_blob_data_service_factory,
        resource_type=CUSTOM_DATA_STORAGE_ADLS)

    def _adls_deprecate_message(self):
        msg = "This {} has been deprecated and will be removed in future release.".format(self.object_type)
        msg += " Use '{}' instead.".format(self.redirect)
        msg += " For more information go to"
        msg += " https://github.com/Azure/azure-cli/blob/dev/src/azure-cli/azure/cli/command_modules/storage/docs/ADLS%20Gen2.md"
        return msg

    # New Blob Commands
    with self.command_group('storage blob', command_type=adls_base_blob_sdk,
                            custom_command_type=get_custom_sdk('blob', adls_blob_data_service_factory,
                                                               CUSTOM_DATA_STORAGE_ADLS),
                            resource_type=CUSTOM_DATA_STORAGE_ADLS) as g:
        g.storage_command_oauth('move', 'rename_path', is_preview=True,
                                deprecate_info=self.deprecate(redirect="az storage fs file move", hide=True,
                                                              message_func=_adls_deprecate_message))

    with self.command_group('storage blob access', command_type=adls_base_blob_sdk,
                            custom_command_type=get_custom_sdk('blob', adls_blob_data_service_factory,
                                                               CUSTOM_DATA_STORAGE_ADLS),
                            resource_type=CUSTOM_DATA_STORAGE_ADLS,
                            deprecate_info=self.deprecate(redirect="az storage fs access", hide=True,
                                                          message_func=_adls_deprecate_message)) as g:
        g.storage_command_oauth('set', 'set_path_access_control')
        g.storage_command_oauth('update', 'set_path_access_control')
        g.storage_command_oauth('show', 'get_path_access_control')

    # TODO: Remove them after deprecate for two sprints
    # Blob directory Commands Group
    with self.command_group('storage blob directory', command_type=adls_base_blob_sdk,
                            custom_command_type=get_custom_sdk('blob', adls_blob_data_service_factory,
                                                               CUSTOM_DATA_STORAGE_ADLS),
                            resource_type=CUSTOM_DATA_STORAGE_ADLS, is_preview=True) as g:
        from ._format import transform_blob_output
        from ._transformers import (transform_storage_list_output, create_boolean_result_output_transformer)
        g.storage_command_oauth('create', 'create_directory')
        g.storage_command_oauth('delete', 'delete_directory')
        g.storage_custom_command_oauth('move', 'rename_directory')
        g.storage_custom_command_oauth('show', 'show_directory', table_transformer=transform_blob_output,
                                       exception_handler=show_exception_handler)
        g.storage_custom_command_oauth('list', 'list_directory', transform=transform_storage_list_output,
                                       table_transformer=transform_blob_output)
        g.storage_command_oauth('exists', 'exists', transform=create_boolean_result_output_transformer('exists'))
        g.storage_command_oauth(
            'metadata show', 'get_blob_metadata', exception_handler=show_exception_handler)
        g.storage_command_oauth('metadata update', 'set_blob_metadata')

    with self.command_group('storage blob directory', is_preview=True,
                            custom_command_type=get_custom_sdk('azcopy', adls_blob_data_service_factory,
                                                               CUSTOM_DATA_STORAGE_ADLS))as g:
        g.storage_custom_command_oauth('upload', 'storage_blob_upload')
        g.storage_custom_command_oauth('download', 'storage_blob_download')

    with self.command_group('storage blob directory access', command_type=adls_base_blob_sdk, is_preview=True,
                            custom_command_type=get_custom_sdk('blob', adls_blob_data_service_factory,
                                                               CUSTOM_DATA_STORAGE_ADLS),
                            resource_type=CUSTOM_DATA_STORAGE_ADLS) as g:
        g.storage_command_oauth('set', 'set_path_access_control')
        g.storage_command_oauth('update', 'set_path_access_control')
        g.storage_command_oauth('show', 'get_path_access_control')

    with self.command_group('storage blob directory',
                            deprecate_info=self.deprecate(redirect="az storage fs directory", hide=True,
                                                          message_func=_adls_deprecate_message)) as g:
        pass

    share_client_sdk = CliCommandType(
        operations_tmpl='azure.multiapi.storagev2.fileshare._share_client#ShareClient.{}',
        client_factory=cf_share_client,
        resource_type=CUSTOM_DATA_STORAGE_FILESHARE)

    directory_client_sdk = CliCommandType(
        operations_tmpl='azext_storage_preview.vendored_sdks.azure_storagev2.fileshare._directory_client#ShareDirectoryClient.{}',
        client_factory=cf_share_directory_client,
        resource_type=CUSTOM_DATA_STORAGE_FILESHARE)

    file_client_sdk = CliCommandType(
        operations_tmpl='azext_storage_preview.vendored_sdks.azure_storagev2.fileshare._file_client#ShareFileClient.{}',
        client_factory=cf_share_file_client,
        resource_type=CUSTOM_DATA_STORAGE_FILESHARE)

    with self.command_group('storage share', command_type=share_client_sdk,
                            custom_command_type=get_custom_sdk('fileshare', cf_share_client,
                                                               CUSTOM_DATA_STORAGE_FILESHARE),
                            resource_type=CUSTOM_DATA_STORAGE_FILESHARE, min_api='2022-11-02') as g:
        from ._transformers import transform_share_list_handle
        g.storage_custom_command_oauth('list-handle', 'list_handle', transform=transform_share_list_handle)
        g.storage_custom_command_oauth('close-handle', 'close_handle')

    with self.command_group('storage directory', command_type=directory_client_sdk,
                            resource_type=CUSTOM_DATA_STORAGE_FILESHARE,
                            custom_command_type=get_custom_sdk('directory', cf_share_directory_client)) as g:
        from ._transformers import transform_share_directory_json_output
        from ._format import transform_file_directory_result, transform_file_output, transform_boolean_for_table
        g.storage_custom_command_oauth('create', 'create_directory',
                                       transform=create_boolean_result_output_transformer('created'),
                                       table_transformer=transform_boolean_for_table)
        g.storage_custom_command_oauth('delete', 'delete_directory',
                                       transform=create_boolean_result_output_transformer('deleted'),
                                       table_transformer=transform_boolean_for_table)
        g.storage_custom_command_oauth('show', 'get_directory_properties',
                                       transform=transform_share_directory_json_output,
                                       table_transformer=transform_file_output,
                                       exception_handler=show_exception_handler)
        g.storage_command_oauth('exists', 'exists',
                                transform=create_boolean_result_output_transformer('exists'))
        g.storage_command_oauth('metadata show', 'get_directory_properties',
                                exception_handler=show_exception_handler,
                                transform=lambda x: getattr(x, 'metadata', x))
        g.storage_command_oauth('metadata update', 'set_directory_metadata')
        g.storage_custom_command_oauth('list', 'list_share_directories',
                                       transform=transform_file_directory_result,
                                       table_transformer=transform_file_output)

    with self.command_group('storage file', command_type=file_client_sdk,
                            resource_type=CUSTOM_DATA_STORAGE_FILESHARE,
                            custom_command_type=get_custom_sdk('file', cf_share_file_client)) as g:
        from ._transformers import transform_file_show_result, transform_url_without_encode
        from ._format import transform_metadata_show, transform_boolean_for_table, transform_file_output
        from ._exception_handler import file_related_exception_handler
        g.storage_custom_command_oauth('list', 'list_share_files', client_factory=cf_share_client,
                                       transform=transform_file_directory_result,
                                       table_transformer=transform_file_output)
        g.storage_command_oauth('delete', 'delete_file', transform=create_boolean_result_output_transformer('deleted'),
                                table_transformer=transform_boolean_for_table)
        g.storage_custom_command_oauth('delete-batch', 'storage_file_delete_batch', client_factory=cf_share_client)
        g.storage_command_oauth('resize', 'resize_file')
        g.storage_custom_command_oauth('url', 'create_file_url', transform=transform_url_without_encode,
                                       client_factory=cf_share_client)
        g.storage_custom_command('generate-sas', 'generate_sas_file', client_factory=cf_share_client)
        g.storage_command_oauth('show', 'get_file_properties', transform=transform_file_show_result,
                                table_transformer=transform_file_output,
                                exception_handler=show_exception_handler)
        g.storage_custom_command_oauth('update', 'file_updates')
        g.storage_custom_command_oauth('exists', 'file_exists',
                                       transform=create_boolean_result_output_transformer('exists'))
        g.storage_command_oauth('metadata show', 'get_file_properties', exception_handler=show_exception_handler,
                                transform=transform_metadata_show)
        g.storage_command_oauth('metadata update', 'set_file_metadata')
        g.storage_custom_command_oauth('copy start', 'storage_file_copy')
        g.storage_command_oauth('copy cancel', 'abort_copy')
        g.storage_custom_command('copy start-batch', 'storage_file_copy_batch', client_factory=cf_share_client)
        g.storage_custom_command_oauth('upload', 'storage_file_upload',
                                       exception_handler=file_related_exception_handler)
        g.storage_custom_command('upload-batch', 'storage_file_upload_batch',
                                 custom_command_type=get_custom_sdk('file', client_factory=cf_share_client))
        g.storage_custom_command_oauth('download', 'download_file',
                                       exception_handler=file_related_exception_handler,
                                       transform=transform_file_show_result)
        g.storage_custom_command('download-batch', 'storage_file_download_batch', client_factory=cf_share_client)
