# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from msrestazure.tools import is_valid_resource_id, parse_resource_id, resource_id
from knack.util import CLIError
from azure.mgmt.loganalytics import LogAnalyticsManagementClient
from azure.cli.core.commands.client_factory import get_mgmt_service_client, get_subscription_id


def validate_workspace_resource_id(cmd, namespace):

    if namespace.workspace_resource_id:
        # If the workspace_resource_id is invalid, use it as a workspace name to splice the workspace_resource_id
        if not is_valid_resource_id(namespace.workspace_resource_id):
            namespace.workspace_resource_id = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='microsoft.OperationalInsights',
                type='workspaces',
                name=namespace.workspace_resource_id
            )

        if not is_valid_resource_id(namespace.workspace_resource_id):
            raise CLIError('usage error: --workspace is invalid, it must be name of resource id of workspace')

        # Determine whether the workspace already exists
        workspace_param = parse_resource_id(namespace.workspace_resource_id)
        if workspace_param['resource_group'] != namespace.resource_group_name:
            raise CLIError('usage error: workspace and solution must be under the same resource group')

        workspaces_client = get_mgmt_service_client(cmd.cli_ctx, LogAnalyticsManagementClient).workspaces
        workspaces = workspaces_client.get(workspace_param['resource_group'], workspace_param['resource_name'])

        # The location of solution is the same as the location of the workspace
        namespace.location = workspaces.location

        namespace.solution_name = namespace.solution_type + "(" + workspace_param['resource_name'] + ")"
