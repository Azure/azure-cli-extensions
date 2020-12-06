# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ImportPipeline, ImportPipelineSourceProperties, PipelineTriggerProperties, PipelineSourceTriggerProperties
from .utility_functions import print_poll_output, create_identity_properties, print_keyvault_policy_output, print_pipeline_output, print_lite_pipeline_output

def create_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options=None, user_assigned_identity_resource_id=None, source_trigger_enabled="True"):
    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    if options is None:
        options_list = []
    else:
        options_list = options.split(',')

    identity_properties = create_identity_properties(user_assigned_identity_resource_id)
    import_pipeline_source_properties = ImportPipelineSourceProperties(key_vault_uri=keyvault_secret_uri, uri=storage_account_container_uri)

    source_trigger_enabled = False if source_trigger_enabled.lower() == "false" else True
    source_trigger_status = "Disabled" if not source_trigger_enabled else "Enabled"

    pipeline_source_trigger_properties = PipelineSourceTriggerProperties(status=source_trigger_status)
    pipeline_trigger_properties = PipelineTriggerProperties(source_trigger=pipeline_source_trigger_properties)
    import_pipeline = ImportPipeline(identity=identity_properties, source=import_pipeline_source_properties, trigger=pipeline_trigger_properties, options=options_list)

    poller = client.import_pipelines.begin_create(resource_group_name=resource_group_name, registry_name=registry_name, import_pipeline_name=import_pipeline_name, import_pipeline_create_parameters=import_pipeline)
    print_poll_output(poller)

    raw_result = client.import_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, import_pipeline_name=import_pipeline_name)
    print_pipeline_output(raw_result)

    print_keyvault_policy_output(keyvault_secret_uri=keyvault_secret_uri,user_assigned_identity_resource_id=user_assigned_identity_resource_id, raw_result=raw_result)

def list_importpipeline(cmd, client, resource_group_name, registry_name):
    raw_result = client.import_pipelines.list(resource_group_name=resource_group_name, registry_name=registry_name)

    for pipeline in raw_result:
        print_lite_pipeline_output(pipeline)

def delete_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name):
    poller = client.import_pipelines.begin_delete(resource_group_name=resource_group_name, registry_name=registry_name, import_pipeline_name=import_pipeline_name)  
    print_poll_output(poller)

def get_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name):
    raw_result = client.import_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, import_pipeline_name=import_pipeline_name)
    print_pipeline_output(raw_result)
    