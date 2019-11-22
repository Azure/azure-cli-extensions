# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from uuid import uuid4
from knack.log import get_logger

_DATABASES = {
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

logger = get_logger(__name__)


# pylint: disable=too-few-public-methods
class DatabaseCreationStep():
    def __init__(self, name: str, delegate, params):
        self.delegate = delegate
        self.params = params
        self.name = name


class DatabaseCreator():
    def __init__(self, steps):
        if not steps:
            raise 'Steps cannot be empty'
        self.steps = steps
        self.__current_poller = None
        self.__is_active = True

    def create(self):
        self.__run_step()
        return self

    # pylint: disable=unused-argument
    def __run_step(self, *args):
        if self.steps:
            step = self.steps.pop(0)
            logger.warning('Configuring %s...', step.name)
            return_value = None
            if step.params:
                return_value = step.delegate(**step.params)
            else:
                return_value = step.delegate()
            if hasattr(return_value, 'add_done_callback'):
                self.__current_poller = return_value
                self.__current_poller.add_done_callback(self.__run_step)
            else:
                self.__run_step(None)
        else:
            self.__is_active = False

    def result(self, timeout):
        if self.__current_poller and hasattr(self.__current_poller, 'result'):
            self.__current_poller.result(timeout)

    def done(self):
        if self.__is_active:
            return False
        return True


class Database():
    def __init__(self, cmd, database_type: str, name: str, location: str):
        self.__steps = []
        self.__cmd = cmd
        self.database_type = database_type.lower()
        self.name = name
        self.admin = 'database_admin'
        self.password = str(uuid4())
        self.location = location

    def create(self):
        if self.database_type == 'mysql':
            steps = self.__get_mysql_steps(
                self.__cmd, self.name, self.location, self.admin, self.password)
        elif self.database_type == 'sql':
            steps = self.__get_sql_steps(
                self.__cmd, self.name, self.location, self.admin, self.password)
        elif self.database_type == 'cosmosdb' or self.database_type == 'mongodb':
            steps = self.__get_cosmosdb_steps(
                self.__cmd, self.name, self.location)
        else:
            raise 'Unknown data store type'
        creator = DatabaseCreator(steps)
        return creator.create()

    @property
    def host(self) -> str:
        return _DATABASES[self.database_type]['host'].format(self.name)

    @property
    def port(self) -> str:
        return _DATABASES[self.database_type]['port']

    def __get_cosmosdb_steps(self, cmd, name, location):
        from azure.mgmt.cosmosdb import CosmosDB
        from azure.cli.core.commands.client_factory import get_mgmt_service_client

        steps = []

        cosmosdb_client = get_mgmt_service_client(cmd.cli_ctx, CosmosDB)

        from azure.mgmt.cosmosdb.models import (
            DatabaseAccountCreateUpdateParameters,
            DatabaseAccountKind,
            Location,
            ConsistencyPolicy
        )

        server_params = {
            'resource_group_name': name,
            'account_name': name,
            'params': DatabaseAccountCreateUpdateParameters(
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
        }
        steps.append(DatabaseCreationStep(
            'server', cosmosdb_client.database_accounts.create_or_update, server_params))

        database_params = {
            'resource_group_name': name,
            'account_name': name,
            'database_name': name,
            'resource': {'id': name},
            'options': {}
        }
        steps.append(DatabaseCreationStep(
            'database', cosmosdb_client.database_accounts.create_update_mongo_db_database, database_params))

        def retrieve_password():
            result = cosmosdb_client.database_accounts.list_keys(
                resource_group_name=name,
                account_name=name
            )
            self.password = result.primary_master_key
        steps.append(DatabaseCreationStep(
            'retrieve password', retrieve_password, None))
        return steps

    # pylint: disable=no-self-use
    def __get_mysql_steps(self, cmd, name: str, location: str, admin: str, password: str):
        from azure.cli.command_modules.rdbms._client_factory import (
            cf_mysql_servers,
            cf_mysql_db,
            cf_mysql_firewall_rules
        )
        from azure.mgmt.rdbms.mysql.models import (
            ServerPropertiesForDefaultCreate,
            ServerForCreate,
            StorageProfile,
            Sku
        )

        mysql_server_client = cf_mysql_servers(cmd.cli_ctx, None)
        mysql_database_client = cf_mysql_db(cmd.cli_ctx, None)
        mysql_firewall_client = cf_mysql_firewall_rules(cmd.cli_ctx, None)

        admin = admin[:16]

        steps = []

        server_params = {
            'resource_group_name': name,
            'server_name': name,
            'parameters': ServerForCreate(
                sku=Sku(name='B_Gen5_1'),
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
        }
        steps.append(DatabaseCreationStep('database server',
                                          mysql_server_client.create, server_params))

        database_params = {
            'resource_group_name': name,
            'server_name': name,
            'database_name': name
        }
        steps.append(DatabaseCreationStep(
            'database', mysql_database_client.create_or_update, database_params))

        firewall_params = {
            'resource_group_name': name,
            'server_name': name,
            'firewall_rule_name': 'Azure',
            'start_ip_address': '0.0.0.0',
            'end_ip_address': '0.0.0.0'
        }

        steps.append(DatabaseCreationStep('database firewall',
                                          mysql_firewall_client.create_or_update, firewall_params))
        return steps

    # pylint: disable=no-self-use
    def __get_sql_steps(self, cmd, name, location, admin, password):
        from azure.cli.command_modules.sql._util import (
            get_sql_management_client
        )
        from azure.cli.command_modules.sql.custom import (
            server_create as sql_server_create,
            db_create as sql_database_create,
            firewall_rule_allow_all_azure_ips as sql_firewall_allow_azure,
            ComputeModelType
        )
        from azure.mgmt.sql.models import (
            Sku
        )

        sql_client = get_sql_management_client(cmd.cli_ctx)

        steps = []

        server_parameters = {
            'client': sql_client.servers,
            'resource_group_name': name,
            'server_name': name,
            'location': location,
            'version': '12.0',
            'administrator_login': admin,
            'administrator_login_password': password
        }
        steps.append(DatabaseCreationStep(
            'server', sql_server_create, server_parameters))

        sku = Sku(capacity=10, name='Standard', tier='Standard', family='Gen5')

        database_parameters = {
            'cmd': cmd,
            'client': sql_client.databases,
            'database_name': name,
            'server_name': name,
            'resource_group_name': name,
            'location': location,
            'sku': sku,
            'elastic_pool_id': None,
            'compute_model': ComputeModelType('Serverless')
        }
        steps.append(DatabaseCreationStep(
            'database', sql_database_create, database_parameters))

        firewall_parameters = {
            'client': sql_client.firewall_rules,
            'server_name': name,
            'resource_group_name': name
        }
        steps.append(DatabaseCreationStep(
            'firewall', sql_firewall_allow_azure, firewall_parameters))
        return steps
