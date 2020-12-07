# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ExportPipeline, ExportPipelineTargetProperties
from .utility_functions import print_poll_output, create_identity_properties, print_keyvault_policy_output, print_pipeline_output, print_lite_pipeline_output

def create_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options=None, user_assigned_identity_resource_id=None):
    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    if options is None:
        options_list = []
    else:
        options_list = options.split(',')

    export_pipeline_target_type = "AzureStorageBlobContainer"
    export_pipeline_target_properties = ExportPipelineTargetProperties(key_vault_uri=keyvault_secret_uri, uri=storage_account_container_uri, type=export_pipeline_target_type)
    identity_properties = create_identity_properties(user_assigned_identity_resource_id)
    export_pipeline = ExportPipeline(identity=identity_properties, target=export_pipeline_target_properties, options=options_list)

    client.export_pipelines.begin_create(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name, export_pipeline_create_parameters=export_pipeline)

    raw_result = client.export_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name)
    print_keyvault_policy_output(keyvault_secret_uri=keyvault_secret_uri, user_assigned_identity_resource_id=user_assigned_identity_resource_id, raw_result=raw_result)

    return print_pipeline_output(raw_result)

def list_exportpipeline(cmd, client, resource_group_name, registry_name):
    raw_result = client.export_pipelines.list(resource_group_name=resource_group_name, registry_name=registry_name)
    pipe_list = []

    for pipeline in raw_result:
        pipe_list.append(print_lite_pipeline_output(pipeline))
    
    return pipe_list
        
def delete_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    client.export_pipelines.begin_delete(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name)

def get_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    raw_result = client.export_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name)
    return print_pipeline_output(raw_result)
   
