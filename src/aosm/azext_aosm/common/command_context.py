# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from dataclasses import dataclass, field
from azure.cli.core import AzCli
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.mgmt.resource import ResourceManagementClient

from azext_aosm.vendored_sdks import HybridNetworkManagementClient


@dataclass
class CommandContext:
    cli_ctx: AzCli
    cli_options: dict = field(default_factory=dict)

    def __post_init__(self):
        self.aosm_client: HybridNetworkManagementClient = get_mgmt_service_client(
            self.cli_ctx, HybridNetworkManagementClient, base_url_bound=False
        )
        self.resources_client: ResourceManagementClient = get_mgmt_service_client(
            self.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES
        )
