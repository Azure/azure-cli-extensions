# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ExportPipeline, ExportPipelineTargetProperties
from .utility_functions import print_poll_output, create_identity_properties, print_keyvault_policy_output, print_pipeline_output, print_lite_pipeline_output

def create_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options, user_assigned_identity_resource_id=None):
    options_list = options.split(',')
    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    export_pipeline_target_type = "AzureStorageBlobContainer"
    export_pipeline_target_properties = ExportPipelineTargetProperties(key_vault_uri=keyvault_secret_uri, uri=storage_account_container_uri, type=export_pipeline_target_type)
    identity_properties = create_identity_properties(user_assigned_identity_resource_id)
    export_pipeline = ExportPipeline(identity=identity_properties, target=export_pipeline_target_properties, options=options_list)

    poller = client.export_pipelines.begin_create(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name, export_pipeline_create_parameters=export_pipeline)
    print_poll_output(poller)

    raw_result = client.export_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name)
    print_pipeline_output(raw_result)

    print_keyvault_policy_output(keyvault_secret_uri=keyvault_secret_uri, user_assigned_identity_resource_id=user_assigned_identity_resource_id, raw_result=raw_result)

def list_exportpipeline(cmd, client, resource_group_name, registry_name):
    raw_result = client.export_pipelines.list(resource_group_name=resource_group_name, registry_name=registry_name)

    for pipeline in raw_result:
        print_lite_pipeline_output(pipeline)

def delete_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    poller = client.export_pipelines.begin_delete(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name)
    print_poll_output(poller)

def get_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    raw_result = client.export_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name)
    print_pipeline_output(raw_result)
