# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_aks_sreclaw._client_factory import cf_managed_clusters
from azure.cli.core.commands import CliCommandType
from knack.log import get_logger

logger = get_logger(__name__)


# pylint: disable=too-many-statements
def load_command_table(self, _):
    managed_clusters_sdk = CliCommandType(
        operations_tmpl="azext_aks_sreclaw.vendored_sdks.azure_mgmt_containerservice.2025_10_01."
        "operations._managed_clusters_operations#ManagedClustersOperations.{}",
        operation_group="managed_clusters",
        client_factory=cf_managed_clusters,
    )

    with self.command_group(
        "aks",
        managed_clusters_sdk,
        client_factory=cf_managed_clusters,

    ) as g:
        g.custom_command("claw create", "aks_sreclaw_create", supports_no_wait=True)
        g.custom_command("claw delete", "aks_sreclaw_delete", supports_no_wait=True)
        g.custom_command("claw connect", "aks_sreclaw_connect")
        g.custom_command("claw status", "aks_sreclaw_status")
