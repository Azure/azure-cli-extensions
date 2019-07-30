# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# # --------------------------------------------------------------------------------------------
from uuid import uuid4
from azure.cli.command_modules.cognitiveservices.custom import (
    create as create_cogsvcs_account
)
from azure.cli.command_modules.cognitiveservices._client_factory import cf_accounts
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
from azure.cli.command_modules.appservice._client_factory import (
    web_client_factory
)
from azure.cli.command_modules.rdbms._client_factory import (
    cf_mysql_servers,
    cf_mysql_db
)
from azure.mgmt.rdbms.mysql.models import (
    ServerPropertiesForDefaultCreate,
    ServerForCreate,
    StorageProfile,
    Sku as MySqlSku
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
    database_settings = {}
    if database_provider.lower() == 'mysql':
        server_client = cf_mysql_servers(cmd.cli_ctx, None)
        database_client = cf_mysql_db(cmd.cli_ctx, None)
        admin = admin[:16]
        database_settings['engine'] = 'django.db.backends.mysql'

        def server_creator():
            sku_name = 'B_Gen5_1'
            parameters = ServerForCreate(
                sku=MySqlSku(name=sku_name),
                location=location,
                properties=ServerPropertiesForDefaultCreate(
                    administrator_login=admin,
                    administrator_login_password=password,
                    version='5.7',
                    ssl_enforcement='Enabled',
                    storage_profile=StorageProfile(
                        backup_retention_days=0,
                        geo_redundant_backup='Disabled',
                        storage_mb=5120
                    )
                )
            )
            return server_client.create(resource_group_name=name, server_name=name, parameters=parameters)

        def database_creator():
            return database_client.create_or_update(
                resource_group_name=name, server_name=name, database_name=name)
    elif database_provider.lower() == 'cosmosdb' or database_provider.lower() == 'mongodb':
        from azure.mgmt.cosmosdb import CosmosDB
        cosmosdb_client = get_mgmt_service_client(cmd.cli_ctx, CosmosDB)

        from azure.mgmt.cosmosdb.models import (
            DatabaseAccountCreateUpdateParameters,
            DatabaseAccountKind,
            Location,
            ConsistencyPolicy
        )

        def server_creator():
            params = DatabaseAccountCreateUpdateParameters(
                location=location,
                locations=[Location(
                    location_name=location,
                    failover_priority=0,
                    is_zone_redundant=False)],
                kind=DatabaseAccountKind.mongo_db.value,
                consistency_policy=ConsistencyPolicy(
                    default_consistency_level=1,
                    max_staleness_prefix=100,
                    max_interval_in_seconds=5
                )
            )
            return cosmosdb_client.database_accounts.create_or_update(name, name, params)

        def database_creator():
            return cosmosdb_client.database_accounts.create_update_mongo_db_database(
                resource_group_name=name,
                account_name=name,
                database_name=name,
                resource={'id': name},
                options={}
            )
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
    poller = server_creator()
    poller.add_done_callback(wrapper.create_database)
    # poller.add_done_callback(print(poller.result()))
    return wrapper


RUNTIMES = {
    'php': {
        'name': 'php|7.3',
        'is_linux': True
    },
    'node': {
        'name': 'node|10.6',
        'is_linux': True
    },
    'tomcat': {
        'name': 'java|11|Tomcat|9.0',
        'is_linux': True
    },
    'jetty': {
        'name': 'java|11|Jetty|9.3',
        'is_linux': True
    },
    'python': {
        'name': 'python|3.6',
        'is_linux': True
    },
    'aspnet': {
        'name': 'aspnet|4.7',
        'is_linux': False
    }
}

DATABASES = {
    'mysql': {
        'host': '{}.mysql.database.azure.com',
        'port': '3306'
    },
    'sql': {
        'host': '{}.database.windows.net',
        'port': '1433'
    },
    'cosmosdb': {
        'host': '{}.documents.azure.com',
        'port': '10255'
    }
}


def create_website(cmd, name, runtime, deployment_local_git=True, deployment_user=None):
    runtime_values = RUNTIMES[runtime.lower()]
    deployment_user_password = None
    create_app_service_plan(cmd, resource_group_name=name,
                            name=name, is_linux=runtime_values['is_linux'], hyper_v=False).result()
    webapp = create_webapp(cmd, resource_group_name=name,
                           name=name, plan=name, runtime=runtime_values['name'],
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
    site['deployment_url'] = webapp.deploymentLocalGitUrl
    site['hostname'] = 'https://{}'.format(webapp.host_names[0])
    return site


def set_website_settings(cmd, name, database_provider, database_admin, database_password, ai):
    settings = []

    if ai:
        from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
        cogsvcs_client = get_mgmt_service_client(
            cmd.cli_ctx, CognitiveServicesManagementClient)
        cogsvcs_key = cogsvcs_client.accounts.list_keys(name, name).key1
        settings.append('COGNITIVE_SERVICES_KEY={}'.format(cogsvcs_key))

    if database_provider.lower() == 'cosmosdb':
        from azure.mgmt.cosmosdb import CosmosDB
        cosmosdb_client = get_mgmt_service_client(cmd.cli_ctx, CosmosDB)
        result = cosmosdb_client.database_accounts.list_keys(
            resource_group_name=name,
            account_name=name
        )
        database_password = result.primary_master_key

    # TODO: Update username to avoid issues
    database_options = DATABASES[database_provider.lower()]
    settings.append('DATABASE_NAME={}'.format(name))
    settings.append('DATABASE_HOST={}'.format(
        database_options['host'].format(name)))
    settings.append('DATABASE_PORT={}'.format(database_options['port']))
    settings.append('DATABASE_USER={}'.format(database_admin))
    settings.append('DATABASE_PASSWORD={}'.format(database_password))
    update_app_settings(cmd, resource_group_name=name,
                        name=name, settings=settings)
    return settings


def create_cogsvcs_key(cmd, name, location):
    client = cf_accounts(cmd.cli_ctx)
    result = create_cogsvcs_account(client, resource_group_name=name,
                                    account_name=name, sku_name='S0',
                                    kind='CognitiveServices', location=location)
    return result
