from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import PipelineRun, PipelineRunRequest, PipelineRunSourceProperties, PipelineRunTargetProperties
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ImportPipeline, IdentityProperties, ImportPipelineSourceProperties, PipelineTriggerProperties, UserIdentityProperties, PipelineSourceTriggerProperties
from .utility_functions import poll_output, print_pipeline_output
import time
import json

def create_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_name, pipeline_run_name, pipeline_type, storage_blob_name, artifacts=None, force_update_tag=False):
    subscription_id = client._config.subscription_id
    
    if pipeline_type == "import":
        pipeline_resource_id = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.ContainerRegistry/registries/{registry_name}/importPipelines/{pipeline_name}'

        pipeline_run_source = PipelineRunSourceProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, source=pipeline_run_source) 

    elif pipeline_type == "export":
        pipeline_resource_id = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.ContainerRegistry/registries/{registry_name}/exportPipelines/{pipeline_name}'
        
        if artifacts is None:
             raise CLIError("artifacts cannot be null for Export PipelineRuns. Please provide a comma separated list of container images to be exported in the form REPOSITORY:TAG")
        
        artifact_list = artifacts.split(',')

        #add tag ":latest" if a tag is not present
        artifact_list = [artifact + ":latest" if ":" not in artifact else artifact for artifact in artifact_list]

        pipeline_run_target = PipelineRunTargetProperties(name=storage_blob_name)
        pipeline_run_request = PipelineRunRequest(pipeline_resource_id=pipeline_resource_id, target=pipeline_run_target, artifacts=artifact_list)
    
    else:
        raise CLIError("Incorrect pipeline-type parameter. Accepted values are 'import' or 'export'")
    
    force_update_tag_str = str(time.time()) if force_update_tag else None
    
    pipeline_run = PipelineRun(request=pipeline_run_request, force_update_tag=force_update_tag_str)

    poller = client.pipeline_runs.begin_create(resource_group_name, registry_name, pipeline_run_name, pipeline_run)
    poll_output(poller=poller)

    get_pipelinerun(cmd=cmd, client=client, resource_group_name=resource_group_name, registry_name=registry_name, pipeline_run_name=pipeline_run_name)
    
def get_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    raw_result = client.pipeline_runs.get(resource_group_name, registry_name, pipeline_run_name)

    print_pipeline_output(raw_result)
    #del raw_result.response.source 
    #object_str= json.dumps(raw_result, default=lambda o: getattr(o, '__dict__', str(o)), indent=2)
    #clean_obj_str = object_str.replace('"additional_properties": {},', '')
    #clean_obj_str = clean_obj_str.replace('"location": null,', '')
    #print('\n'.join([line for line in clean_obj_str.split("\n") if line.strip()!='']))

def delete_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    poller = client.pipeline_runs.begin_delete(resource_group_name, registry_name, pipeline_run_name)
    
    poll_output(poller=poller)

def list_pipelinerun(cmd, client, resource_group_name, registry_name):
    raw_result = client.pipeline_runs.list(resource_group_name, registry_name)

    for pipelinerun in raw_result:
        print(pipelinerun)