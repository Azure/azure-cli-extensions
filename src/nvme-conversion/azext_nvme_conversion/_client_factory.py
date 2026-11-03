# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Client factory for Azure Compute Management SDK."""


def cf_compute(cli_ctx, **_):
    """Create a ComputeManagementClient from the CLI context."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.compute import ComputeManagementClient
    return get_mgmt_service_client(cli_ctx, ComputeManagementClient)
