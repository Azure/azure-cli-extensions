# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_connectedmachine(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_connectedmachine.vendored_sdks import HybridComputeManagementClient
    return get_mgmt_service_client(cli_ctx, HybridComputeManagementClient)
