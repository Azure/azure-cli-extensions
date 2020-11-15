# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import PipelineRun, PipelineRunRequest, PipelineRunSourceProperties, PipelineRunTargetProperties
import json

def create_importpipeline(cmd, client, resource_group_name, registry_name, location=None, tags=None):
    
    raise CLIError('TODO: Implement `importpipeline create`')

def list_importpipeline(cmd, client, resource_group_name, registry_name):
    print("doggo")

    raw_result = client.import_pipelines.list(resource_group_name, registry_name)

    for pipeline in raw_result:
        print(pipeline)

        print(pipeline.identity.type)

    print("done")

def delete_importpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `importpipeline list`')

def get_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name):
    raw_result = client.import_pipelines.get(resource_group_name, registry_name, import_pipeline_name)

    print(raw_result)


def update_importpipeline(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def create_exportpipeline(cmd, client, resource_group_name, registry_name, location=None, tags=None):
    raise CLIError('TODO: Implement `exportpipeline create`')

def list_exportpipeline(cmd, client, resource_group_name, registry_name):
    raw_result = client.export_pipelines.list(resource_group_name, registry_name)

    for pipeline in raw_result:
        print(pipeline)

def delete_exportpipeline(cmd, client, resource_group_name=None):
    raise CLIError('TODO: Implement `exportpipeline list`')

def get_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    raw_result = client.export_pipelines.get(resource_group_name, registry_name, export_pipeline_name)

    print(raw_result)

def update_exportpipeline(cmd, instance, tags=None):
    with cmd.update_context(instance) as c:
        c.set_param('tags', tags)
    return instance

def create_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_name, pipeline_run_name, pipeline_type, storage_blob_name, artifacts=None, force_update_tag=False):
    subscription_id = client._config.subscription_id
    
    if pipeline_type == "import":
        full_pipeline_type = "importPipelines"
        pipeline_resource_id = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.ContainerRegistry/registries/{registry_name}/{full_pipeline_type}/{pipeline_name}'

        pipeline_run_source = PipelineRunSourceProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, source=pipeline_run_source) 

    elif pipeline_type == "export":
        full_pipeline_type = "exportPipelines"
        pipeline_resource_id = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.ContainerRegistry/registries/{registry_name}/{full_pipeline_type}/{pipeline_name}'
        
        if artifacts == None:
             raise CLIError("artifacts cannot be null for Export PipelineRuns. Please provide a comma separated list of container images to be exported in the form REPOSITORY:TAG")
        
        artifact_list = artifacts.split(',')

        #add tag ":latest" if a tag is not present
        artifact_list = [artifact + ":latest" if ":" not in artifact else artifact for artifact in artifact_list]

        pipeline_run_target = PipelineRunTargetProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, target=pipeline_run_target, artifacts=artifact_list) 
    
    else:
        raise CLIError("Incorrect pipeline-type parameter. Accepted values are 'import' or 'export'")
    
    #TODO force update tag doesn't work
    #pipeline run object expects a string for force_update_tag
    force_update_tag_str = "true" if force_update_tag else "false"

    pipeline_run = PipelineRun(request=pipeline_run_request, force_update_tag=force_update_tag_str)

    raw_result = client.pipeline_runs.begin_create(resource_group_name, registry_name, pipeline_run_name, pipeline_run)

    print(raw_result)

def list_pipelinerun(cmd, client, resource_group_name, registry_name):
    raw_result = client.pipeline_runs.list(resource_group_name, registry_name)

    for pipelinerun in raw_result:
        print(pipelinerun)


def get_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    raw_result = client.pipeline_runs.get(resource_group_name, registry_name, pipeline_run_name)

    print(raw_result.response)

def delete_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    poller = client.pipeline_runs.begin_delete(resource_group_name, registry_name, pipeline_run_name)

    print(poller)