# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from azure.cli.core.util import sdk_no_wait
from azext_aks_preview._client_factory import CUSTOM_MGMT_AKS_PREVIEW


def update_managed_bastion_profile(
    cmd,
    client,
    resource_group_name,
    name,
    no_wait=False,
    aks_custom_headers=None,
    enabled=False,
    require_enabled=False,
    enabling=False,
    bastion_sku=None,
    bastion_public_ip=None,
    bastion_scale_units=None
):
    instance = client.get(resource_group_name, name, headers=aks_custom_headers)

    NetworkProfile = cmd.get_models(
        "NetworkProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )
    BastionProfile = cmd.get_models(
        "BastionProfile",
        resource_type=CUSTOM_MGMT_AKS_PREVIEW,
        operation_group="managed_clusters",
    )

    network_profile = instance.network_profile
    if network_profile is None:
        network_profile = NetworkProfile()

    bastion_profile = network_profile.bastion_profile
    if bastion_profile is None:
        bastion_profile = BastionProfile()

    if enabling and bastion_profile.enabled:
        raise CLIError('Bastion is already enabled, please use "az aks bastion update" to update it.')
    if require_enabled and not bastion_profile.enabled:
        raise CLIError('Bastion is not enabled, please use "az aks bastion enable" to enable it first.')

    bastion_profile.enabled = enabled
    if bastion_sku is not None:
        bastion_profile.sku = bastion_sku
    if bastion_public_ip is not None:
        bastion_profile.public_ip_address_id = bastion_public_ip
    if bastion_scale_units is not None:
        bastion_profile.scale_units = bastion_scale_units

    network_profile.bastion_profile = bastion_profile
    instance.network_profile = network_profile

    result = sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        name,
        instance,
        headers=aks_custom_headers)

    return result
