# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


# `az aks identity-binding create` command
def aks_ib_cmd_create(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
    managed_identity_resource_id: str,
    no_wait: bool = False,
):
    from azure.cli.core.util import sdk_no_wait
    from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import (
        IdentityBinding,
        IdentityBindingProperties,
        IdentityBindingManagedIdentityProfile,
    )

    instance = IdentityBinding(
        name=name,
        properties=IdentityBindingProperties(
            managed_identity=IdentityBindingManagedIdentityProfile(
                resource_id=managed_identity_resource_id,
            )
        )
    )

    return sdk_no_wait(
        no_wait,
        client.begin_create_or_update,
        resource_group_name,
        cluster_name,
        name,
        instance,
    )


# `az aks identity-binding delete` command
def aks_ib_cmd_delete(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
    no_wait: bool = False,
):
    from azure.cli.core.util import sdk_no_wait

    return sdk_no_wait(
        no_wait,
        client.begin_delete,
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        identity_binding_name=name,
    )


# `az aks identity-binding show` command
def aks_ib_cmd_show(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
    name: str,
):
    return client.get(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
        identity_binding_name=name,
    )


# `az aks identity-binding list` command
def aks_ib_cmd_list(
    cmd, client,  # pylint: disable=unused-argument
    resource_group_name: str,
    cluster_name: str,
):
    return client.list_by_managed_cluster(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
    )
