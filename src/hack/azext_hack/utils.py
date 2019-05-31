from uuid import uuid4
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.cli.command_modules.sql._util import (
    get_sql_management_client
)
from azure.cli.command_modules.sql.custom import (
    server_create as sql_server_create,
    db_create as sql_database_create
)
from azure.mgmt.sql.models import (
    Sku
)
from azure.cli.command_modules.appservice.custom import (
    create_app_service_plan,
    create_webapp,
    update_app_settings,
    set_deployment_user
)
from azure.cli.command_modules.rdbms.custom import (
    _server_create as mysql_server_create
)
from azure.cli.command_modules.appservice._client_factory import (
    web_client_factory
)
from azure.cli.command_modules.rdbms._client_factory import (
    cf_mysql_servers,
    cf_mysql_db
)
from azure.mgmt.rdbms.mysql.models import (
    ServerPropertiesForDefaultCreate,
    StorageProfile
)
from knack.log import get_logger
logger = get_logger(__name__)


class DatabaseCreator(object):
    def __init__(self, database_creator):
        self.poller = None
        self.database_creator = database_creator

    def done(self):
        if not self.poller:
            return False
        return self.poller.done()

    def result(self, timeout=None):
        if not self.poller:
            return None
        return self.poller.result(timeout)

    def create_database(self, _):
        self.poller = self.database_creator()
        return self


def create_resource_group(cmd, name, location):
    client = get_mgmt_service_client(
        cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    params = ResourceGroup(location=location)
    client.resource_groups.create_or_update(name, params)


def create_database(cmd, database_provider, name, location, admin, password):
    if database_provider.lower() == 'mysql':
        server_client = cf_mysql_servers(cmd.cli_ctx, None)
        database_client = cf_mysql_db(cmd.cli_ctx, None)

        def server_creator():
            storage_profile = StorageProfile(
                backup_retention_days=0, geo_redundant_backup='Disabled', storage_mb=200)
            server_properties = ServerPropertiesForDefaultCreate(
                version='5.7', ssl_enforcement='enabled', storage_profile=storage_profile, administrator_login=admin, administrator_login_password=str(password), create_mode='ANSI')
            return server_client.create(resource_group_name=name, server_name=name, parameters=server_properties)
            # cmd, server_client, resource_group_name=name, server_name=name, sku_name='B_Gen5_1', administrator_login=admin, administrator_login_password=password, location=location)

        def database_creator():
            return database_client.create_or_update(
                resource_group_name=name, server_name=name, database_name=name)
    else:
        sql_client = get_sql_management_client(cmd.cli_ctx)
        sql_parameters = {
            'location': location,  # "self.region" is 'west-us' by default
            'version': '12.0',
            'administrator_login': admin,
            'administrator_login_password': password
        }
        sku = Sku(capacity=10, name='Standard', tier='Standard')

        def server_creator():
            return sql_server_create(sql_client.servers, name, name, **sql_parameters)

        def database_creator():
            return sql_database_create(cmd, sql_client.databases,
                                       database_name=name,
                                       server_name=name,
                                       resource_group_name=name,
                                       location=location,
                                       sku=sku,
                                       elastic_pool_id=None)
    wrapper = DatabaseCreator(database_creator)
    server_creator().add_done_callback(wrapper.create_database)
    return wrapper


def create_website(cmd, name, runtime, deployment_local_git=True, deployment_user=None):
    deployment_user_password = None
    create_app_service_plan(cmd, resource_group_name=name,
                            name=name, is_linux=True, hyper_v=False).result()
    webapp = create_webapp(cmd, resource_group_name=name,
                           name=name, plan=name, runtime=runtime,
                           deployment_local_git=deployment_local_git)
    if deployment_user:
        deployment_user_password = uuid4()
        set_deployment_user(cmd, deployment_user, deployment_user_password)
    else:
        deployment_user = web_client_factory(
            cmd.cli_ctx).get_publishing_user().publishing_user_name
    site = {}
    site['deployment_user'] = deployment_user
    site['deployment_password'] = deployment_user_password if deployment_user_password else '***'
    # 'https://{}@{}.scm.azurewebsites.net/{}.git'.format(deployment_user, name, name)
    site['deployment_url'] = webapp.deploymentLocalGitUrl
    site['hostname'] = 'https://{}'.format(webapp.host_names[0])
    return site


def set_website_settings(cmd, name, database_admin, database_password):
    settings = []
    settings.append('DATABASE_NAME={}'.format(name))
    settings.append('DATABASE_HOST={}.database.windows.net'.format(name))
    settings.append('DATABASE_PORT=1433')
    settings.append('DATABASE_USER={}'.format(database_admin))
    settings.append('DATABASE_PASSWORD={}'.format(database_admin))
    update_app_settings(cmd, resource_group_name=name,
                        name=name, settings=settings)
    return settings
