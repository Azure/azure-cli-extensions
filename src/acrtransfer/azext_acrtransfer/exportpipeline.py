# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import ResourceNotFoundError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ExportPipeline, ExportPipelineTargetProperties
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._container_registry_management_client_enums import PipelineSourceType
from .utility_functions import create_identity_properties


def create_exportpipeline(client, resource_group_name, registry_name, export_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options=None, user_assigned_identity_resource_id=None):
    '''Create an export pipeline.'''

    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    export_pipeline_target_type = PipelineSourceType.AZURE_STORAGE_BLOB_CONTAINER
    export_pipeline_target_properties = ExportPipelineTargetProperties(key_vault_uri=keyvault_secret_uri,
                                                                       uri=storage_account_container_uri,
                                                                       type=export_pipeline_target_type)

    identity_properties = create_identity_properties(user_assigned_identity_resource_id)
    export_pipeline = ExportPipeline(identity=identity_properties,
                                     target=export_pipeline_target_properties,
                                     options=options)

    client.export_pipelines.begin_create(resource_group_name=resource_group_name,
                                         registry_name=registry_name,
                                         export_pipeline_name=export_pipeline_name,
                                         export_pipeline_create_parameters=export_pipeline)

    return client.export_pipelines.get(resource_group_name=resource_group_name,
                                       registry_name=registry_name,
                                       export_pipeline_name=export_pipeline_name)


def get_exportpipeline(client, resource_group_name, registry_name, export_pipeline_name):
    '''Get an export pipeline.'''

    return client.export_pipelines.get(resource_group_name=resource_group_name,
                                       registry_name=registry_name,
                                       export_pipeline_name=export_pipeline_name)


def delete_exportpipeline(client, resource_group_name, registry_name, export_pipeline_name):
    '''Delete an export pipeline.'''

    try:
        client.export_pipelines.get(resource_group_name=resource_group_name,
                                    registry_name=registry_name,
                                    export_pipeline_name=export_pipeline_name)

    except Exception as e:
        raise ResourceNotFoundError(f'Export pipeline {export_pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.') from e

    return client.export_pipelines.begin_delete(resource_group_name=resource_group_name,
                                                registry_name=registry_name,
                                                export_pipeline_name=export_pipeline_name)


def list_exportpipeline(client, resource_group_name, registry_name):
    '''List export pipelines on a registry.'''

    return client.export_pipelines.list(resource_group_name=resource_group_name, registry_name=registry_name)
