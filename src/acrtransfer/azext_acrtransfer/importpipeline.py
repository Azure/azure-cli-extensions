# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from azure.cli.core.azclierror import ResourceNotFoundError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ImportPipeline, ImportPipelineSourceProperties, PipelineTriggerProperties, PipelineSourceTriggerProperties
from .utility_functions import create_identity_properties


def create_importpipeline(client, resource_group_name, registry_name, import_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options=None, user_assigned_identity_resource_id=None, source_trigger_enabled=True):
    '''Create an import pipeline.'''

    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    identity_properties = create_identity_properties(user_assigned_identity_resource_id)
    import_pipeline_source_properties = ImportPipelineSourceProperties(key_vault_uri=keyvault_secret_uri, uri=storage_account_container_uri)
    source_trigger_status = "Enabled" if source_trigger_enabled else "Disabled"

    pipeline_source_trigger_properties = PipelineSourceTriggerProperties(status=source_trigger_status)
    pipeline_trigger_properties = PipelineTriggerProperties(source_trigger=pipeline_source_trigger_properties)
    import_pipeline = ImportPipeline(identity=identity_properties,
                                     source=import_pipeline_source_properties,
                                     trigger=pipeline_trigger_properties,
                                     options=options)

    client.import_pipelines.begin_create(resource_group_name=resource_group_name,
                                         registry_name=registry_name,
                                         import_pipeline_name=import_pipeline_name,
                                         import_pipeline_create_parameters=import_pipeline)

    return client.import_pipelines.get(resource_group_name=resource_group_name,
                                       registry_name=registry_name,
                                       import_pipeline_name=import_pipeline_name)


def get_importpipeline(client, resource_group_name, registry_name, import_pipeline_name):
    '''Get an import pipeline.'''

    return client.import_pipelines.get(resource_group_name=resource_group_name,
                                       registry_name=registry_name,
                                       import_pipeline_name=import_pipeline_name)


def delete_importpipeline(client, resource_group_name, registry_name, import_pipeline_name):
    '''Delete an import pipeline.'''

    try:
        client.import_pipelines.get(resource_group_name=resource_group_name,
                                    registry_name=registry_name,
                                    import_pipeline_name=import_pipeline_name)

    except Exception as e:
        raise ResourceNotFoundError(f'Import pipeline {import_pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.') from e

    return client.import_pipelines.begin_delete(resource_group_name=resource_group_name,
                                                registry_name=registry_name,
                                                import_pipeline_name=import_pipeline_name)


def list_importpipeline(client, resource_group_name, registry_name):
    '''List import pipelines on a registry.'''

    return client.import_pipelines.list(resource_group_name=resource_group_name, registry_name=registry_name)
