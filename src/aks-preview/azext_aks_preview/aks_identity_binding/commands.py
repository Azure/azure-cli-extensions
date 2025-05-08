# `az aks identity-binding create` command
def aks_ib_cmd_create(
    identity_binding_name: str,
    *args, **kwargs,
):
    print(args, kwargs)
    raise ValueError('create')

# `az aks identity-binding show` command
def aks_ib_cmd_show(
    identity_binding_name: str,
    *args, **kwargs,
):
    print(args, kwargs)
    raise ValueError('show')