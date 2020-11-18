from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import IdentityProperties, UserIdentityProperties
import json

def poll_output(poller, poll_interval=10):
    print("Operation Status: " + poller.status())
    while not poller.done():
        print("Please wait " + str(poll_interval) + " seconds for the next update.")
        poller.wait(timeout=poll_interval)
        print("Operation Status: " + poller.status())
    return poller.status()

def create_options_list (options, allowed_options_list): 
    options_list = options.split(',')

    if not set(options_list).issubset(set(allowed_options_list)):
        print("Allowed options are: ", end='')
        print(allowed_options_list)
        raise CLIError("Invalid option found in options parameter. Please provide a comma separated list of allowed options.")

    return options_list

def create_identity_properties(user_assigned_identity_resource_id):
    if user_assigned_identity_resource_id is None:
        resource_identity_type = "SystemAssigned"
        user_assigned_identities = None
    else:
        resource_identity_type = "UserAssigned"
        user_identity_properties = UserIdentityProperties()
        user_assigned_identities = {user_assigned_identity_resource_id: user_identity_properties}

    return IdentityProperties(type=resource_identity_type, user_assigned_identities=user_assigned_identities)

def keyvault_policy_output(keyvault_secret_uri, user_assigned_identity_resource_id, raw_result):
    keyvault_name = keyvault_secret_uri.split("https://")[1].split('.')[0]
    
    if user_assigned_identity_resource_id is not None:
        #if user ended resource id with a '/', remove it
        if user_assigned_identity_resource_id[-1] == '/':
            user_assigned_identity_resource_id = user_assigned_identity_resource_id[:-1]

        #account for ARM bug where the identity user assigned identities dict key resource id has lowercase resourcegroup rather than resourceGroup
        user_assigned_identity_resource_id_list = user_assigned_identity_resource_id.split("/")
        user_assigned_identity_resource_id_list[3] = "resourcegroups"
        user_assigned_identity_resource_id = '/'.join(user_assigned_identity_resource_id_list)

    identity_object_id = raw_result.identity.principal_id if user_assigned_identity_resource_id is None else raw_result.identity.user_assigned_identities[user_assigned_identity_resource_id].principal_id

    print("***YOU MUST RUN THE FOLLOWING COMMAND PRIOR TO ATTEMPTING A PIPELINERUN OR EXPECTING SOURCETRIGGER TO SUCCESSFULLY IMPORT IMAGES***")
    print(f'az keyvault set-policy --name {keyvault_name} --secret-permissions get --object-id {identity_object_id}')

def print_pipeline_output(obj):
    

    is_importpipeline = "importPipelines" in obj.id
    is_exportpipeline = "exportPipelines" in obj.id
    is_pipelinerun = "pipelineRuns" in obj.id

    if is_pipelinerun:
        pipelinerun_type = "import" if "importPipelines" in obj.request.pipeline_resource_id else "export"
    
    #unroll the obj
    obj= json.loads(json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o))))
    d = {} 
    d["name"] = obj["name"]
    d["status"] = obj["response"]["status"]
    d["pipeline_resource_id"] = obj["request"]["pipeline_resource_id"]
    d["imported_artifacts"] = obj["response"]["imported_artifacts"]
    d["progress_percentage"] = obj["response"]["progress"]["percentage"]
    d["start_time"] = obj["response"]["start_time"]
    d["finish_time"] = obj["response"]["finish_time"]
    d["catalog_digest"] = obj["response"]["catalog_digest"]
    d["pipeline_run_error_message"] = obj["response"]["pipeline_run_error_message"]




    print(json.dumps(d, indent=2))

    obj_str = json.dumps(obj, indent=2)
    obj_str = obj_str.replace('"additional_properties": {},', '')
    print('\n'.join([line for line in obj_str.split("\n") if line.strip()!='']))
    
    
    



