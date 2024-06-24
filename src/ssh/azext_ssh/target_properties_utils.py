# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import colorama

from azure.cli.core import telemetry
from azure.cli.core import azclierror 
from knack import log
from . import constants as const
from . import bastion_utils




logger = log.get_logger(__name__)


# Send target OS type telemetry and check if authentication options are valid for that OS.
def handle_target_machine_properties(cmd, op_info):

    properties = get_properties(cmd, op_info.resource_type.lower(), op_info.resource_group_name, op_info.vm_name)
    if properties:
        os_type = parse_os_type(properties, op_info.resource_type.lower())
        agent_version = parse_agent_version(properties, op_info.resource_type.lower())
        if op_info.bastion:
            handle_bastion_properties(cmd, op_info, properties)
    else:
        os_type, agent_version = None, None
    check_valid_os_type(os_type, op_info)
    check_valid_agent_version(agent_version, op_info)
    return

def handle_bastion_properties(cmd, op_info, properties):
    check_valid_developer_sku_location(properties, op_info.resource_type.lower(), op_info)

    op_info.resource_id = parse_resource_id(properties)
    subscription_id = parse_subscription_id(properties)
    nic_name = parse_nic_name(properties)

    nic_info = _request_vm_network_interface_card(cmd, op_info.resource_group_name, nic_name)

    vnet_id, vnet_name= parse_vnet(nic_info)

    bastion = _request_specified_bastion(cmd, subscription_id, vnet_name, op_info.resource_group_name)
    if bastion['count'] == 0:
        print("No Bastion found in the same VNet. Creating a new Bastion Host.")
        bastion = bastion_utils.create_bastion(cmd, op_info, vnet_id)
    else:
        op_info.bastion_name = parse_bastion_name(bastion)
  
def get_properties(cmd, resource_type, resource_group_name, vm_name):
    if resource_type == "microsoft.compute/virtualmachines":
        return _request_azure_vm_properties(cmd, resource_group_name, vm_name)
    if resource_type == "microsoft.hybridcompute/machines":
        return _request_arc_server_properties(cmd, resource_group_name, vm_name)
    if resource_type == "microsoft.connectedvmwarevsphere/virtualmachines":
        return _request_connected_vmware_properties(cmd, resource_group_name, vm_name)


# This function is used to get the properties needed from an Azure VM
def _request_azure_vm_properties(cmd, resource_group_name, vm_name):
    from azure.cli.core.commands import client_factory
    from azure.cli.core import profiles
    # pylint: disable=broad-except
    try:
        # Retrieves the VM object \\
        compute_client = client_factory.get_mgmt_service_client(cmd.cli_ctx, profiles.ResourceType.MGMT_COMPUTE)
        return compute_client.virtual_machines.get(resource_group_name, vm_name)
    except Exception:
        return None


# This function is used to get the properties needed needed from an Azure Arc Server
def _request_arc_server_properties(cmd, resource_group_name, vm_name):
    from .aaz.latest.hybrid_compute.machine import Show as ArcServerShow
    # pylint: disable=broad-except
    try:
        get_args = {'resource_group': resource_group_name, 'machine_name': vm_name}
        # Retrieves the Arc Server object
        return ArcServerShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return None


# This function is used to get the properties needed from a Connected VMware VM
def _request_connected_vmware_properties(cmd, resource_group_name, vm_name):
    from .aaz.latest.connected_v_mwarev_sphere.virtual_machine import Show as VMwarevSphereShow

    # pylint: disable=broad-except
    try:
        get_args = {'resource_group': resource_group_name, 'machine_name': vm_name}
        # Retrieves the Connected VMware VM object
        return VMwarevSphereShow(cli_ctx=cmd.cli_ctx)(command_args=get_args)
    except Exception:
        return None
    
def _request_vm_network_interface_card(cmd, resource_group, nic_name):
    from .aaz.latest.network.nic import Show
    try:
        nic = Show(cli_ctx=cmd.cli_ctx)(command_args={
                "resource_group": resource_group,
                "name": nic_name
            })
        return nic
    except Exception:
        raise azclierror.ClientRequestError("Failed to get VM's NIC information. Please try again later.")


def parse_os_type(properties, resource_type):
    if resource_type == "microsoft.compute/virtualmachines":
        if (properties.storage_profile and properties.storage_profile.os_disk and
                properties.storage_profile.os_disk.os_type):

            return properties.storage_profile.os_disk.os_type

    elif resource_type == "microsoft.hybridcompute/machines":
        if properties.get('osName', None):
            return properties.get('osName')
        if properties.get('properties', None):
            return properties.get('properties').get('osType', None)

    elif resource_type == "microsoft.connectedvmwarevsphere/virtualmachines":
        if properties.get("osProfile") and properties.get("osProfile").get("osType"):
            return properties.get("osProfile").get("osType")


def parse_agent_version(properties, resource_type):
    if resource_type == "microsoft.compute/virtualmachines":
        return None

    if resource_type == "microsoft.hybridcompute/machines":
        if properties.get('properties'):
            return properties.get('properties').get('agentVersion')

    if resource_type == "microsoft.connectedvmwarevsphere/virtualmachines":
        if properties.get("properties") and properties.get("properties").get('guestAgentProfile') and\
                properties.get("properties").get('guestAgentProfile').get('agentVersion'):

            return properties.get("properties").get('guestAgentProfile').get('agentVersion')

def parse_resource_id(properties):
        return properties.id

    
