# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
from datetime import datetime

from azext_aks_preview._client_factory import get_providers_client_factory
from azext_aks_preview.azurecontainerstorage._consts import (
    CONST_ACSTOR_K8S_EXTENSION_NAME,
    CONST_EXT_INSTALLATION_NAME,
    CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME,
    CONST_K8S_EXTENSION_CUSTOM_MOD_NAME,
    CONST_K8S_EXTENSION_NAME,
    CONST_STORAGE_POOL_OPTION_NVME,
    CONST_STORAGE_POOL_TYPE_ELASTIC_SAN,
    CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK,
    RP_REGISTRATION_POLLING_INTERVAL_IN_SEC,
)
from azure.cli.command_modules.acs._roleassignments import (
    add_role_assignment,
    build_role_scope,
    delete_role_assignments,
)
from azure.cli.core.azclierror import UnknownError
from knack.log import get_logger

logger = get_logger(__name__)


def register_dependent_rps(cmd, subscription_id) -> bool:
    required_rp = 'Microsoft.KubernetesConfiguration'
    from azure.mgmt.resource.resources.models import (
        ProviderConsentDefinition, ProviderRegistrationRequest)

    properties = ProviderRegistrationRequest(
        third_party_provider_consent=ProviderConsentDefinition(
            consent_to_authorization=False
        )
    )
    client = get_providers_client_factory(cmd.cli_ctx)
    is_registered = False
    try:
        is_registered = _is_rp_registered(cmd, required_rp, subscription_id)
        if is_registered:
            return True
        client.register(required_rp, properties=properties)
        # wait for registration to finish
        timeout_secs = 120
        start = datetime.utcnow()
        is_registered = _is_rp_registered(cmd, required_rp, subscription_id)
        while not is_registered:
            is_registered = _is_rp_registered(cmd, required_rp, subscription_id)
            time.sleep(RP_REGISTRATION_POLLING_INTERVAL_IN_SEC)
            if (datetime.utcnow() - start).seconds >= timeout_secs:
                logger.error(
                    "Timed out while waiting for the %s resource provider to be registered.", required_rp
                )
                break

    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "Installation of Azure Container Storage requires registering to the following resource provider: %s. "
            "We were unable to perform the registration on your behalf due to the following error: %s\n"
            "Please check with your admin on permissions, or try running registration manually with: "
            "`az provider register --namespace %s` command.", required_rp, e, required_rp
        )

    return is_registered


def should_create_storagepool(
    cmd,
    subscription_id,
    node_resource_group,
    kubelet_identity_object_id,
    storage_pool_type,
    storage_pool_option,
    agentpool_details,
    nodepool_name,
):
    role_assignment_success = perform_role_operations_on_managed_rg(
        cmd,
        subscription_id,
        node_resource_group,
        kubelet_identity_object_id,
        True
    )
    return_val = True

    if not role_assignment_success:
        msg = "\nUnable to add Role Assignments needed for Elastic SAN storagepools to be functional. " \
            "Please check with your admin on permissions."
        if storage_pool_type == CONST_STORAGE_POOL_TYPE_ELASTIC_SAN:
            msg += "\nThis command will not create an Elastic SAN storagepool after installation."
            return_val = False
        msg += "\nGoing ahead with the installation of Azure Container Storage..."
        logger.warning(msg)

    if not return_val:
        return return_val

    if storage_pool_type == CONST_STORAGE_POOL_TYPE_EPHEMERAL_DISK and \
       storage_pool_option == CONST_STORAGE_POOL_OPTION_NVME:
        nodepool_list = nodepool_name.split(',')
        for nodepool in nodepool_list:
            agentpool_vm = agentpool_details.get(nodepool.lower())
            if agentpool_vm is not None and agentpool_vm.lower().startswith('standard_l'):
                break
        else:
            logger.warning(
                "\nNo supporting nodepool found which can support ephemeral NVMe disk "
                "so this command will not create an ephemeral NVMe disk storage pool after installation."
                "\nGoing ahead with the installation of Azure Container Storage..."
            )
            return_val = False

    return return_val


def perform_role_operations_on_managed_rg(
    cmd,
    subscription_id,
    node_resource_group,
    kubelet_identity_object_id,
    assign
):
    managed_rg_role_scope = build_role_scope(node_resource_group, None, subscription_id)
    roles = ["Reader", "Network Contributor", "Elastic SAN Owner", "Elastic SAN Volume Group Owner"]
    result = True

    for role in roles:
        try:
            if assign:
                result = add_role_assignment(
                    cmd,
                    role,
                    kubelet_identity_object_id,
                    scope=managed_rg_role_scope,
                    delay=0,
                )
            else:
                # NOTE: delete_role_assignments accepts cli_ctx
                # instead of cmd unlike add_role_assignment.
                result = delete_role_assignments(
                    cmd.cli_ctx,
                    role,
                    kubelet_identity_object_id,
                    scope=managed_rg_role_scope,
                    delay=0,
                )

            if not result:
                break
        except Exception:  # pylint: disable=broad-except
            break
    else:
        return True

    if not assign:
        logger.error("\nUnable to revoke Role Assignments if any, added for Azure Container Storage.")

    return False


def get_k8s_extension_module(module_name):
    try:
        # adding the installed extension in the path
        from azure.cli.core.extension.operations import add_extension_to_path
        add_extension_to_path(CONST_K8S_EXTENSION_NAME)
        # import the extension module
        from importlib import import_module
        azext_custom = import_module(module_name)
        return azext_custom
    except ImportError:
        raise UnknownError(  # pylint: disable=raise-missing-from
            "Please add CLI extension `k8s-extension` for performing Azure Container Storage operations.\n"
            "Run command `az extension add --name k8s-extension`"
        )


def check_if_extension_is_installed(cmd, resource_group, cluster_name) -> bool:
    client_factory = get_k8s_extension_module(CONST_K8S_EXTENSION_CLIENT_FACTORY_MOD_NAME)
    client = client_factory.cf_k8s_extension_operation(cmd.cli_ctx)
    k8s_extension_custom_mod = get_k8s_extension_module(CONST_K8S_EXTENSION_CUSTOM_MOD_NAME)
    return_val = True
    try:
        extension = k8s_extension_custom_mod.show_k8s_extension(
            client,
            resource_group,
            cluster_name,
            CONST_EXT_INSTALLATION_NAME,
            "managedClusters",
        )

        extension_type = extension.extension_type.lower()
        if extension_type != CONST_ACSTOR_K8S_EXTENSION_NAME:
            return_val = False
    except:  # pylint: disable=bare-except
        return_val = False

    return return_val


def _is_rp_registered(cmd, required_rp, subscription_id):
    registered = False
    try:
        providers_client = get_providers_client_factory(cmd.cli_ctx, subscription_id)
        registration_state = getattr(providers_client.get(required_rp), 'registration_state', "NotRegistered")

        registered = (registration_state and registration_state.lower() == 'registered')
    except Exception:  # pylint: disable=broad-except
        pass
    return registered
