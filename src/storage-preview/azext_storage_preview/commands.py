# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.arm import show_exception_handler
from ._client_factory import (cf_blob_data_gen_update,
                              blob_data_service_factory, adls_blob_data_service_factory)
from .profiles import CUSTOM_DATA_STORAGE, CUSTOM_DATA_STORAGE_ADLS


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

    base_blob_sdk = CliCommandType(
        operations_tmpl='azext_storage_preview.vendored_sdks.azure_storage.blob.baseblobservice#BaseBlobService.{}',
        client_factory=blob_data_service_factory,
        resource_type=CUSTOM_DATA_STORAGE)

    with self.command_group('storage blob service-properties', command_type=base_blob_sdk) as g:
        g.storage_command_oauth('show', 'get_blob_service_properties', exception_handler=show_exception_handler)
        g.storage_command_oauth('update', generic_update=True, getter_name='get_blob_service_properties',
                                setter_type=get_custom_sdk('blob', cf_blob_data_gen_update),
                                setter_name='set_service_properties',
                                client_factory=cf_blob_data_gen_update)

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

    # Change existing Blob Commands
    with self.command_group('storage blob', command_type=adls_base_blob_sdk) as g:
        from ._format import transform_blob_output
        from ._transformers import transform_storage_list_output
        g.storage_command_oauth('list', 'list_blobs', transform=transform_storage_list_output,
                                table_transformer=transform_blob_output,
                                deprecate_info=self.deprecate(redirect="az storage fs file list", hide=True,
                                                              message_func=_adls_deprecate_message))

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
