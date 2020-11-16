# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import PipelineRun, PipelineRunRequest, PipelineRunSourceProperties, PipelineRunTargetProperties
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ImportPipeline, IdentityProperties, ImportPipelineSourceProperties, PipelineTriggerProperties, UserIdentityProperties, PipelineSourceTriggerProperties
import time
import json

def poll_output(poller, poll_interval=10):
    print("Operation Status: " + poller.status())
    while(not poller.done()):
        print("Please wait " + str(poll_interval) + " seconds for the next update.")
        poller.wait(timeout=poll_interval)
        print("Operation Status: " + poller.status())
    return poller.status()

def create_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options, user_assigned_identity_resource_id=None):
    '''  
        BEGIN_CREATE
        resource_group_name,  # type: str
        registry_name,  # type: str
        import_pipeline_name,  # type: str
        import_pipeline_create_parameters #type ImportPipeline,  
        
        ImportPipeline
        location: Optional[str] = None,
        identity: Optional["IdentityProperties"] = None,
        source: Optional["ImportPipelineSourceProperties"] = None,
        trigger: Optional["PipelineTriggerProperties"] = None,
        options: Optional[List[Union[str, "PipelineOptions"]]] = None,

        IdentityProperties
        principal_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        type: Optional[Union[str, "ResourceIdentityType"]] = None, ### UserAssigned or SystemAssigned
        user_assigned_identities: Optional[Dict[str, "UserIdentityProperties"]] = None, ### MSI resource ID as key

        UserIdentityProperties
        principal_id: Optional[str] = None,
        client_id: Optional[str] = None,
        
        ImportPipelineSourceProperties
        key_vault_uri: str, https://mabenedikv.vault.azure.net/secrets/transfer/
        type: Optional[Union[str, "PipelineSourceType"]] = "AzureStorageBlobContainer", 
        uri: Optional[str] = None, https://accountName.blob.core.windows.net/containerName

        PipelineTriggerProperties 
        source_trigger: Optional["PipelineSourceTriggerProperties"] = None,

        PipelineSourceTriggerProperties
        status: Union[str, "TriggerStatus"]
        "Enabled" or "Disabled" 

        PipelineOptions
        list of strings
        OverwriteTags - Overwrite existing target tags
        DeleteSourceBlobOnSuccess - Delete the source storage blob after successful import to the target registry
        ContinueOnErrors - Continue import of remaining artifacts in the target registry if one artifact import fails.
        DisableSourceTrigger
        '''

    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    if user_assigned_identity_resource_id is None:
        resource_identity_type = "SystemAssigned"
        user_assigned_identities = None
    else:
        resource_identity_type = "UserAssigned"
        user_identity_properties = UserIdentityProperties()
        user_assigned_identities = {user_assigned_identity_resource_id: user_identity_properties}

    identity_properties = IdentityProperties(type=resource_identity_type, user_assigned_identities=user_assigned_identities)

    import_pipeline_source_properties = ImportPipelineSourceProperties(key_vault_uri=keyvault_secret_uri, uri=storage_account_container_uri)

    allowed_options_list = ["DisableSourceTrigger", "OverwriteTags", "DeleteSourceBlobOnSuccess", "ContinueOnErrors"]
    options_list = options.split(',')

    if not set(options_list).issubset(set(allowed_options_list)):
        print("Allowed options are: ", end='')
        print(allowed_options_list)
        raise CLIError("Invalid option found in options parameter. Please provide a comma separated list of allowed options.")

    source_trigger_status = "Disabled" if "DisableSourceTrigger" in options_list else "Enabled"

    pipeline_source_trigger_properties = PipelineSourceTriggerProperties(status=source_trigger_status)
    pipeline_trigger_properties = PipelineTriggerProperties(source_trigger=pipeline_source_trigger_properties)
    import_pipeline = ImportPipeline(identity=identity_properties, source=import_pipeline_source_properties, trigger=pipeline_trigger_properties, options=options_list)

    poller = client.import_pipelines.begin_create(resource_group_name=resource_group_name, registry_name=registry_name, import_pipeline_name=import_pipeline_name, import_pipeline_create_parameters=import_pipeline)
    
    poll_output(poller)

    keyvault_name = keyvault_secret_uri.split("https://")[1].split('.')[0]
    
    #account for ARM bug where the identity user assigned identities dict key resource id has lowercase resourcegroup rather than resourceGroup
    if user_assigned_identity_resource_id is not None: 
        user_assigned_identity_resource_id_list = user_assigned_identity_resource_id.split("/")
        user_assigned_identity_resource_id_list[3] = "resourcegroups"
        user_assigned_identity_resource_id = '/'.join(user_assigned_identity_resource_id_list)

    raw_result = client.import_pipelines.get(resource_group_name, registry_name, import_pipeline_name)
    identity_object_id = raw_result.identity.principal_id if user_assigned_identity_resource_id is None else raw_result.identity.user_assigned_identities[user_assigned_identity_resource_id].principal_id

    print("***YOU MUST RUN THE FOLLOWING COMMAND PRIOR TO ATTEMPTING A PIPELINERUN OR EXPECTING SOURCETRIGGER TO SUCCESSFULLY IMPORT IMAGES***")
    print(f'az keyvault set-policy --name {keyvault_name} --secret-permissions get --object-id {identity_object_id}')


def list_importpipeline(cmd, client, resource_group_name, registry_name):
    raw_result = client.import_pipelines.list(resource_group_name, registry_name)

    for pipeline in raw_result:
        print(pipeline)

        print(pipeline.identity.type)

    

def delete_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name):
    poller = client.import_pipelines.begin_delete(resource_group_name, registry_name, import_pipeline_name)
    
    poll_output(poller=poller)

def get_importpipeline(cmd, client, resource_group_name, registry_name, import_pipeline_name):
    raw_result = client.import_pipelines.get(resource_group_name, registry_name, import_pipeline_name)

    print(raw_result)
    print(raw_result.identity.user_assigned_identities)

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
    
def list_pipelinerun(cmd, client, resource_group_name, registry_name):
    raw_result = client.pipeline_runs.list(resource_group_name, registry_name)

    for pipelinerun in raw_result:
        print(pipelinerun)


def get_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    raw_result = client.pipeline_runs.get(resource_group_name, registry_name, pipeline_run_name)
    print(raw_result)
    print(raw_result.response)

def delete_pipelinerun(cmd, client, resource_group_name, registry_name, pipeline_run_name):
    poller = client.pipeline_runs.begin_delete(resource_group_name, registry_name, pipeline_run_name)
    
    poll_output(poller=poller)
        

    