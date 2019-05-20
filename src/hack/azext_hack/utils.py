from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.mgmt.resource.resources.models import ResourceGroup

def create_resource_group(cmd, name, location):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    params = ResourceGroup(location=location)
    return client.resource_groups.create_or_update(name, params)
