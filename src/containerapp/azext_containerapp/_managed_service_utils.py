# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.azclierror import ValidationError
from knack.log import get_logger


class ManagedRedisUtils:

    @staticmethod
    def build_redis_resource_id(subscription_id, resource_group_name, service_name, arg_dict):
        url_fmt = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Cache/redis/{}/databases/{}"
        resource_id = url_fmt.format(
            subscription_id,
            resource_group_name,
            service_name,
            arg_dict["database"] if "database" in arg_dict else "0")
        return resource_id

    @staticmethod
    def build_redis_params(resource_id, capp_name, key_vault_id):
        parameters = {
            'target_service': {
                "type": "AzureResource",
                "id": resource_id
            },
            "auth_info": {
                "auth_type": "secret"
            },
            'secret_store': {
                'key_vault_id': key_vault_id,
            },
            'scope': capp_name,
        }
        return [parameters]

    @staticmethod
    def build_redis_service_connector_def(subscription_id, resource_group_name, service_name, arg_dict, name,
                                          binding_name):
        resource_id = ManagedRedisUtils.build_redis_resource_id(subscription_id, resource_group_name, service_name,
                                                                arg_dict)
        parameters = ManagedRedisUtils.build_redis_params(
            resource_id, name, key_vault_id=None)
        return {"linker_name": binding_name, "parameters": parameters, "resource_id": resource_id}


class ManagedCosmosDBUtils:

    @staticmethod
    def build_cosmos_resource_id(subscription_id, resource_group_name, service_name, arg_dict):
        url_fmt = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DocumentDB/" \
                  "databaseAccounts/{}/mongodbDatabases/{}"
        resource_id = url_fmt.format(
            subscription_id,
            resource_group_name,
            service_name,
            arg_dict["database"])
        return resource_id

    @staticmethod
    def build_cosmos_params(resource_id, capp_name, key_vault_id):
        parameters = {
            'target_service': {
                "type": "AzureResource",
                "id": resource_id
            },
            'auth_info': {
                'auth_type': "systemAssignedIdentity"
            },
            'secret_store': {
                'key_vault_id': key_vault_id,
            },
            'scope': capp_name,
        }
        return [parameters]

    @staticmethod
    def build_cosmosdb_service_connector_def(subscription_id, resource_group_name, service_name, arg_dict, name,
                                             binding_name):
        if "database" not in arg_dict:
            raise ValidationError(
                "Managed Cosmos DB needs the database argument.")
        resource_id = ManagedCosmosDBUtils.build_cosmos_resource_id(subscription_id, resource_group_name, service_name,
                                                                    arg_dict)
        parameters = ManagedCosmosDBUtils.build_cosmos_params(
            resource_id, name, key_vault_id=None)
        return {"linker_name": binding_name, "parameters": parameters, "resource_id": resource_id}


class ManagedPostgreSQLFlexibleUtils:

    @staticmethod
    def build_postgres_resource_id(subscription_id, resource_group_name, service_name, arg_dict):
        url_fmt = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DBforPostgreSQL/flexibleServers/" \
                  "{}/databases/{}"
        resource_id = url_fmt.format(
            subscription_id,
            resource_group_name,
            service_name,
            arg_dict["database"])
        return resource_id

    @staticmethod
    def build_postgres_params(resource_id, capp_name, username, password, key_vault_id):
        parameters = {
            'target_service': {
                "type": "AzureResource",
                "id": resource_id
            },
            'auth_info': {
                'authType': "secret",
                'secret_info': {
                    'secret_type': "rawValue",
                    'value': password,
                },
                'name': username
            },
            'secret_store': {
                'key_vault_id': key_vault_id,
            },
            'scope': capp_name,
        }
        return [parameters]

    @staticmethod
    def build_postgresql_service_connector_def(subscription_id, resource_group_name, service_name, arg_dict, name,
                                               binding_name):
        if not all(key in arg_dict for key in ["database", "username", "password"]):
            raise ValidationError(
                "Managed PostgreSQL Flexible Server needs the database, username, and password arguments.")
        resource_id = ManagedPostgreSQLFlexibleUtils.build_postgres_resource_id(subscription_id, resource_group_name,
                                                                                service_name, arg_dict)
        parameters = ManagedPostgreSQLFlexibleUtils.build_postgres_params(resource_id, name, arg_dict["username"],
                                                                          arg_dict["password"], key_vault_id=None)
        return {"linker_name": binding_name, "parameters": parameters, "resource_id": resource_id}


