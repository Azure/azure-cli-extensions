# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

import time
from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import PipelineRun, PipelineRunRequest, PipelineRunSourceProperties, PipelineRunTargetProperties
from .utility_functions import print_poll_output, print_pipeline_output, print_lite_pipeline_output

def create_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_name, pipeline_run_name, pipeline_type, storage_blob_name, artifacts=None, force_update_tag=False):
    if pipeline_type == "import":
        try:
            raw_result = client.import_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, import_pipeline_name=pipeline_name)
        except:
            raise CLIError(f'Import pipeline {pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.')

        pipeline_resource_id = raw_result.id
        pipeline_run_source = PipelineRunSourceProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, source=pipeline_run_source)

    else:
        try:
            raw_result = client.export_pipelines.get(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=pipeline_name)
        except:
            raise CLIError(f'Export pipeline {pipeline_name} not found on registry {registry_name} in the {resource_group_name} resource group.')

        pipeline_resource_id = raw_result.id
        if artifacts is None:
            raise CLIError("artifacts cannot be null for Export PipelineRuns. Please provide a comma separated list of container images to be exported in the form REPOSITORY:TAG or REPOSITORY@sha256:90659bf80b44ce6be8234e6ff90a1ac34acbeb826903b02cfa0da11c82cbc042.")

        artifact_list = artifacts.split(',')
        #add tag ":latest" if a tag is not present
        artifact_list = [artifact + ":latest" if ":" not in artifact and "@" not in artifact else artifact for artifact in artifact_list]
        pipeline_run_target = PipelineRunTargetProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, target=pipeline_run_target, artifacts=artifact_list)

    force_update_tag_str = str(time.time()) if force_update_tag else None
    pipeline_run = PipelineRun(request=pipeline_run_request, force_update_tag=force_update_tag_str)

    poller = client.pipeline_runs.begin_create(resource_group_name=resource_group_name, registry_name=registry_name, pipeline_run_name=pipeline_run_name, pipeline_run_create_parameters=pipeline_run)
    print_poll_output(poller)

    get_pipelinerun(cmd=cmd, client=client, resource_group_name=resource_group_name, registry_name=registry_name, pipeline_run_name=pipeline_run_name)

def get_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    raw_result = client.pipeline_runs.get(resource_group_name=resource_group_name, registry_name=registry_name, pipeline_run_name=pipeline_run_name)
    return print_pipeline_output(raw_result)

def delete_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    client.pipeline_runs.begin_delete(resource_group_name=resource_group_name, registry_name=registry_name, pipeline_run_name=pipeline_run_name)

def list_pipelinerun(cmd, client, resource_group_name, registry_name):
    raw_result = client.pipeline_runs.list(resource_group_name=resource_group_name, registry_name=registry_name)
    pipe_list = []

    for pipelinerun in raw_result:
        pipe_list.append(print_lite_pipeline_output(pipelinerun))
    
    return pipe_list
