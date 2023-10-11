# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import UnknownError
from azure.cli.command_modules.resource.custom import register_provider
from azure.cli.command_modules.acs._roleassignments import (
    add_role_assignment,
    build_role_scope,
    delete_role_assignments,
)
from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_K8S_EXTENSION_NAME,
    CONST_STORAGE_POOL_NAME_PREFIX,
    CONST_STORAGE_POOL_RANDOM_LENGTH,
)
import random
import string


def _register_dependent_rps(cmd):
    register_provider(cmd, 'Microsoft.Kubernetes', wait=True)
    register_provider(cmd, 'Microsoft.KubernetesConfiguration', wait=True)
    register_provider(cmd, 'Microsoft.ExtendedLocation', wait=True)


def _perform_role_operations_on_managed_rg(cmd, subscription_id, node_resource_group, kubelet_identity_object_id, assign):
    managed_rg_role_scope = build_role_scope(node_resource_group, None, subscription_id)
    roles = ["Reader", "Network Contributor", "Elastic SAN Owner", "Elastic SAN Volume Group Owner"]

    for role in roles:
        if assign:
            add_role_assignment(
                cmd,
                role,
                kubelet_identity_object_id,
                scope=managed_rg_role_scope,
            )
        else:
            # NOTE: delete_role_assignments accepts cli_ctx
            # instead of cmd unlike add_role_assignment.
            delete_role_assignments(
                cmd.cli_ctx,
                role,
                kubelet_identity_object_id,
                scope=managed_rg_role_scope,
            )


def _generate_random_storage_pool_name():
    random_name = CONST_STORAGE_POOL_NAME_PREFIX + ''.join(random.choices(string.ascii_lowercase, k=CONST_STORAGE_POOL_RANDOM_LENGTH))
    return random_name


def _get_k8s_extension_module(module_name):
    try:
        # adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(CONST_K8S_EXTENSION_NAME)
        # import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError as ie:
        raise UnknownError(
            "Please add CLI extension `k8s-extension` for performing Azure Container Storage operations.\n"
            "Run command `az extension --name k8s-extension`"
        )
