VERSION_2023_01_01_PREVIEW = "2023-01-01-preview"
from azure.cli.core.profiles import ResourceType

def cf_metadata(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_CONTAINERREGISTRY, api_version=VERSION_2023_01_01_PREVIEW)
