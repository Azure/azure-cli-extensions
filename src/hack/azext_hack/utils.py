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
    Sku
)

from azure.cli.command_modules.appservice.custom import (
    create_app_service_plan,
    create_webapp,
    update_app_settings
)

user = 'mysecretname'
password = 'THis_is_Sec4et!'

class DatabaseCreator(object):
    def __init__(self, cmd, client, name, location, sku):
        self.cmd = cmd
        self.client = client
        self.name = name
        self.location = location
        self.sku = sku
        self.poller = None
    def done(self):
        if not self.poller:
            return False
        return self.poller.done()
    def result(self, timeout=None):
        if not self.poller:
            return None
        return self.poller.result(timeout)
    def create(self, _):
        print('creating database')
        self.poller = db_create(self.cmd, self.client,
                                database_name=self.name,
                                server_name=self.name,
                                resource_group_name=self.name,
                                location=self.location,
                                sku=self.sku,
                                elastic_pool_id=None)
        return self

def create_resource_group(cmd, name, location):
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    params = ResourceGroup(location=location)
    client.resource_groups.create_or_update(name, params)

def create_database(cmd, name, location):
    sql_client = get_sql_management_client(cmd.cli_ctx)
    sql_parameters = {
        'location': location, # "self.region" is 'west-us' by default
        'version': '12.0',
        'administrator_login': user,
        'administrator_login_password': password
    }

    sku = Sku(capacity=10, name='Standard', tier='Standard')
    creator = DatabaseCreator(cmd, sql_client.databases, name, location, sku)
    server_create(sql_client.servers, name, name, **sql_parameters).add_done_callback(creator.create)

    return creator

def create_website(cmd, name, location):
    create_app_service_plan(cmd, resource_group_name=name, name=name, is_linux=True, hyper_v=False).result()
    create_webapp(cmd, resource_group_name=name, name=name, plan=name, runtime='python|3.6')
    settings = []
    settings.append('DATABASE_NAME={}'.format(name))
    settings.append('DATABASE_HOST={}.database.windows.net'.format(name))
    settings.append('DATABASE_PORT=1433')
    settings.append('DATABASE_USER={}'.format(user))
    settings.append('DATABASE_PASSWORD={}'.format(password))
    update_app_settings(cmd, resource_group_name=name, name=name, settings=['test=value'])
