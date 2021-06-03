

def cf_resource_graph_client(cli_ctx, _):
    from azure.mgmt.resourcegraph import ResourceGraphClient
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx,
                                   ResourceGraphClient, subscription_bound=False)
