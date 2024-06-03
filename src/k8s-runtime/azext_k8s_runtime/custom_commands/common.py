# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from dataclasses import dataclass
from knack.log import get_logger

from azure.cli.core.commands import AzCliCommand
from azure.mgmt.resource import ResourceManagementClient
from azure.cli.command_modules.role import graph_client_factory
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.graphrbac import GraphRbacManagementClient
from azure.cli.core._profile import Profile

logger = get_logger(__name__)

KUBERNETES_RUNTIME_RP = "Microsoft.KubernetesRuntime"
KUBERNETES_RUNTIME_FPA_APP_ID = "087fca6e-4606-4d41-b3f6-5ebdf75b8b4c"
AZURE_ROLE_CONTRIBUTOR = "b24988ac-6180-42a0-ab88-20f7382dd24c"
AZURE_ROLE_OWNER = "8e3af657-a8ff-443c-a75c-2fe8c4bcb635"
AUTHOTIZATION_RP = "Microsoft.Authorization"


def query_rp_oid(cmd: AzCliCommand):
    """
    Query the Kubernetes Runtime RP SP's object id in customer tenant


    """
    graph_client = graph_client_factory(cmd.cli_ctx)

    resp = graph_client.service_principal_list(filter=f"appId eq '{KUBERNETES_RUNTIME_FPA_APP_ID}'")

    if len(resp) == 0:
        raise RuntimeError("No Kubernetes Runtime RP SP found" +
                           f"Please check if {KUBERNETES_RUNTIME_RP} has been registered in your subscription.")
    if len(resp) > 1:
        raise RuntimeError("Found more than one Kubernetes Runtime RP. Please contact Azure support.")

    return resp[0]["id"]


def check_rp_registration(cmd: AzCliCommand, resource_id: str):
    """
    Check if RP is registered.
    1. If RP registered, then return.
    2. If RP is not registered, check permissions. If user has owner/contributor role definition, then register RP. Otherwise, return error message saying you need to ask for help to register RP.


    """
    resource_management_client: ResourceManagementClient = get_mgmt_service_client(cmd.cli_ctx, ResourceManagementClient, subscription_id=resource_id.subscription_id)
    resource_provider = resource_management_client.providers.get(KUBERNETES_RUNTIME_RP)
    if resource_provider.registration_state == "Registered":
        print(f"Kubernetes Runtime RP has been registered in subscription {resource_id.subscription_id}...")
        return

    print(f"Registering Kubernetes Runtime RP in subscription {resource_id.subscription_id}...")
    profile = Profile(cli_ctx=cmd.cli_ctx)
    cred, _, tenant_id = profile.get_login_credentials(resource=cmd.cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    graph_rbac_management_client = GraphRbacManagementClient(cred, tenant_id, base_url=cmd.cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
    current_user = graph_rbac_management_client.signed_in_user.get()

    authorization_management_client: AuthorizationManagementClient = get_mgmt_service_client(cmd.cli_ctx, AuthorizationManagementClient, subscription_id=resource_id.subscription_id)
    role_assignments = authorization_management_client.role_assignments.list_for_subscription(filter=f"atScope() and assignedTo('{current_user.object_id}')")
    role_definition_id_prefix = f"/subscriptions/{resource_id.subscription_id}/providers/{AUTHOTIZATION_RP}/roleDefinitions/"
    for role_assignment in role_assignments:
        if role_assignment.role_definition_id == role_definition_id_prefix + AZURE_ROLE_CONTRIBUTOR or role_assignment.role_definition_id == role_definition_id_prefix + AZURE_ROLE_OWNER:
            resource_management_client.providers.register(
                resource_provider_namespace=KUBERNETES_RUNTIME_RP
            )
            print("Kubernetes Runtime RP has been registered successfully.")
            return

    raise RuntimeError("Failed to register Kubernetes Runtime RP. You need to contact subscription contributor or owner to register it.")


class InvalidResourceUriException(Exception):
    def __init__(self):
        super().__init__("Resource uri must reference a Microsoft.Kubernetes/connectedClusters resource.")


def _compare_caseless(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()


@dataclass
class ConnectedClusterResourceId:
    subscription_id: str
    resource_group: str
    cluster_name: str

    @staticmethod
    def parse(resource_uri: str) -> "ConnectedClusterResourceId":
        if not resource_uri.startswith("/"):
            resource_uri = "/" + resource_uri
        parts = resource_uri.split("/")

        if len(parts) != 9:
            raise InvalidResourceUriException()

        if not (_compare_caseless(parts[1], "subscriptions") and _compare_caseless(parts[3], "resourceGroups") and _compare_caseless(parts[5], "providers") and _compare_caseless(parts[6], "Microsoft.Kubernetes") and _compare_caseless(parts[7], "connectedClusters")):
            raise InvalidResourceUriException()

        return ConnectedClusterResourceId(
            subscription_id=parts[2],
            resource_group=parts[4],
            cluster_name=parts[8]
        )

    @property
    def resource_uri(self) -> str:
        return f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.Kubernetes/connectedClusters/{self.cluster_name}"
