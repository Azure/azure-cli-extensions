# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def validate_env_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id

    if not namespace.env or not namespace.resource_group_name:
        return

    # Set environment type
    environment_type = None

    if namespace.__dict__.get("environment_type"):
        environment_type = namespace.environment_type

    if namespace.env:
        if "connectedEnvironments" in namespace.env:
            environment_type = "connected"
        if "managedEnvironments" in namespace.env:
            environment_type = "managed"
    if namespace.__dict__.get("custom_location") or namespace.__dict__.get("connected_cluster_id"):
        environment_type = "connected"
    # Validate resource id / format resource id
    if environment_type == "connected":
        if not is_valid_resource_id(namespace.env):
            namespace.env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.App',
                type='connectedEnvironments',
                name=namespace.env
            )
    elif environment_type == "managed":
        if not is_valid_resource_id(namespace.env):
            namespace.env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.App',
                type='managedEnvironments',
                name=namespace.env
            )