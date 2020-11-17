from knack.util import CLIError
from .vendored_sdks.containerregistry.v2019_12_01_preview.models._models_py3 import IdentityProperties, UserIdentityProperties

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

def keyvault_policy_output(client, keyvault_secret_uri, user_assigned_identity_resource_id, raw_result):
    keyvault_name = keyvault_secret_uri.split("https://")[1].split('.')[0]
    
    #account for ARM bug where the identity user assigned identities dict key resource id has lowercase resourcegroup rather than resourceGroup
    if user_assigned_identity_resource_id is not None:
        user_assigned_identity_resource_id_list = user_assigned_identity_resource_id.split("/")
        user_assigned_identity_resource_id_list[3] = "resourcegroups"
        user_assigned_identity_resource_id = '/'.join(user_assigned_identity_resource_id_list)

    identity_object_id = raw_result.identity.principal_id if user_assigned_identity_resource_id is None else raw_result.identity.user_assigned_identities[user_assigned_identity_resource_id].principal_id

    print("***YOU MUST RUN THE FOLLOWING COMMAND PRIOR TO ATTEMPTING A PIPELINERUN OR EXPECTING SOURCETRIGGER TO SUCCESSFULLY IMPORT IMAGES***")
    print(f'az keyvault set-policy --name {keyvault_name} --secret-permissions get --object-id {identity_object_id}')
