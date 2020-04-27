# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from msrestazure.tools import is_valid_resource_id, parse_resource_id
from knack.util import CLIError
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.cli.core.commands.client_factory import get_mgmt_service_client


def validate_workspace_resource_id(cmd, namespace):
    if namespace.workspace_resource_id:
        if not is_valid_resource_id(namespace.workspace_resource_id):
            raise CLIError('usage error: --workspace-resource-id is invalid')

        # Determine whether the workspace already exists
        workspace_param = parse_resource_id(namespace.workspace_resource_id)
        workspaces_client = get_mgmt_service_client(cmd.cli_ctx, LogAnalyticsManagementClient).workspaces
        workspaces = workspaces_client.get(workspace_param['resource_group'], workspace_param['resource_name'])

        if workspaces and namespace.location:
            if workspaces.location != namespace.location:
                raise CLIError('usage error: workspace and solution must be under the same location')

    if namespace.workspace_resource_id is None and namespace.workspace_name is None:
        raise CLIError('usage error: please specify only one of --workspace-resource-id and --workspace-name')

    if namespace.workspace_resource_id and namespace.workspace_name:
        raise CLIError('usage error: please specify only one of --workspace-resource-id and --workspace-name, not both')
