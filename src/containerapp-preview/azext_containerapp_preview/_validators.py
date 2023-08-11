# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ._constants import (MANAGED_ENVIRONMENT_TYPE,
                         CONNECTED_ENVIRONMENT_TYPE,
                         MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                         CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                         CONTAINER_APPS_RP)


def validate_env_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id, parse_resource_id

    if not namespace.managed_env or not namespace.resource_group_name:
        return

    # Set environment type
    environment_type = None

    if namespace.__dict__.get("environment_type"):
        environment_type = namespace.environment_type

    if namespace.managed_env:
        if is_valid_resource_id(namespace.managed_env):
            env_dict = parse_resource_id(namespace.managed_env)
            resource_type = env_dict.get("resource_type")
            if resource_type:
                if CONNECTED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                    environment_type = CONNECTED_ENVIRONMENT_TYPE
                if MANAGED_ENVIRONMENT_RESOURCE_TYPE.lower() == resource_type.lower():
                    environment_type = MANAGED_ENVIRONMENT_TYPE
    # Validate resource id / format resource id
    if environment_type == CONNECTED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=CONNECTED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.managed_env
            )
    elif environment_type == MANAGED_ENVIRONMENT_TYPE:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace=CONTAINER_APPS_RP,
                type=MANAGED_ENVIRONMENT_RESOURCE_TYPE,
                name=namespace.managed_env
            )
