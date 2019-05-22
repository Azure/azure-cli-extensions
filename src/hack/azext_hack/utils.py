from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.cli.command_modules.sql._util import (
    get_sql_management_client
)
from azure.cli.command_modules.sql.custom import (
    server_create,
    db_create
)

from azure.mgmt.sql.models import (
    Sku,
)

from azure.cli.command_modules.appservice.custom import (
    create_app_service_plan,
    create_webapp
)

def create_resource_group(cmd, name, location):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    params = ResourceGroup(location=location)
    client.resource_groups.create_or_update(name, params)

def create_database(cmd, name, location):
    sql_client = get_sql_management_client(cmd.cli_ctx)
    sql_parameters = {
        'location': location, # "self.region" is 'west-us' by default
        'version': '12.0',
        'administrator_login': 'mysecretname',
        'administrator_login_password': 'HusH_Sec4et'
    }

    poller = server_create(sql_client.servers, name, name, **sql_parameters)
    while not poller.done():
        pass

    print('creating database')
    sku = Sku(capacity=10, name='Standard', tier='Standard')
    poller = db_create(cmd, sql_client.databases,
                       name, name, name,
                       location=location,
                       sku=sku,
                       elastic_pool_id=None)

    return poller

def create_website(cmd, name, location):
    plan = create_app_service_plan(cmd, name, name, True, False)
    return create_webapp(cmd, name, name, plan)
