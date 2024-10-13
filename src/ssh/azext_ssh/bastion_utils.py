# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=protected-access

import threading
from azure.cli.core import azclierror
from knack.log import get_logger
from knack.prompting import prompt_y_n


from .aaz.latest.network.bastion import Create
from .vendored_sdks.resourcegraph._resource_graph_client import ResourceGraphClient
from . import resource_graph_utils
from . import ssh_utils

logger = get_logger(__name__)

# pylint: disable=too-few-public-methods


class BastionSku():
    Basic = "Basic"
    Standard = "Standard"
    Developer = "Developer"
    QuickConnect = "QuickConnect"
    ValidLocation = ["centraluseuap", "eastus2euap", "westus", "northeurope", "northcentralus", "westcentralus"]
    QuickStartLink = "https://learn.microsoft.com/azure/bastion/quickstart-developer-sku"
    ConfigLink = "https://learn.microsoft.com/azure/bastion/configuration-settings"
    TunnelPort = 0
    ResourcePort = 22


# ============================= Put Call to create a bastion Developer Sku============================= #
def create_bastion(cmd, op_info, vnet_id, vnet_name, bastion_resource_group):
    bastion_creator = Create(cli_ctx=cmd.cli_ctx)
    bastion_name = f"{vnet_name}-bastion"
    bastion_args = {
        "location": op_info.location,
        "name": bastion_name,
        "resource_group": bastion_resource_group,
        "sku": "Developer",
        "virtual_network": {
            "id": vnet_id
        },
        "ip_configurations": [],
        "scale_units": 2,
        "tags": {}
    }
    try:
        poller = bastion_creator(command_args=bastion_args)
        result = poller.result()
        if result:
            logger.warning("Bastion Host created successfully.")
            op_info.bastion_name = result.get("name", bastion_name)
            op_info.bastion_rsg = result.get("resourceGroup", bastion_resource_group)

    except Exception as e:
        raise azclierror.ClientRequestError(f"Failed to create bastion information: {e}") from e

# ================================ Get call for current bastion ====================================================#


def show_bastion(cmd, op_info):
    from .aaz.latest.network.bastion import Show
    try:
        bastion = Show(cli_ctx=cmd.cli_ctx)(command_args={
            "name": op_info.bastion_name,
            "resource_group": op_info.bastion_rsg,
        })
        return bastion

    except Exception as e:
        raise azclierror.CLIInternalError(
            "Fetching Error: Failed to get Bastion information."
            " Please try again later.", e
        ) from e

# ============================= SSH to Bastion Host Logic ============================= #


