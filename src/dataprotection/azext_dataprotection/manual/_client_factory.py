# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_resource_graph_client(cli_ctx, _):
    from azext_dataprotection.vendored_sdks.resourcegraph import ResourceGraphClient
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx,
                                   ResourceGraphClient, subscription_bound=False)
