# `az aks identity-binding create` command
def aks_ib_cmd_create(
    cmd, client,
    resource_group_name: str,
    cluster_name: str,
    name: str,
    managed_identity_resource_id: str,
):
    print(client, resource_group_name, cluster_name, name)
    raise ValueError('create')


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
    print(type(client))
    return client.list_by_managed_cluster(
        resource_group_name=resource_group_name,
        resource_name=cluster_name,
    )