def ssh_bastion_host(cmd, op_info, delete_keys, delete_cert):

    bastion = show_bastion(cmd, op_info)

    if bastion['sku']['name'] != BastionSku.Developer:
        raise azclierror.InvalidArgumentValueError(
            "SSH to Bastion host via Az CLI/PowerShell is only supported for Developer."
        )

    port = BastionSku.ResourcePort
    target_resource_id = op_info.resource_id

    bastion_endpoint = _get_data_pod(cmd, port, target_resource_id, bastion)

    tunnel_server = _get_tunnel(cmd, bastion, bastion_endpoint, target_resource_id, port)

    t = threading.Thread(target=_start_tunnel, args=(tunnel_server,))
    t.daemon = True
    t.start()

    op_info.ssh_args.extend(
        [
            "-p", str(tunnel_server.local_port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "LogLevel=Error"
        ]
    )

    try:
        ssh_utils.start_ssh_connection(op_info, delete_keys, delete_cert)
    except Exception as ex:
        raise azclierror.CLIInternalError(ex) from ex
    finally:
        tunnel_server.cleanup()


def _get_data_pod(cmd, port, target_resource_id, bastion):
    from azure.cli.core._profile import Profile
    from azure.cli.core.util import should_disable_connection_verify
    import requests

    profile = Profile(cli_ctx=cmd.cli_ctx)
    auth_token, _, _ = profile.get_raw_token()
    content = {
        'resourceId': target_resource_id,
        'bastionResourceId': bastion['id'],
        'vmPort': str(port),
        'azToken': auth_token[1],
        'connectionType': 'nativeclient'
    }
    headers = {'Content-Type': 'application/json'}

    web_address = f"https://{bastion['dnsName']}/api/connection"
    response = requests.post(
        web_address, json=content, headers=headers, verify=not should_disable_connection_verify()
    )

    return response.content.decode("utf-8")


def validate_no_custome_port(op_info):
    if op_info.port is not None:
        raise azclierror.InvalidArgumentValueError("Custom Ports are not allowed for the Bastion Developer Sku.")
    op_info.port = None


# ============================= Tunnel Logic ============================= #
def _get_tunnel(cmd, bastion, bastion_endpoint, vm_id, resource_port):
    BASTION_EXTENSION_NAME = "bastion"
    BASTION_EXTENSION_MODULE = "azext_bastion.tunnel"
    azbastion = _get_azext_module(BASTION_EXTENSION_NAME, BASTION_EXTENSION_MODULE)

    # In the case we ever dont want to import the tunnel server
    port = BastionSku.TunnelPort
    # from .tunnel import TunnelServer
    # tunnel_server = TunnelServer(cmd.cli_ctx, "localhost", port, bastion, bastion_endpoint, vm_id, resource_port)

    # The zero is the port number which will be auto-selected from 1024-65535
    tunnel_server = azbastion.TunnelServer(
        cmd.cli_ctx, "localhost", port, bastion, bastion_endpoint, vm_id, resource_port
    )

    return tunnel_server


def _start_tunnel(tunnel_server):
    tunnel_server.start_server()


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
        raise azclierror.ClientRequestError(ie) from ie
# =============================  Bastion Parsing Logic  ============================= #


def handle_bastion_properties(cmd, op_info, nic):
    if not nic:
        raise azclierror.ClientRequestError("Error fetching the Network Interface of the specified Virtual Machine.")
    check_valid_developer_sku_location(nic, op_info.resource_type.lower(), op_info)

    op_info.resource_id = parse_resource_id(nic)

    vnet_id, vnet_name = parse_vnet(nic)
    nic_subscription_id, bastion_resource_group = parse_nic_rs_groupand_id(nic)
    query_response = _request_specified_bastion(cmd, nic_subscription_id, vnet_id)
    if query_response['count'] == 0:
        prompt = (
            f"There is currently no Bastion associated with this VNet."
            " Would you like to associate this VNet with Bastion Developer? To learn more,"
            f" please visit {BastionSku.QuickStartLink}"
        )
        if not prompt_y_n(prompt):
            raise azclierror.ClientRequestError("No Bastion Host found or created in the VNet.")
        create_bastion(cmd, op_info, vnet_id, vnet_name, bastion_resource_group)

    else:
        op_info.bastion_name = parse_bastion_name(query_response)
        op_info.bastion_rsg = bastion_resource_group


def check_valid_developer_sku_location(nic, resource_type, op_info):
    if resource_type.lower() == "microsoft.compute/virtualmachines":
        location = nic.get('location')
        op_info.location = location
        if location not in BastionSku.ValidLocation:
            raise azclierror.InvalidArgumentValueError(
                "The Bastion Developer SKU is not supported in the region of the target VM. "
                f"Learn more about Bastion Developer SKU at {BastionSku.ConfigLink}"
            )
    else:
        raise azclierror.InvalidArgumentValueError(
            "The Bastion Developer SKU is not supported for this type of resource."
        )


def parse_nic_rs_groupand_id(nic):
    try:
        resource_id = nic['id']
        parts = resource_id.split('/')
        subscription_id = parts[2]
        resource_group = parts[4]
    except Exception:
        raise azclierror.CLIInternalError(
            "Internal CLI Error: Failed to get subscription ID and resource group from Network Interface."
            "Please try again later."
        )
    return subscription_id, resource_group


def parse_vnet(nic_info):
    try:
        subnet_id = nic_info['ipConfigurations'][0]['subnet']['id']
        vnet_id = '/'.join(subnet_id.split('/')[:-2])
        return vnet_id, vnet_id.split('/')[-1]

    except Exception:
        raise azclierror.CLIInternalError("Internal CLI Error: Failed to get VNet information. Please try again later.")


def parse_bastion_name(bastion_data):
    try:
        data = bastion_data.get('data', [])
        if data and len(data) > 0:
            bastion_name = data[0].get('name')
            return bastion_name

        return None
    except Exception:
        raise azclierror.CLIInternalError(
            "Internal CLI Error: Failed to get Bastion information. Please try again later."
        )


def parse_resource_id(nic):
    try:
        vm_id = nic['virtualMachine']['id']
    except Exception:
        raise azclierror.CLIInternalError("Internal CLI Error: Failed to get resource ID. Please try again later.")
    return vm_id

# ============================= Bastion Request Logic ============================= #


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


def _request_specified_bastion(cmd, subscription_id, vnet_id):
    from azure.cli.core._profile import Profile

    # Initialize Resource Graph client for Azure queries specfically for Vnet -> Bastion relationship:
    # This block dynamically loads the 'resource-graph' extension modules
    # necessary for accessing the Azure Resource Graph. It then:
    # 1. Retrieves the current user's Azure Active Directory access token from the CLI context.
    # 2. Initializes the AccessTokenCredential with the retrieved token.
    # 3. Creates an instance of the ResourceGraphClient using the authenticated credentials.
    # The resulting client can then be used to perform resource queries across multiple Azure subscriptions,
    # leveraging the Resource Graph extension to fetch detailed information the queried resource.

    try:
        access_token = Profile(cli_ctx=cmd.cli_ctx).get_raw_token()[0][2].get("accessToken")
        credentials = AccessTokenCredential(access_token)
        client = ResourceGraphClient(credentials, subscription_id)

    except Exception:
        raise azclierror.ClientRequestError(
            "Failed to get access token. Ensure you are currently logged in using az login."
        )
    query = f"""
    Resources
    | where type =~ 'Microsoft.Network/bastionHosts'
    and (properties.ipConfigurations[0].properties.subnet.id startswith '{vnet_id}/'
    or properties.virtualNetwork.id =~ '{vnet_id}')
    | project id, location, name, sku, properties, type, vnetid = '{vnet_id}'
    | union (
        Resources
        | where id =~ '{vnet_id}'
        | where type =~ 'Microsoft.Network/virtualNetworks' and id contains '/virtualNetworks/{vnet_id}'
        | mv-expand peering=properties.virtualNetworkPeerings limit 400
        | project vnetid = tolower(tostring(peering.properties.remoteVirtualNetwork.id))
        | join kind=inner (
            Resources
            | where type =~ 'Microsoft.Network/bastionHosts'
            | extend vnetid=tolower(extract('(.*/virtualnetworks/[^/]+)/', 1, tolower(tostring(properties.ipConfigurations[0].properties.subnet.id))))
        ) on vnetid
    )
    """

    try:
        response = resource_graph_utils.execute_query(client, query, 10, 0, None, None, False, None)
    except Exception:
        raise azclierror.ClientRequestError(
            "Failed to find Bastion assocaited to VNet in the specified subscription."
            " Ensure the Bastion is not in a different subscription or resource group."
        )

    return response
