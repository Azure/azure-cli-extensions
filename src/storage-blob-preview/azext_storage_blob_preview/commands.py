from ._client_factory import cf_blob_client, cf_container_client, cf_blob_service

from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.arm import show_exception_handler
from azure.cli.core.profiles import ResourceType
from .profiles import CUSTOM_DATA_STORAGE_BLOB


def load_command_table(self, _):  # pylint: disable=too-many-locals, too-many-statements

    def get_custom_sdk(custom_module, client_factory, resource_type=ResourceType.DATA_STORAGE):
        """Returns a CliCommandType instance with specified operation template based on the given custom module name.
        This is useful when the command is not defined in the default 'custom' module but instead in a module under
        'operations' package."""
        return CliCommandType(
            operations_tmpl='azext_storage_blob_preview.operations.{}#'.format(
                custom_module) + '{}',
            client_factory=client_factory,
            resource_type=resource_type
        )

    blob_client_sdk = CliCommandType(
        operations_tmpl='azext_storage_blob_preview.vendored_sdks.azure_storage_blob._blob_client#BlobClient.{}',
        client_factory=cf_blob_client,
        resource_type=CUSTOM_DATA_STORAGE_BLOB
    )

    blob_service_sdk = CliCommandType(
        operations_tmpl='azext_storage_blob_preview.vendored_sdks.azure_storage_blob._blob_service_client#BlobServiceClient.{}',
        client_factory=cf_blob_service,
        resource_type=CUSTOM_DATA_STORAGE_BLOB
    )

    container_client_sdk = CliCommandType(
        operations_tmpl='azext_storage_blob_preview.vendored_sdks.azure_storage_blob._container_client#ContainerClient.{}',
        client_factory=cf_container_client,
        resource_type=CUSTOM_DATA_STORAGE_BLOB
    )

    with self.command_group('storage blob', blob_client_sdk, resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            min_api='2019-02-02',
                            custom_command_type=get_custom_sdk('blob', client_factory=cf_blob_client,
                                                               resource_type=CUSTOM_DATA_STORAGE_BLOB)) as g:
        from azure.cli.command_modules.storage._format import transform_blob_output
        from ._transformers import transform_blob_list_output, transform_blob_json_output
        g.storage_custom_command_oauth('list', 'list_blobs', client_factory=cf_container_client,
                                       transform=transform_blob_list_output,
                                       table_transformer=transform_blob_output)
        g.storage_custom_command_oauth('show', 'show_blob_v2', transform=transform_blob_json_output,
                                       table_transformer=transform_blob_output,
                                       exception_handler=show_exception_handler)
        g.storage_custom_command_oauth('upload', 'upload_blob')
        g.storage_command_oauth('copy start', 'start_copy_from_url')
        g.storage_command_oauth('delete', 'delete_blob')
        g.storage_custom_command_oauth('download', 'download_blob')
        g.storage_custom_command_oauth('generate-sas', 'generate_sas_blob_uri',
                                       custom_command_type=get_custom_sdk(
                                           'blob', client_factory=cf_blob_service,
                                           resource_type=CUSTOM_DATA_STORAGE_BLOB))
        g.storage_custom_command_oauth('set-tier', 'set_blob_tier_v2')

    with self.command_group('storage blob', blob_service_sdk, resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            min_api='2019-12-12',
                            custom_command_type=get_custom_sdk('blob', client_factory=cf_blob_service,
                                                               resource_type=CUSTOM_DATA_STORAGE_BLOB)) as g:
        g.storage_command_oauth('filter', 'find_blobs_by_tags')

    with self.command_group('storage blob tag', command_type=blob_client_sdk,
                            custom_command_type=get_custom_sdk('blob', cf_blob_client),
                            is_preview=True, resource_type=CUSTOM_DATA_STORAGE_BLOB, min_api='2019-12-12') as g:
        g.storage_command_oauth('list', 'get_blob_tags')
        g.storage_command_oauth('set', 'set_blob_tags')

    with self.command_group('storage container', blob_client_sdk, resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            min_api='2019-02-02',
                            custom_command_type=get_custom_sdk('blob', client_factory=cf_container_client,
                                                               resource_type=CUSTOM_DATA_STORAGE_BLOB)) as g:
        g.storage_custom_command_oauth('generate-sas', 'generate_sas_container_uri',
                                       custom_command_type=get_custom_sdk('blob', client_factory=cf_blob_service,
                                                                          resource_type=CUSTOM_DATA_STORAGE_BLOB))


