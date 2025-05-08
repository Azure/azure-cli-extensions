# `az aks identity-binding create` command
def aks_ib_cmd_create(
    cmd, client,
    resource_group_name: str,
    cluster_name: str,
    name: str,
    managed_identity_resource_id: str,
    no_wait: bool = False,
):
    from azure.mgmt.core.tools import parse_resource_id
    from azure.cli.core.util import sdk_no_wait
    from azext_aks_preview._client_factory import get_msi_client
    from azext_aks_preview.vendored_sdks.azure_mgmt_preview_aks.models import (
        IdentityBinding,
        IdentityBindingProperties,
        IdentityBindingManagedIdentityProfile,
    )

    # FIXME(hbc): workaround for resolving MI from client side
    parsed_managed_identity_resource_id = parse_resource_id(managed_identity_resource_id)
    msi_client = get_msi_client(cmd.cli_ctx, subscription_id=parsed_managed_identity_resource_id['subscription'])
    msi = msi_client.user_assigned_identities.get(
        parsed_managed_identity_resource_id['resource_group'],
        parsed_managed_identity_resource_id['resource_name'],
    )

    instance = IdentityBinding(
        name=name,
        properties=IdentityBindingProperties(
            managed_identity=IdentityBindingManagedIdentityProfile(
                resource_id=managed_identity_resource_id,
                client_id=msi.client_id,
                object_id=msi.principal_id,
                tenant_id=msi.tenant_id,
            )
        )
    )
    instance.name = name
    print(instance)

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
    cmd, client,
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
    cmd, client,
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
    cmd, client,
    resource_group_name: str,
    cluster_name: str,
):
    return client.list_by_managed_cluster(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
    )
