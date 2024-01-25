# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from dataclasses import dataclass
from knack.log import get_logger

from azure.cli.core.commands import AzCliCommand
from azure.cli.command_modules.role import graph_client_factory


logger = get_logger(__name__)

KUBERNETES_RUNTIME_RP = "Microsoft.KubernetesRuntime"
KUBERNETES_RUNTIME_FPA_APP_ID = "087fca6e-4606-4d41-b3f6-5ebdf75b8b4c"


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
