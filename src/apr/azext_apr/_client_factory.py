def cf_apr(cli_ctx, *_):
    del cli_ctx
    # Control-plane (ARM) client factory. The az command pipeline calls this
    # BEFORE the handler runs, so it's the right place to refuse control-plane
    # commands while running as a local dev build — otherwise the same gate in the
    # handlers would be shadowed by the error below. Keep this check first when the
    # real azure-mgmt-apr client is wired up.
    from azext_apr.server import raise_if_dev_extension

    raise_if_dev_extension()
    raise NotImplementedError("azure-mgmt-apr SDK not yet available")
