# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azure.cli.core.commands.arm import show_exception_handler
from azure.cli.core.profiles import ResourceType

from ._client_factory import cf_blob_client, cf_container_client, cf_blob_service, cf_blob_lease_client
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
        operations_tmpl='azext_storage_blob_preview.vendored_sdks.azure_storage_blob._blob_service_client#'
                        'BlobServiceClient.{}',
        client_factory=cf_blob_service,
        resource_type=CUSTOM_DATA_STORAGE_BLOB
    )

    blob_service_custom_sdk = get_custom_sdk('blob', client_factory=cf_blob_service,
                                             resource_type=CUSTOM_DATA_STORAGE_BLOB)

    with self.command_group('storage blob', blob_client_sdk, resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            min_api='2019-02-02',
                            custom_command_type=get_custom_sdk('blob', client_factory=cf_blob_client,
                                                               resource_type=CUSTOM_DATA_STORAGE_BLOB)) as g:
        from azure.cli.command_modules.storage._format import transform_blob_output
        from ._transformers import transform_blob_json_output, transform_metadata,\
            create_boolean_result_output_transformer, transform_blob_list_output
        from ._validators import (process_blob_download_batch_parameters, process_blob_delete_batch_parameters,
                                  process_blob_upload_batch_parameters)
        g.storage_command_oauth('delete', 'delete_blob')
        g.storage_custom_command_oauth('download', 'download_blob', transform=transform_blob_json_output)
        g.storage_command_oauth('exists', 'exists', transform=create_boolean_result_output_transformer('exists'))
        g.storage_custom_command_oauth('generate-sas', 'generate_sas_blob_uri',
                                       custom_command_type=blob_service_custom_sdk)
        g.storage_command_oauth('metadata show', 'get_blob_properties', exception_handler=show_exception_handler,
                                transform=transform_metadata)
        g.storage_command_oauth('metadata update', 'set_blob_metadata')
        g.storage_custom_command_oauth('set-tier', 'set_blob_tier_v2')
        g.storage_command_oauth('snapshot', 'create_snapshot')  # need to refine output
        g.storage_custom_command_oauth('show', 'show_blob_v2', transform=transform_blob_json_output,
                                       table_transformer=transform_blob_output,
                                       exception_handler=show_exception_handler)
        g.storage_command_oauth('undelete', 'undelete_blob')
        g.storage_custom_command_oauth('upload', 'upload_blob')
        g.storage_custom_command_oauth('upload-batch', 'storage_blob_upload_batch', client_factory=cf_blob_service,
                                       validator=process_blob_upload_batch_parameters)
        g.storage_custom_command_oauth('download-batch', 'storage_blob_download_batch', client_factory=cf_blob_service,
                                       validator=process_blob_download_batch_parameters)
        g.storage_custom_command_oauth('delete-batch', 'storage_blob_delete_batch', client_factory=cf_blob_service,
                                       validator=process_blob_delete_batch_parameters)
        g.storage_custom_command_oauth('copy start-batch', 'storage_blob_copy_batch', client_factory=cf_blob_service)
        g.storage_custom_command_oauth('query', 'query_blob',
                                       is_preview=True, min_api='2020-10-02')
        g.storage_command_oauth('set-legal-hold', 'set_legal_hold', min_api='2020-10-02', is_preview=True)
        g.storage_custom_command_oauth('immutability-policy set', 'set_blob_immutability_policy',
                                       min_api='2020-10-02', is_preview=True)
        g.storage_command_oauth('immutability-policy delete', 'delete_immutability_policy',
                                min_api='2020-10-02', is_preview=True)

    with self.command_group('storage blob', blob_service_sdk, resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            min_api='2019-12-12',
                            custom_command_type=blob_service_custom_sdk) as g:
        g.storage_custom_command_oauth('filter', 'find_blobs_by_tags', is_preview=True)

    blob_lease_client_sdk = CliCommandType(
        operations_tmpl='azure.multiapi.storagev2.blob._lease#BlobLeaseClient.{}',
        client_factory=cf_blob_lease_client,
        resource_type=ResourceType.DATA_STORAGE_BLOB
    )

    with self.command_group('storage blob lease', blob_lease_client_sdk, resource_type=ResourceType.DATA_STORAGE_BLOB,
                            min_api='2019-02-02',
                            custom_command_type=get_custom_sdk('blob', client_factory=cf_blob_lease_client,
                                                               resource_type=ResourceType.DATA_STORAGE_BLOB)) as g:
        g.storage_custom_command_oauth('acquire', 'acquire_blob_lease')
        g.storage_command_oauth('break', 'break_lease')
        g.storage_command_oauth('change', 'change')
        g.storage_custom_command_oauth('renew', 'renew_blob_lease')
        g.storage_command_oauth('release', 'release')

    with self.command_group('storage blob service-properties delete-policy', command_type=blob_service_sdk,
                            min_api='2019-02-02', resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            custom_command_type=get_custom_sdk('blob', cf_blob_service)) as g:
        g.storage_command_oauth('show', 'get_service_properties',
                                transform=lambda x: x.get('delete_retention_policy', x),
                                exception_handler=show_exception_handler)
        g.storage_custom_command_oauth('update', 'set_delete_policy')

    with self.command_group('storage blob service-properties', command_type=blob_service_sdk,
                            custom_command_type=get_custom_sdk('blob', cf_blob_service),
                            min_api='2019-02-02', resource_type=CUSTOM_DATA_STORAGE_BLOB) as g:
        from ._transformers import transform_blob_service_properties
        g.storage_command_oauth(
            'show', 'get_service_properties', exception_handler=show_exception_handler,
            transform=transform_blob_service_properties)
        g.storage_custom_command_oauth('update', 'set_service_properties',
                                       transform=transform_blob_service_properties)

    # --auth-mode login need to verify
    with self.command_group('storage blob tag', command_type=blob_client_sdk,
                            custom_command_type=get_custom_sdk('blob', cf_blob_client),
                            resource_type=CUSTOM_DATA_STORAGE_BLOB, min_api='2019-12-12', is_preview=True) as g:
        g.storage_command_oauth('list', 'get_blob_tags')
        g.storage_custom_command_oauth('set', 'set_blob_tags')

    with self.command_group('storage container', resource_type=CUSTOM_DATA_STORAGE_BLOB,
                            min_api='2019-02-02',
                            custom_command_type=get_custom_sdk('blob', client_factory=cf_container_client,
                                                               resource_type=CUSTOM_DATA_STORAGE_BLOB)) as g:
        from ._transformers import transform_container_list_output
        from azure.cli.command_modules.storage._format import transform_container_list
        g.storage_custom_command_oauth('generate-sas', 'generate_sas_container_uri',
                                       custom_command_type=blob_service_custom_sdk)
        g.storage_custom_command_oauth('list', 'list_containers', custom_command_type=blob_service_custom_sdk,
                                       transform=transform_container_list_output,
                                       table_transformer=transform_container_list)
        g.storage_command_oauth('restore', 'undelete_container', command_type=blob_service_sdk,
                                min_api='2020-02-10', is_preview=True)
