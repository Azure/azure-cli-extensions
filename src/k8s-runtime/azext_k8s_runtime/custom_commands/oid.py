# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

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
