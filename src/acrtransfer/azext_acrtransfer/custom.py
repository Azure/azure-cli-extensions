# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import PipelineRun, PipelineRunRequest, PipelineRunSourceProperties, PipelineRunTargetProperties
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ImportPipeline, IdentityProperties, ImportPipelineSourceProperties, PipelineTriggerProperties, UserIdentityProperties, PipelineSourceTriggerProperties
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import ExportPipeline, ExportPipelineTargetProperties

import time
import json
from .pipelinerun import *
from .utility_functions import *



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

def create_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name, keyvault_secret_uri, storage_account_container_uri, options, user_assigned_identity_resource_id=None):
    '''     
        EXPORT PIPELINE
        identity: Optional["IdentityProperties"] = None,
        target: Optional["ExportPipelineTargetProperties"] = None,
        options: Optional[List[Union[str, "PipelineOptions"]]] = None,
        
        EXPORTPIPELINETARGETPROPERTIES
        key_vault_uri: str, https://mabenedikv.vault.azure.net/secrets/transfer/
        type: Optional[str] = None, AzureStorageBlobContainer
        uri: Optional[str] = None, https://accountName.blob.core.windows.net/containerName
    '''

    allowed_options_list = ["OverwriteBlobs", "ContinueOnErrors"]
    options_list = options.split(',')

    if not set(options_list).issubset(set(allowed_options_list)):
        print("Allowed options are: ", end='')
        print(allowed_options_list)
        raise CLIError("Invalid option found in options parameter. Please provide a comma separated list of allowed options.")

    keyvault_secret_uri = keyvault_secret_uri.lower()
    storage_account_container_uri = storage_account_container_uri.lower()

    export_pipeline_target_type = "AzureStorageBlobContainer"

    export_pipeline_target_properties = ExportPipelineTargetProperties(key_vault_uri=keyvault_secret_uri, uri=storage_account_container_uri, type=export_pipeline_target_type)
    
    if user_assigned_identity_resource_id is None:
        resource_identity_type = "SystemAssigned"
        user_assigned_identities = None
    else:
        resource_identity_type = "UserAssigned"
        user_identity_properties = UserIdentityProperties()
        user_assigned_identities = {user_assigned_identity_resource_id: user_identity_properties}

    identity_properties = IdentityProperties(type=resource_identity_type, user_assigned_identities=user_assigned_identities)

    export_pipeline = ExportPipeline(identity=identity_properties, target=export_pipeline_target_properties, options=options_list)

    poller = client.export_pipelines.begin_create(resource_group_name=resource_group_name, registry_name=registry_name, export_pipeline_name=export_pipeline_name, export_pipeline_create_parameters=export_pipeline)
    
    poll_output(poller)

    raw_result = client.export_pipelines.get(resource_group_name, registry_name, export_pipeline_name)

    print(raw_result)

def list_exportpipeline(cmd, client, resource_group_name, registry_name):
    raw_result = client.export_pipelines.list(resource_group_name, registry_name)

    for pipeline in raw_result:
        print(pipeline)

def delete_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    poller = client.export_pipelines.begin_delete(resource_group_name, registry_name, export_pipeline_name)

    poll_output(poller=poller)

def get_exportpipeline(cmd, client, resource_group_name, registry_name, export_pipeline_name):
    raw_result = client.export_pipelines.get(resource_group_name, registry_name, export_pipeline_name)

    print(raw_result)




        

    