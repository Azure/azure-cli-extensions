# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import InvalidArgumentValueError, ResourceNotFoundError
from azext_aks_preview._consts import (
    CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME,
    CONST_K8S_EXTENSION_CUSTOM_MOD_NAME,
)
from azext_aks_preview._helpers import get_k8s_extension_module
from azext_aks_preview.azuremanagedlustre._consts import (
    CONST_AML_EXT_INSTALLATION_NAME,
    CONST_AML_K8S_EXTENSION_NAME,
)


def get_azure_managed_lustre_extension_client(cmd):
    client_factory = get_k8s_extension_module(CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME)
    custom_module = get_k8s_extension_module(CONST_K8S_EXTENSION_CUSTOM_MOD_NAME)
    return client_factory.cf_k8s_extension_operation(cmd.cli_ctx), custom_module


def check_if_extension_is_installed(cmd, resource_group, cluster_name):
    client, custom_module = get_azure_managed_lustre_extension_client(cmd)
    try:
        extension = custom_module.show_k8s_extension(
            client, resource_group, cluster_name, CONST_AML_EXT_INSTALLATION_NAME, "managedClusters"
        )
    except ResourceNotFoundError:
        return False

    if extension.extension_type.lower() != CONST_AML_K8S_EXTENSION_NAME:
        raise InvalidArgumentValueError(
            f"The extension '{CONST_AML_EXT_INSTALLATION_NAME}' already exists with type "
            f"'{extension.extension_type}', not '{CONST_AML_K8S_EXTENSION_NAME}'."
        )
    return True
