# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from unicodedata import name
from azure.cli.core.azclierror import (ValidationError, RequiredArgumentMissingError)


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def validate_memory(namespace):
    memory = namespace.memory

    if memory is not None:
        valid = False

        if memory.endswith("Gi"):
            valid = _is_number(memory[:-2])

        if not valid:
            raise ValidationError("Usage error: --memory must be a number ending with \"Gi\"")

def validate_cpu(namespace):
    if namespace.cpu:
        cpu = namespace.cpu
        try:
            float(cpu)
        except ValueError:
            raise ValidationError("Usage error: --cpu must be a number eg. \"0.5\"")

def validate_managed_env_name_or_id(cmd, namespace):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from msrestazure.tools import is_valid_resource_id, resource_id

    if namespace.managed_env:
        if not is_valid_resource_id(namespace.managed_env):
            namespace.managed_env = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.App',
                type='managedEnvironments',
                name=namespace.managed_env
            )

def validate_registry_server(namespace):
    if "create" in namespace.command.lower():
        if namespace.registry_server:
            if not namespace.registry_user or not namespace.registry_pass:
                if ".azurecr.io" not in namespace.registry_server:
                    raise ValidationError("Usage error: --registry-server, --registry-password and --registry-username are required together if not using Azure Container Registry")

def validate_registry_user(namespace):
    if "create" in namespace.command.lower():
        if namespace.registry_user:
            if not namespace.registry_server or (not namespace.registry_pass and ".azurecr.io" not in namespace.registry_server):
                raise ValidationError("Usage error: --registry-server, --registry-password and --registry-username are required together if not using Azure Container Registry")

def validate_registry_pass(namespace):
    if "create" in namespace.command.lower():
        if namespace.registry_pass:
            if not namespace.registry_server or (not namespace.registry_user and ".azurecr.io" not in namespace.registry_server):
                raise ValidationError("Usage error: --registry-server, --registry-password and --registry-username are required together if not using Azure Container Registry")

def validate_target_port(namespace):
    if "create" in namespace.command.lower():
        if namespace.target_port:
            if not namespace.ingress:
                raise ValidationError("Usage error: must specify --ingress with --target-port")

def validate_ingress(namespace):
    if "create" in namespace.command.lower():
        if namespace.ingress:
            if not namespace.target_port:
                raise ValidationError("Usage error: must specify --target-port with --ingress")
