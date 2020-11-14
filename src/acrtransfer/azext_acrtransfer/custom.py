# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import PipelineRun
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

def create_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    dummy_pipe = PipelineRun()

    print(dummy_pipe) 

def list_pipelinerun(cmd, client, resource_group_name, registry_name):
    raw_result = client.pipeline_runs.list(resource_group_name, registry_name)

    for pipelinerun in raw_result:
        print(pipelinerun)


def get_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    raw_result = client.pipeline_runs.get(resource_group_name, registry_name, pipeline_run_name)

    print(raw_result)