class ManagedMySQLFlexibleUtils:

    @staticmethod
    def build_mysql_resource_id(subscription_id, resource_group_name, service_name, arg_dict):
        url_fmt = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.DBforMySQL/flexibleServers/" \
                  "{}/databases/{}"
        resource_id = url_fmt.format(
            subscription_id,
            resource_group_name,
            service_name,
            arg_dict["database"])
        return resource_id

    @staticmethod
    def build_mysql_params(resource_id, capp_name, username, password, key_vault_id):
        parameters = {
            'target_service': {
                "type": "AzureResource",
                "id": resource_id
            },
            'auth_info': {
                'authType': "secret",
                'secret_info': {
                    'secret_type': "rawValue",
                    'value': password,
                },
                'name': username
            },
            'secret_store': {
                'key_vault_id': key_vault_id,
            },
            'scope': capp_name,
        }
        return [parameters]

    @staticmethod
    def build_mysql_service_connector_def(subscription_id, resource_group_name, service_name, arg_dict, name,
                                          binding_name):
        if not all(key in arg_dict for key in ["database", "username", "password"]):
            raise ValidationError(
                "Managed MySQL Flexible Server needs the database, username, and password arguments.")
        resource_id = ManagedMySQLFlexibleUtils.build_mysql_resource_id(subscription_id, resource_group_name,
                                                                        service_name, arg_dict)
        parameters = ManagedMySQLFlexibleUtils.build_mysql_params(resource_id, name, arg_dict["username"],
                                                                  arg_dict["password"], key_vault_id=None)
        return {"linker_name": binding_name, "parameters": parameters, "resource_id": resource_id}


class ManagedKafkaUtils:

    @staticmethod
    def build_kafka_server_params(capp_name, arg_dict, key_vault_id, client_type=None, customized_keys=None):
        server_parameters = {
            'target_service': {
                "type": "ConfluentBootstrapServer",
                "endpoint": arg_dict["bootstrap_server"]
            },
            'auth_info': {
                'name': arg_dict["kafka_key"],
                'secret_info': {
                    'secret_type': 'rawValue',
                    'value': arg_dict["kafka_secret"]
                },
                'auth_type': 'secret'
            },
            'secret_store': {
                'key_vault_id': key_vault_id,
            },
            'client_type': client_type,
            'scope': capp_name,
            'configurationInfo': {
                'customizedKeys': customized_keys
            },
        }
        return [server_parameters]

    @staticmethod
    def build_kafka_registry_params(capp_name, arg_dict, key_vault_id, client_type=None, customized_keys=None):
        registry_parameters = {
            'target_service': {
                "type": "ConfluentSchemaRegistry",
                "endpoint": arg_dict["schema_registry"]
            },
            'auth_info': {
                'name': arg_dict["schema_key"],
                'secret_info': {
                    'secret_type': 'rawValue',
                    'value': arg_dict["schema_secret"]
                },
                'auth_type': 'secret'
            },
            'secret_store': {
                'key_vault_id': key_vault_id,
            },
            'client_type': client_type,
            'scope': capp_name,
            'configurationInfo': {
                'customizedKeys': customized_keys
            },
        }
        return [registry_parameters]

    @staticmethod
    def build_kafka_service_binding_name(binding_name, arg_dict):
        logger = get_logger(__name__)
        bootstrap_server_binding = "_bootstrap_server"
        registry_server_binding = "_schema_registry"
        binding_prefix = binding_name
        if '.' in binding_prefix:
            logger.warning(
                "Kafka on Confluent cloud binding names cannot contain periods ('.')."
                " Removing '.' and generating binding name ...")
            binding_prefix = binding_prefix.replace('.', '')
        binding_name = (
            f"{binding_prefix}{bootstrap_server_binding}.{binding_prefix}{registry_server_binding}"
            if len(arg_dict) == 6 else
            f"{binding_prefix}{bootstrap_server_binding}"
        )
        return binding_name

    @staticmethod
    def build_kafka_service_connector_def(arg_dict, name, binding_name):
        logger = get_logger(__name__)
        has_server_params = all(key in arg_dict for key in [
                                "bootstrap_server", "kafka_key", "kafka_secret"])
        partial_registry_params = any(key in arg_dict for key in [
                                      "schema_registry", "schema_secret", "schema_secret"])
        has_registry_params = all(key in arg_dict for key in [
                                  "schema_registry", "schema_secret", "schema_secret"])

        if not has_server_params:
            logger.warning("With no space in-between, Managed Kafka bootstrap server arguments"
                           "  are in the form: bootstrap_server=pkc-xxxx.eastus.azure.confluent.cloud:9092,"
                           "kafka_key=xxxxx,kafka_secret=xxxxx. For a REST Endpoint, the first argument"
                           " takes the form: bootstrap_server=https://pkc-xxxx.eastus.azure.confluent.cloud:443")
            raise ValidationError(
                "Managed Kafka needs the bootstrap_server, kafka_key, and kafka_secret arguments. All must be set.")

        if partial_registry_params and not has_registry_params:
            logger.warning("With no space in-between, Managed Kafka schema registry arguments"
                           " are in the form: schema_registry=https://psrc-xxxx.westus2.azure.confluent.cloud,"
                           "schema_key=xxxxx,schema_secret=xxxxx")
            raise ValidationError(
                "Managed Kafka needs the schema_registry, schema_key, and schema_secret arguments. All must be set.")

        server_parameters = []
        registry_parameters = []

        if has_server_params:
            server_parameters = ManagedKafkaUtils.build_kafka_server_params(
                name, arg_dict, key_vault_id=None)
        if has_server_params and has_registry_params:
            if len(arg_dict) > 6:
                logger.warning(
                    "More than the required arguments were provided. Only required arguments"
                    " will be used. Proceeding with operation ...")
            registry_parameters = ManagedKafkaUtils.build_kafka_registry_params(
                name, arg_dict, key_vault_id=None)

        parameters = server_parameters + registry_parameters
        return {"linker_name": binding_name, "parameters": parameters, "resource_id": None}