def parse_nic_name(properties):
    try:
        nic_id = properties.network_profile.network_interfaces[0].id
        nic_name = nic_id.split('/')[-1]
        return nic_name
    except Exception as e:
        print(e)
        return None
    
def parse_vnet(nic_info):
    try:
        subnet_id = nic_info['ipConfigurations'][0]['subnet']['id']
        vnet_id = '/'.join(subnet_id.split('/')[:-2])

        return vnet_id, vnet_id.split('/')[-1]

    except (IndexError, KeyError, TypeError) as e:
        print("Error:", e)
        return None
    
def parse_subscription_id(properties):
    try:
        properties_id = properties.id
        return properties_id.split('/')[2]
    except KeyError:
        return None
    
def parse_bastion_name(bastion_data):
    try:
        data = bastion_data.get('data', [])
        if data and len(data) > 0:
            bastion_name = data[0].get('name')
            return bastion_name
        else:
            return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing Bastion name: {e}")
        return None


# This function is used to check if the OS type is valid and if the authentication options are valid for that OS
def check_valid_os_type(os_type, op_info):
    if os_type:
        logger.debug("Target OS Type: %s", os_type)
        telemetry.add_extension_event('ssh', {'Context.Default.AzureCLI.TargetOSType': os_type})

    if os_type and os_type.lower() == 'windows' and not op_info.local_user:
        colorama.init()
        error_message = "SSH Login using AAD credentials is not currently supported for Windows."
        recommendation = colorama.Fore.YELLOW + "Please provide --local-user." + colorama.Style.RESET_ALL
        raise azclierror.RequiredArgumentMissingError(error_message, recommendation)


def check_valid_agent_version(agent_version, op_info):
    # pylint: disable=broad-except
    if op_info.is_arc() and agent_version:
        try:
            major, minor, _, _ = agent_version.split('.', 4)
            if int(major) < const.AGENT_MINIMUM_VERSION_MAJOR or int(minor) < const.AGENT_MINIMUM_VERSION_MINOR:
                logger.warning("The version of the Arc Agent, %s running on the target machine "
                               "is not compatible with this version of the ssh extension. "
                               "Please update to the latest version.", agent_version)
        except Exception:
            return
        
def check_valid_developer_sku_location(properties, resource_type, op_info):
    if resource_type == "microsoft.compute/virtualmachines":
        location = properties.location
        op_info.location = location
        if location not in ["centralus", "eastus2", "westus", "northeurope", "northcentralus", "westcentralus"]:
            raise azclierror.InvalidArgumentValueError("The Bastion Developer SKU is not supported in the region of the target VM.")
    else:
        raise azclierror.InvalidArgumentValueError("The Bastion Developer SKU is not supported for this type of resource.")
    

def _get_azext_module(extension_name, module_name):
    try:
        # adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(extension_name)
        # import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError as ie:
        raise CLIInternalError(ie) from ie


class AccessTokenCredential:  # pylint: disable=too-few-public-methods
    """Simple access token authentication. Return the access token as-is.
    """
    def __init__(self, access_token):
        self.access_token = access_token

    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        import time
        from azure.cli.core.auth.util import AccessToken
        # Assume the access token expires in 1 year / 31536000 seconds
        return AccessToken(self.access_token, int(time.time()) + 31536000)
    
def _request_specified_bastion(cmd, subscription_id, vnet_id, resource_group):
    from azure.cli.core._profile import Profile

    RESOURCE_GRAPH_EXTENSION_NAME = 'resource-graph'
    RG_EXTENSION_MODULE = 'azext_resourcegraph.custom'
    RG_SDK_MODULE = 'azext_resourcegraph.vendored_sdks.resourcegraph._resource_graph_client'

    RG_custom = _get_azext_module(RESOURCE_GRAPH_EXTENSION_NAME, RG_EXTENSION_MODULE)
    RG_client = _get_azext_module(RESOURCE_GRAPH_EXTENSION_NAME, RG_SDK_MODULE)

    try:
        access_token = Profile(cli_ctx=cmd.cli_ctx).get_raw_token()[0][2].get("accessToken")
        credentials = AccessTokenCredential(access_token)
        client = RG_client.ResourceGraphClient(credentials, subscription_id)

    except Exception:
        raise azclierror.ClientRequestError(f"Failed to get access token. Make sure you are logged in.")
    query = f"""
    Resources
    | where type =~ 'Microsoft.Network/bastionHosts' and 
      (properties.ipConfigurations[0].properties.subnet.id startswith '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{vnet_id}/' or 
       properties.virtualNetwork.id =~ '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{vnet_id}')
    | project id, location, name, sku, properties, type, vnetid = '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{vnet_id}'
    | union (
        Resources 
        | where id =~ '/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{vnet_id}'
        | mv-expand peering=properties.virtualNetworkPeerings limit 400
        | project vnetid = tolower(tostring(peering.properties.remoteVirtualNetwork.id))
        | join kind=inner (
            Resources 
            | where type =~ 'microsoft.network/bastionHosts'
            | extend vnetid=tolower(extract('(.*/virtualnetworks/[^/]+)/', 1, tolower(tostring(properties.ipConfigurations[0].properties.subnet.id))))
        ) on vnetid
    )
    """
    try: 
        response = RG_custom.execute_query(client, query, 10, 0, None, None, False, None)

    except Exception:
        raise azclierror.ClientRequestError(f"Failed to get Bastion information. Please try again later.")
    
    return response

