# pylint: disable=too-many-lines
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, consider-using-f-string, broad-except, no-member, raise-missing-from
import datetime
from knack.util import CLIError
from knack.log import get_logger
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    AutoscaleSettings,
    ClusterResource,
    ClusterResourceProperties,
    ContainerPartitionKey,
    DataCenterResource,
    DataCenterResourceProperties,
    ManagedCassandraManagedServiceIdentity,
    AuthenticationMethodLdapProperties,
    ServiceResourceCreateUpdateParameters,
    MongoRoleDefinitionCreateUpdateParameters,
    MongoUserDefinitionCreateUpdateParameters,
    DatabaseAccountKind,
    ContinuousBackupRestoreLocation,
    DatabaseAccountUpdateParameters,
    RestoreParameters,
    PeriodicModeBackupPolicy,
    PeriodicModeProperties,
    ContinuousModeBackupPolicy,
    ContinuousModeProperties,
    DatabaseAccountCreateUpdateParameters,
    MergeParameters,
    RetrieveThroughputParameters,
    RetrieveThroughputPropertiesResource,
    PhysicalPartitionId,
    RedistributeThroughputParameters,
    RedistributeThroughputPropertiesResource,
    ThroughputPolicyType,
    SqlDatabaseResource,
    SqlDatabaseCreateUpdateParameters,
    SqlContainerResource,
    SqlContainerCreateUpdateParameters,
    MongoDBDatabaseResource,
    MongoDBDatabaseCreateUpdateParameters,
    MongoDBCollectionResource,
    MongoDBCollectionCreateUpdateParameters,
    TableResource,
    TableCreateUpdateParameters,
    GremlinDatabaseCreateUpdateParameters,
    GremlinGraphResource,
    GremlinGraphCreateUpdateParameters,
    Location,
    CreateMode,
    ConsistencyPolicy,
    ResourceIdentityType,
    ManagedServiceIdentity,
    AnalyticalStorageConfiguration,
    ManagedServiceIdentityUserAssignedIdentity,
    MongoCluster,
    NodeGroupSpec,
    NodeKind,
    FirewallRule,
    CosmosCassandraDataTransferDataSourceSink,
    CosmosSqlDataTransferDataSourceSink,
    CosmosMongoDataTransferDataSourceSink
)

from azext_cosmosdb_preview._client_factory import (
    cf_restorable_gremlin_resources,
    cf_restorable_table_resources,
    cf_restorable_database_accounts
)

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.command_modules.cosmosdb.custom import _convert_to_utc_timestamp
from azure.core.exceptions import ResourceNotFoundError

from azure.cli.command_modules.cosmosdb._client_factory import (
    cf_restorable_sql_resources,
    cf_restorable_mongodb_resources
)

DEFAULT_INDEXING_POLICY = """{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [
    {
      "path": "/*"
    }
  ],
  "excludedPaths": [
    {
      "path": "/\\"_etag\\"/?"
    }
  ]
}"""


logger = get_logger(__name__)


def _handle_exists_exception(cloud_error):
    if cloud_error.status_code == 404:
        return False
    raise cloud_error


def cli_cosmosdb_mongocluster_firewall_rule_create(client,
                                                   resource_group_name,
                                                   cluster_name,
                                                   rule_name,
                                                   start_ip_address,
                                                   end_ip_address):

    '''Creates an Azure Cosmos DB Mongo Cluster Firewall rule'''

    firewall_rule = FirewallRule(start_ip_address=start_ip_address, end_ip_address=end_ip_address)

    return client.begin_create_or_update_firewall_rule(resource_group_name, cluster_name, rule_name, firewall_rule)


def cli_cosmosdb_mongocluster_firewall_rule_update(client,
                                                   resource_group_name,
                                                   cluster_name,
                                                   rule_name,
                                                   start_ip_address,
                                                   end_ip_address):

    '''Creates an Azure Cosmos DB Mongo Cluster Firewall rule'''

    mongo_cluster_firewallRule = client.get_firewall_rule(resource_group_name, cluster_name, rule_name)

    if start_ip_address is None:
        start_ip_address = mongo_cluster_firewallRule.startIpAddress

    if end_ip_address is None:
        end_ip_address = mongo_cluster_firewallRule.endIpAddress

    firewall_rule = FirewallRule(start_ip_address=start_ip_address, end_ip_address=end_ip_address)

    return client.begin_create_or_update_firewall_rule(resource_group_name, cluster_name, rule_name, firewall_rule)


def cli_cosmosdb_mongocluster_firewall_rule_list(client, resource_group_name, cluster_name):

    """List Azure CosmosDB Mongo Cluster Firewall Rule."""

    return client.list_firewall_rules(resource_group_name, cluster_name)


def cli_cosmosdb_mongocluster_firewall_rule_get(client, resource_group_name, cluster_name, rule_name):

    """Gets Azure CosmosDB Mongo Cluster Firewall rule"""

    return client.get_firewall_rule(resource_group_name, cluster_name, rule_name)


def cli_cosmosdb_mongocluster_firewall_rule_delete(client, resource_group_name, cluster_name, rule_name):

    """Delete Azure CosmosDB Mongo Cluster Firewall Rule"""

    return client.begin_delete_firewall_rule(resource_group_name, cluster_name, rule_name)


def cli_cosmosdb_mongocluster_create(client,
                                     resource_group_name,
                                     cluster_name,
                                     administrator_login,
                                     administrator_login_password,
                                     location,
                                     tags=None,
                                     server_version="5.0",
                                     shard_node_tier=None,
                                     shard_node_disk_size_gb=None,
                                     shard_node_ha=None,
                                     shard_node_count=1):

    '''Creates an Azure Cosmos DB Mongo Cluster '''

    if ((administrator_login is None and administrator_login_password is not None) or (administrator_login is not None and administrator_login_password is None)):
        raise InvalidArgumentValueError('Both(administrator_login and administrator_login_password) Mongo Cluster admin user parameters must be provided together')

    node_group_spec = NodeGroupSpec(
        sku=shard_node_tier,
        disk_size_gb=shard_node_disk_size_gb,
        enable_ha=shard_node_ha,
        kind=NodeKind.SHARD.value,
        node_count=shard_node_count
    )

    node_group_specs = [node_group_spec]
    mongodb_cluster = MongoCluster(
        location=location,
        tags=tags,
        create_mode=CreateMode.DEFAULT.value,
        administrator_login=administrator_login,
        administrator_login_password=administrator_login_password,
        server_version=server_version,
        node_group_specs=node_group_specs)

    return client.begin_create_or_update(resource_group_name, cluster_name, mongodb_cluster)


def cli_cosmosdb_mongocluster_update(client,
                                     resource_group_name,
                                     cluster_name,
                                     administrator_login=None,
                                     administrator_login_password=None,
                                     tags=None,
                                     server_version=None,
                                     shard_node_tier=None,
                                     shard_node_ha=None,
                                     shard_node_disk_size_gb=None):

    '''Updates an Azure Cosmos DB Mongo Cluster '''

    mongo_cluster_resource = client.get(resource_group_name, cluster_name)

    # user name and password should be updated together

    if ((administrator_login is None and administrator_login_password is not None) or (administrator_login is not None and administrator_login_password is None)):
        raise InvalidArgumentValueError('Both(administrator_login and administrator_login_password) Mongo Cluster admin user parameters must be provided together')

    if administrator_login_password is None:
        administrator_login_password = mongo_cluster_resource.administrator_login_password

    # Resource location is immutable
    location = mongo_cluster_resource.location

    if server_version is None:
        server_version = mongo_cluster_resource.server_version
    if tags is None:
        tags = mongo_cluster_resource.tags

    # Shard info update.
    if shard_node_tier is None:
        shard_node_tier = mongo_cluster_resource.node_group_specs[0].sku
    if shard_node_disk_size_gb is None:
        shard_node_disk_size_gb = mongo_cluster_resource.node_group_specs[0].disk_size_gb
    if shard_node_ha is None:
        shard_node_ha = mongo_cluster_resource.node_group_specs[0].enable_ha

    node_group_spec = NodeGroupSpec(
        sku=shard_node_tier,
        disk_size_gb=shard_node_disk_size_gb,
        enable_ha=shard_node_ha,
        kind=NodeKind.SHARD.value,
        node_count=None,
    )

    node_group_specs = [node_group_spec]
    mongodb_cluster = MongoCluster(
        location=location,
        tags=tags,
        create_mode=CreateMode.DEFAULT.value,
        administrator_login=administrator_login,
        administrator_login_password=administrator_login_password,
        server_version=server_version,
        node_group_specs=node_group_specs)

    return client.begin_create_or_update(resource_group_name, cluster_name, mongodb_cluster)


def cli_cosmosdb_mongocluster_list(client,
                                   resource_group_name=None):

    """List Azure CosmosDB Mongo Clusters by resource group and subscription."""

    if resource_group_name is None:
        return client.list()

    return client.list_by_resource_group(resource_group_name)


def cli_cosmosdb_mongocluster_get(client,
                                  resource_group_name, cluster_name):

    """Gets Azure CosmosDB Mongo Cluster"""

    return client.get(resource_group_name, cluster_name)


def cli_cosmosdb_mongocluster_delete(client,
                                     resource_group_name, cluster_name):

    """Delete Azure CosmosDB Mongo Cluster"""

    return client.begin_delete(resource_group_name, cluster_name)


def cli_cosmosdb_managed_cassandra_cluster_create(client,
                                                  resource_group_name,
                                                  cluster_name,
                                                  location,
                                                  delegated_management_subnet_id,
                                                  tags=None,
                                                  identity_type='None',
                                                  cluster_name_override=None,
                                                  initial_cassandra_admin_password=None,
                                                  client_certificates=None,
                                                  external_gossip_certificates=None,
                                                  external_seed_nodes=None,
                                                  restore_from_backup_id=None,
                                                  cassandra_version=None,
                                                  authentication_method=None,
                                                  hours_between_backups=None,
                                                  repair_enabled=None,
                                                  cluster_type='Production',
                                                  extensions=None):

    """Creates an Azure Managed Cassandra Cluster"""

    if initial_cassandra_admin_password is None and external_gossip_certificates is None:
        raise CLIError('At least one out of the Initial Cassandra Admin Password or External Gossip Certificates is required.')

    if initial_cassandra_admin_password is not None and external_gossip_certificates is not None:
        raise CLIError('Only one out of the Initial Cassandra Admin Password or External Gossip Certificates has to be specified.')

    cluster_properties = ClusterResourceProperties(
        delegated_management_subnet_id=delegated_management_subnet_id,
        cluster_name_override=cluster_name_override,
        initial_cassandra_admin_password=initial_cassandra_admin_password,
        client_certificates=client_certificates,
        external_gossip_certificates=external_gossip_certificates,
        external_seed_nodes=external_seed_nodes,
        restore_from_backup_id=restore_from_backup_id,
        cassandra_version=cassandra_version,
        authentication_method=authentication_method,
        hours_between_backups=hours_between_backups,
        repair_enabled=repair_enabled,
        cluster_type=cluster_type,
        extensions=extensions)

    managed_service_identity_parameter = ManagedCassandraManagedServiceIdentity(
        type=identity_type
    )

    cluster_resource_create_update_parameters = ClusterResource(
        location=location,
        tags=tags,
        identity=managed_service_identity_parameter,
        properties=cluster_properties)

    return client.begin_create_update(resource_group_name, cluster_name, cluster_resource_create_update_parameters)


def cli_cosmosdb_managed_cassandra_cluster_update(client,
                                                  resource_group_name,
                                                  cluster_name,
                                                  tags=None,
                                                  identity_type=None,
                                                  client_certificates=None,
                                                  external_gossip_certificates=None,
                                                  external_seed_nodes=None,
                                                  cassandra_version=None,
                                                  authentication_method=None,
                                                  hours_between_backups=None,
                                                  repair_enabled=None,
                                                  cluster_type=None,
                                                  extensions=None):

    """Updates an Azure Managed Cassandra Cluster"""

    cluster_resource = client.get(resource_group_name, cluster_name)

    if client_certificates is None:
        client_certificates = cluster_resource.properties.client_certificates

    if external_gossip_certificates is not None:
        external_gossip_certificates = cluster_resource.properties.external_gossip_certificates

    if external_seed_nodes is None:
        external_seed_nodes = cluster_resource.properties.external_seed_nodes

    if cassandra_version is None:
        cassandra_version = cluster_resource.properties.cassandra_version

    if authentication_method is None:
        authentication_method = cluster_resource.properties.authentication_method

    if hours_between_backups is None:
        hours_between_backups = cluster_resource.properties.hours_between_backups

    if repair_enabled is None:
        repair_enabled = cluster_resource.properties.repair_enabled

    if tags is None:
        tags = cluster_resource.tags

    identity = cluster_resource.identity

    if identity_type is not None:
        identity = ManagedCassandraManagedServiceIdentity(type=identity_type)

    if cluster_type is None:
        cluster_type = cluster_resource.properties.cluster_type

    if extensions is None:
        extensions = cluster_resource.properties.extensions

    # to remove extension
    if len(extensions) == 1 and extensions[0] == '':
        extensions = None

    cluster_properties = ClusterResourceProperties(
        provisioning_state=cluster_resource.properties.provisioning_state,
        restore_from_backup_id=cluster_resource.properties.restore_from_backup_id,
        delegated_management_subnet_id=cluster_resource.properties.delegated_management_subnet_id,
        cassandra_version=cassandra_version,
        cluster_name_override=cluster_resource.properties.cluster_name_override,
        authentication_method=authentication_method,
        initial_cassandra_admin_password=cluster_resource.properties.initial_cassandra_admin_password,
        hours_between_backups=hours_between_backups,
        repair_enabled=repair_enabled,
        client_certificates=client_certificates,
        external_gossip_certificates=external_gossip_certificates,
        gossip_certificates=cluster_resource.properties.gossip_certificates,
        external_seed_nodes=cluster_resource.properties.external_seed_nodes,
        seed_nodes=cluster_resource.properties.seed_nodes,
        cluster_type=cluster_type,
        extensions=extensions
    )

    cluster_resource_create_update_parameters = ClusterResource(
        location=cluster_resource.location,
        tags=tags,
        identity=identity,
        properties=cluster_properties)

    return client.begin_create_update(resource_group_name, cluster_name, cluster_resource_create_update_parameters)


def cli_cosmosdb_managed_cassandra_cluster_list(client,
                                                resource_group_name=None):

    """List Azure Managed Cassandra Clusters by resource group and subscription."""

    if resource_group_name is None:
        return client.list_by_subscription()

    return client.list_by_resource_group(resource_group_name)


def cli_cosmosdb_managed_cassandra_cluster_list_backup(client,
                                                       resource_group_name,
                                                       cluster_name):
    """List Azure Managed Cassandra Backup"""
    return client.list_backups(resource_group_name, cluster_name)


def cli_cosmosdb_managed_cassandra_cluster_deallocate(client,
                                                      resource_group_name,
                                                      cluster_name,
                                                      force='false'):
    """Deallocate Azure Managed Cassandra Cluster"""
    return client.begin_deallocate(resource_group_name, cluster_name, force)


def cli_cosmosdb_managed_cassandra_cluster_show_backup(client,
                                                       resource_group_name,
                                                       cluster_name,
                                                       backup_id):
    """Get Azure Managed Cassandra Backup"""
    return client.get_backup(resource_group_name, cluster_name, backup_id)


def cli_cosmosdb_managed_cassandra_datacenter_create(client,
                                                     resource_group_name,
                                                     cluster_name,
                                                     data_center_name,
                                                     data_center_location,
                                                     delegated_subnet_id,
                                                     node_count,
                                                     base64_encoded_cassandra_yaml_fragment=None,
                                                     managed_disk_customer_key_uri=None,
                                                     backup_storage_customer_key_uri=None,
                                                     sku=None,
                                                     disk_sku=None,
                                                     disk_capacity=None,
                                                     availability_zone=None,
                                                     server_hostname=None,
                                                     server_port=None,
                                                     service_user_distinguished_name=None,
                                                     service_user_password=None,
                                                     search_base_distinguished_name=None,
                                                     search_filter_template=None,
                                                     server_certificates=None):

    """Creates an Azure Managed Cassandra Datacenter"""

    authentication_method_ldap_properties = AuthenticationMethodLdapProperties(
        server_hostname=server_hostname,
        server_port=server_port,
        service_user_distinguished_name=service_user_distinguished_name,
        service_user_password=service_user_password,
        search_base_distinguished_name=search_base_distinguished_name,
        search_filter_template=search_filter_template,
        server_certificates=server_certificates
    )

    data_center_properties = DataCenterResourceProperties(
        data_center_location=data_center_location,
        delegated_subnet_id=delegated_subnet_id,
        node_count=node_count,
        base64_encoded_cassandra_yaml_fragment=base64_encoded_cassandra_yaml_fragment,
        sku=sku,
        disk_sku=disk_sku,
        disk_capacity=disk_capacity,
        availability_zone=availability_zone,
        managed_disk_customer_key_uri=managed_disk_customer_key_uri,
        backup_storage_customer_key_uri=backup_storage_customer_key_uri,
        authentication_method_ldap_properties=authentication_method_ldap_properties
    )

    data_center_resource = DataCenterResource(
        properties=data_center_properties
    )

    return client.begin_create_update(resource_group_name, cluster_name, data_center_name, data_center_resource)


def cli_cosmosdb_managed_cassandra_datacenter_update(client,
                                                     resource_group_name,
                                                     cluster_name,
                                                     data_center_name,
                                                     node_count=None,
                                                     base64_encoded_cassandra_yaml_fragment=None,
                                                     managed_disk_customer_key_uri=None,
                                                     backup_storage_customer_key_uri=None,
                                                     server_hostname=None,
                                                     server_port=None,
                                                     service_user_distinguished_name=None,
                                                     service_user_password=None,
                                                     search_base_distinguished_name=None,
                                                     search_filter_template=None,
                                                     server_certificates=None):

    """Updates an Azure Managed Cassandra Datacenter"""

    data_center_resource = client.get(resource_group_name, cluster_name, data_center_name)

    if node_count is None:
        node_count = data_center_resource.properties.node_count

    if base64_encoded_cassandra_yaml_fragment is None:
        base64_encoded_cassandra_yaml_fragment = data_center_resource.properties.base64_encoded_cassandra_yaml_fragment

    if managed_disk_customer_key_uri is None:
        managed_disk_customer_key_uri = data_center_resource.properties.managed_disk_customer_key_uri

    if backup_storage_customer_key_uri is None:
        backup_storage_customer_key_uri = data_center_resource.properties.backup_storage_customer_key_uri

    is_ldap_properties_none = False
    if data_center_resource.properties.authentication_method_ldap_properties is None:
        is_ldap_properties_none = True

    if server_hostname is None and is_ldap_properties_none is False:
        server_hostname = data_center_resource.properties.authentication_method_ldap_properties.server_hostname

    if server_port is None and is_ldap_properties_none is False:
        server_port = data_center_resource.properties.authentication_method_ldap_properties.server_port

    if service_user_password is None and is_ldap_properties_none is False:
        service_user_password = data_center_resource.properties.authentication_method_ldap_properties.service_user_password

    if service_user_distinguished_name is None and is_ldap_properties_none is False:
        service_user_distinguished_name = data_center_resource.properties.authentication_method_ldap_properties.service_user_distinguished_name

    if search_base_distinguished_name is None and is_ldap_properties_none is False:
        search_base_distinguished_name = data_center_resource.properties.authentication_method_ldap_properties.search_base_distinguished_name

    if search_filter_template is None and is_ldap_properties_none is False:
        search_filter_template = data_center_resource.properties.authentication_method_ldap_properties.search_filter_template

    if server_certificates is None and is_ldap_properties_none is False:
        server_certificates = data_center_resource.properties.authentication_method_ldap_properties.server_certificates

    authentication_method_ldap_properties = AuthenticationMethodLdapProperties(
        server_hostname=server_hostname,
        server_port=server_port,
        service_user_distinguished_name=service_user_distinguished_name,
        service_user_password=service_user_password,
        search_base_distinguished_name=search_base_distinguished_name,
        search_filter_template=search_filter_template,
        server_certificates=server_certificates
    )

    data_center_properties = DataCenterResourceProperties(
        data_center_location=data_center_resource.properties.data_center_location,
        delegated_subnet_id=data_center_resource.properties.delegated_subnet_id,
        node_count=node_count,
        seed_nodes=data_center_resource.properties.seed_nodes,
        base64_encoded_cassandra_yaml_fragment=base64_encoded_cassandra_yaml_fragment,
        managed_disk_customer_key_uri=managed_disk_customer_key_uri,
        backup_storage_customer_key_uri=backup_storage_customer_key_uri,
        authentication_method_ldap_properties=authentication_method_ldap_properties
    )

    data_center_resource = DataCenterResource(
        properties=data_center_properties
    )

    return client.begin_create_update(resource_group_name, cluster_name, data_center_name, data_center_resource)


def cli_cosmosdb_service_create(client,
                                account_name,
                                resource_group_name,
                                service_kind,
                                service_name,
                                instance_count=1,
                                instance_size="Cosmos.D4s"):
    params = ServiceResourceCreateUpdateParameters(service_type=service_kind,
                                                   instance_count=instance_count,
                                                   instance_size=instance_size)

    return client.begin_create(resource_group_name, account_name, service_name, create_update_parameters=params)


def cli_cosmosdb_service_update(client,
                                account_name,
                                resource_group_name,
                                service_name,
                                service_kind,
                                instance_count,
                                instance_size=None):
    params = ServiceResourceCreateUpdateParameters(service_type=service_kind,
                                                   instance_count=instance_count,
                                                   instance_size=instance_size)

    return client.begin_create(resource_group_name, account_name, service_name, create_update_parameters=params)


def cli_cosmosdb_mongo_role_definition_create(client,
                                              resource_group_name,
                                              account_name,
                                              mongo_role_definition_body):
    '''Creates an Azure Cosmos DB Mongo Role Definition '''
    mongo_role_definition_create_resource = MongoRoleDefinitionCreateUpdateParameters(
        role_name=mongo_role_definition_body['RoleName'],
        type=mongo_role_definition_body['Type'],
        database_name=mongo_role_definition_body['DatabaseName'],
        privileges=mongo_role_definition_body['Privileges'],
        roles=mongo_role_definition_body['Roles'])

    return client.begin_create_update_mongo_role_definition(mongo_role_definition_body['Id'], resource_group_name, account_name, mongo_role_definition_create_resource)


def cli_cosmosdb_mongo_role_definition_update(client,
                                              resource_group_name,
                                              account_name,
                                              mongo_role_definition_body):
    '''Update an existing Azure Cosmos DB Mongo Role Definition'''
    logger.debug('reading Mongo role definition')
    mongo_role_definition = client.get_mongo_role_definition(mongo_role_definition_body['Id'], resource_group_name, account_name)

    if mongo_role_definition_body['RoleName'] != mongo_role_definition.role_name:
        raise InvalidArgumentValueError('Cannot update Mongo Role Definition Name.')

    mongo_role_definition_update_resource = MongoRoleDefinitionCreateUpdateParameters(
        role_name=mongo_role_definition.role_name,
        type=mongo_role_definition_body['Type'],
        database_name=mongo_role_definition_body['DatabaseName'],
        privileges=mongo_role_definition_body['Privileges'],
        roles=mongo_role_definition_body['Roles'])

    return client.begin_create_update_mongo_role_definition(mongo_role_definition_body['Id'], resource_group_name, account_name, mongo_role_definition_update_resource)


def cli_cosmosdb_mongo_role_definition_exists(client,
                                              resource_group_name,
                                              account_name,
                                              mongo_role_definition_id):
    """Checks if an Azure Cosmos DB Mongo Role Definition exists"""
    try:
        client.get_mongo_role_definition(mongo_role_definition_id, resource_group_name, account_name)
    except Exception as ex:
        return _handle_exists_exception(ex.response)

    return True


def cli_cosmosdb_mongo_user_definition_create(client,
                                              resource_group_name,
                                              account_name,
                                              mongo_user_definition_body):
    '''Creates an Azure Cosmos DB Mongo User Definition '''
    mongo_user_definition_create_resource = MongoUserDefinitionCreateUpdateParameters(
        user_name=mongo_user_definition_body['UserName'],
        password=mongo_user_definition_body['Password'],
        database_name=mongo_user_definition_body['DatabaseName'],
        custom_data=mongo_user_definition_body['CustomData'],
        mechanisms=mongo_user_definition_body['Mechanisms'],
        roles=mongo_user_definition_body['Roles'])

    return client.begin_create_update_mongo_user_definition(mongo_user_definition_body['Id'], resource_group_name, account_name, mongo_user_definition_create_resource)


def cli_cosmosdb_mongo_user_definition_update(client,
                                              resource_group_name,
                                              account_name,
                                              mongo_user_definition_body):
    '''Update an existing Azure Cosmos DB Mongo User Definition'''
    logger.debug('reading Mongo user definition')
    try:
        mongo_user_definition = client.get_mongo_user_definition(mongo_user_definition_body['Id'], resource_group_name, account_name)

        mongo_user_definition_update_resource = MongoUserDefinitionCreateUpdateParameters(
            user_name=mongo_user_definition.user_name,
            password=mongo_user_definition_body['Password'],
            database_name=mongo_user_definition_body['DatabaseName'],
            custom_data=mongo_user_definition_body['CustomData'],
            mechanisms=mongo_user_definition_body['Mechanisms'],
            roles=mongo_user_definition_body['Roles'])

        return client.begin_create_update_mongo_user_definition(mongo_user_definition_body['Id'], resource_group_name, account_name, mongo_user_definition_update_resource)
    except Exception as ex:
        return _handle_exists_exception(ex.response)


def cli_cosmosdb_mongo_user_definition_exists(client,
                                              resource_group_name,
                                              account_name,
                                              mongo_user_definition_id):
    """Checks if an Azure Cosmos DB Mongo User Definition exists"""
    try:
        client.get_mongo_user_definition(mongo_user_definition_id, resource_group_name, account_name)
    except Exception as ex:
        return _handle_exists_exception(ex.response)

    return True


def _gen_guid():
    import uuid
    return uuid.uuid4()


# create cosmosdb account with gremlin databases and tables to restore
# pylint: disable=too-many-locals
def cli_cosmosdb_create(cmd,
                        client,
                        resource_group_name,
                        account_name,
                        locations=None,
                        tags=None,
                        kind=DatabaseAccountKind.global_document_db.value,
                        default_consistency_level=None,
                        max_staleness_prefix=100,
                        max_interval=5,
                        ip_range_filter=None,
                        enable_automatic_failover=None,
                        capabilities=None,
                        enable_virtual_network=None,
                        virtual_network_rules=None,
                        enable_multiple_write_locations=None,
                        disable_key_based_metadata_write_access=None,
                        key_uri=None,
                        public_network_access=None,
                        enable_analytical_storage=None,
                        enable_free_tier=None,
                        server_version=None,
                        network_acl_bypass=None,
                        network_acl_bypass_resource_ids=None,
                        backup_interval=None,
                        backup_retention=None,
                        backup_redundancy=None,
                        assign_identity=None,
                        default_identity=None,
                        analytical_storage_schema_type=None,
                        backup_policy_type=None,
                        continuous_tier=None,
                        databases_to_restore=None,
                        gremlin_databases_to_restore=None,
                        tables_to_restore=None,
                        is_restore_request=None,
                        restore_source=None,
                        restore_timestamp=None,
                        enable_materialized_views=None,
                        enable_burst_capacity=None,
                        enable_priority_based_execution=None,
                        default_priority_level=None,
                        enable_prpp_autoscale=None,
                        enable_partition_merge=None):
    """Create a new Azure Cosmos DB database account."""

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)

    rg = resource_client.resource_groups.get(resource_group_name)
    resource_group_location = rg.location  # pylint: disable=no-member

    restore_timestamp_utc = None
    if restore_timestamp is not None:
        restore_timestamp_utc = _convert_to_utc_timestamp(
            restore_timestamp).isoformat()

    return _create_database_account(client=client,
                                    resource_group_name=resource_group_name,
                                    account_name=account_name,
                                    locations=locations,
                                    tags=tags,
                                    kind=kind,
                                    default_consistency_level=default_consistency_level,
                                    max_staleness_prefix=max_staleness_prefix,
                                    max_interval=max_interval,
                                    ip_range_filter=ip_range_filter,
                                    enable_automatic_failover=enable_automatic_failover,
                                    capabilities=capabilities,
                                    enable_virtual_network=enable_virtual_network,
                                    virtual_network_rules=virtual_network_rules,
                                    enable_multiple_write_locations=enable_multiple_write_locations,
                                    disable_key_based_metadata_write_access=disable_key_based_metadata_write_access,
                                    key_uri=key_uri,
                                    public_network_access=public_network_access,
                                    enable_analytical_storage=enable_analytical_storage,
                                    enable_free_tier=enable_free_tier,
                                    server_version=server_version,
                                    network_acl_bypass=network_acl_bypass,
                                    network_acl_bypass_resource_ids=network_acl_bypass_resource_ids,
                                    is_restore_request=is_restore_request,
                                    restore_source=restore_source,
                                    restore_timestamp=restore_timestamp_utc,
                                    analytical_storage_schema_type=analytical_storage_schema_type,
                                    backup_policy_type=backup_policy_type,
                                    continuous_tier=continuous_tier,
                                    backup_interval=backup_interval,
                                    backup_redundancy=backup_redundancy,
                                    assign_identity=assign_identity,
                                    default_identity=default_identity,
                                    backup_retention=backup_retention,
                                    databases_to_restore=databases_to_restore,
                                    gremlin_databases_to_restore=gremlin_databases_to_restore,
                                    tables_to_restore=tables_to_restore,
                                    arm_location=resource_group_location,
                                    enable_materialized_views=enable_materialized_views,
                                    enable_burst_capacity=enable_burst_capacity,
                                    enable_priority_based_execution=enable_priority_based_execution,
                                    default_priority_level=default_priority_level,
                                    enable_prpp_autoscale=enable_prpp_autoscale,
                                    enable_partition_merge=enable_partition_merge)


# pylint: disable=too-many-branches
def cli_cosmosdb_update(client,
                        resource_group_name,
                        account_name,
                        locations=None,
                        tags=None,
                        default_consistency_level=None,
                        max_staleness_prefix=None,
                        max_interval=None,
                        ip_range_filter=None,
                        enable_automatic_failover=None,
                        capabilities=None,
                        enable_virtual_network=None,
                        virtual_network_rules=None,
                        enable_multiple_write_locations=None,
                        disable_key_based_metadata_write_access=None,
                        public_network_access=None,
                        enable_analytical_storage=None,
                        network_acl_bypass=None,
                        network_acl_bypass_resource_ids=None,
                        server_version=None,
                        backup_interval=None,
                        backup_retention=None,
                        backup_redundancy=None,
                        default_identity=None,
                        analytical_storage_schema_type=None,
                        backup_policy_type=None,
                        continuous_tier=None,
                        enable_materialized_views=None,
                        enable_burst_capacity=None,
                        enable_priority_based_execution=None,
                        default_priority_level=None,
                        enable_prpp_autoscale=None,
                        enable_partition_merge=None):
    """Update an existing Azure Cosmos DB database account. """
    existing = client.get(resource_group_name, account_name)

    update_consistency_policy = False
    if max_interval is not None or \
            max_staleness_prefix is not None or \
            default_consistency_level is not None:
        update_consistency_policy = True

    if max_staleness_prefix is None:
        max_staleness_prefix = existing.consistency_policy.max_staleness_prefix

    if max_interval is None:
        max_interval = existing.consistency_policy.max_interval_in_seconds

    if default_consistency_level is None:
        default_consistency_level = existing.consistency_policy.default_consistency_level

    consistency_policy = None
    if update_consistency_policy:
        consistency_policy = ConsistencyPolicy(default_consistency_level=default_consistency_level,
                                               max_staleness_prefix=max_staleness_prefix,
                                               max_interval_in_seconds=max_interval)

    api_properties = {'ServerVersion': server_version}

    backup_policy = None
    if backup_interval is not None or backup_retention is not None or backup_redundancy is not None:
        if isinstance(existing.backup_policy, PeriodicModeBackupPolicy):
            if backup_policy_type is not None and backup_policy_type.lower() == 'continuous':
                raise CLIError('backup-interval and backup-retention can only be set with periodic backup policy.')
            periodic_mode_properties = PeriodicModeProperties(
                backup_interval_in_minutes=backup_interval,
                backup_retention_interval_in_hours=backup_retention,
                backup_storage_redundancy=backup_redundancy
            )
            backup_policy = existing.backup_policy
            backup_policy.periodic_mode_properties = periodic_mode_properties
        else:
            raise CLIError(
                'backup-interval, backup-retention and backup_redundancy can only be set for accounts with periodic backup policy.')  # pylint: disable=line-too-long
    elif backup_policy_type is not None and backup_policy_type.lower() == 'continuous':
        if isinstance(existing.backup_policy, PeriodicModeBackupPolicy):
            backup_policy = ContinuousModeBackupPolicy()
            if continuous_tier is not None:
                continuous_mode_properties = ContinuousModeProperties(
                    tier=continuous_tier
                )
            else:
                continuous_mode_properties = ContinuousModeProperties(
                    tier='Continuous30Days'
                )
            backup_policy.continuous_mode_properties = continuous_mode_properties
        else:
            backup_policy = existing.backup_policy
            if continuous_tier is not None:
                continuous_mode_properties = ContinuousModeProperties(
                    tier=continuous_tier
                )
                backup_policy.continuous_mode_properties = continuous_mode_properties

    analytical_storage_configuration = None
    if analytical_storage_schema_type is not None:
        analytical_storage_configuration = AnalyticalStorageConfiguration()
        analytical_storage_configuration.schema_type = analytical_storage_schema_type

    params = DatabaseAccountUpdateParameters(
        locations=locations,
        tags=tags,
        consistency_policy=consistency_policy,
        ip_rules=ip_range_filter,
        is_virtual_network_filter_enabled=enable_virtual_network,
        enable_automatic_failover=enable_automatic_failover,
        capabilities=capabilities,
        virtual_network_rules=virtual_network_rules,
        enable_multiple_write_locations=enable_multiple_write_locations,
        disable_key_based_metadata_write_access=disable_key_based_metadata_write_access,
        public_network_access=public_network_access,
        enable_analytical_storage=enable_analytical_storage,
        network_acl_bypass=network_acl_bypass,
        network_acl_bypass_resource_ids=network_acl_bypass_resource_ids,
        api_properties=api_properties,
        backup_policy=backup_policy,
        default_identity=default_identity,
        analytical_storage_configuration=analytical_storage_configuration,
        enable_materialized_views=enable_materialized_views,
        enable_burst_capacity=enable_burst_capacity,
        enable_priority_based_execution=enable_priority_based_execution,
        default_priority_level=default_priority_level,
        enable_per_region_per_partition_autoscale=enable_prpp_autoscale,
        enable_partition_merge=enable_partition_merge)

    async_docdb_update = client.begin_update(resource_group_name, account_name, params)
    docdb_account = async_docdb_update.result()
    docdb_account = client.get(resource_group_name, account_name)  # Workaround
    return docdb_account


# pylint: disable=too-many-branches
def cli_cosmosdb_restorable_database_account_list(client,
                                                  location=None,
                                                  account_name=None):
    restorable_database_accounts = None
    if location is not None:
        restorable_database_accounts = client.list_by_location(location)
    else:
        restorable_database_accounts = client.list()

    if account_name is None:
        return restorable_database_accounts

    matching_restorable_accounts = []
    restorable_database_accounts_list = list(restorable_database_accounts)
    for account in restorable_database_accounts_list:
        if account.account_name == account_name:
            matching_restorable_accounts.append(account)
    return matching_restorable_accounts


# pylint: disable=too-many-branches
def cli_cosmosdb_restorable_database_account_get_by_location(client,
                                                             location=None,
                                                             instance_id=None):
    return client.get_by_location(location, instance_id)


# restore cosmosdb account with gremlin databases and tables to restore
# pylint: disable=too-many-statements
def cli_cosmosdb_restore(cmd,
                         client,
                         resource_group_name,
                         account_name,
                         target_database_account_name,
                         restore_timestamp,
                         location,
                         assign_identity=None,
                         default_identity=None,
                         databases_to_restore=None,
                         gremlin_databases_to_restore=None,
                         tables_to_restore=None,
                         public_network_access=None,
                         source_backup_location=None,
                         disable_ttl=None):
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    target_restorable_account = None
    restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)

    # If restore timestamp is timezone aware, get the utcnow as timezone aware as well
    from datetime import datetime, timezone  # pylint: disable=redefined-outer-name,reimported
    current_dateTime = datetime.utcnow()
    if restore_timestamp_datetime_utc.tzinfo is not None and restore_timestamp_datetime_utc.tzinfo.utcoffset(restore_timestamp_datetime_utc) is not None:
        current_dateTime = datetime.now(timezone.utc)

    # Fail if provided restoretimesamp is greater than current timestamp
    if restore_timestamp_datetime_utc > current_dateTime:
        raise CLIError("Restore timestamp {} should be less than current timestamp {}".format(restore_timestamp_datetime_utc, current_dateTime))

    is_source_restorable_account_deleted = False
    for account in restorable_database_accounts_list:
        if account.account_name == account_name:
            if account.deletion_time is not None:
                if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                    target_restorable_account = account
                    is_source_restorable_account_deleted = True
                    break
            else:
                if restore_timestamp_datetime_utc >= account.creation_time:
                    target_restorable_account = account
                    break

    if target_restorable_account is None:
        raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))

    # Validate if source account is empty only for live account restores. For deleted account restores the api will not work
    if not is_source_restorable_account_deleted:
        restorable_resources = None
        api_type = target_restorable_account.api_type.lower()
        arm_location_normalized = target_restorable_account.location.lower().replace(" ", "")
        source_location = location

        if source_backup_location is not None:
            source_location = source_backup_location

        if api_type == "sql":
            try:
                restorable_sql_resources_client = cf_restorable_sql_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_sql_resources_client.list(
                    arm_location_normalized,
                    target_restorable_account.name,
                    source_location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, source_location))
        elif api_type == "mongodb":
            try:
                restorable_mongodb_resources_client = cf_restorable_mongodb_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_mongodb_resources_client.list(
                    arm_location_normalized,
                    target_restorable_account.name,
                    source_location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, source_location))
        elif "sql" in api_type and "gremlin" in api_type:
            try:
                restorable_gremlin_resources_client = cf_restorable_gremlin_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_gremlin_resources_client.list(
                    arm_location_normalized,
                    target_restorable_account.name,
                    source_location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, source_location))
        elif "sql" in api_type and "table" in api_type:
            try:
                restorable_table_resources_client = cf_restorable_table_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_table_resources_client.list(
                    arm_location_normalized,
                    target_restorable_account.name,
                    source_location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, source_location))
        else:
            raise CLIError("Provided API Type {} is not supported for account {}".format(target_restorable_account.api_type, account_name))

        if restorable_resources is None or not any(restorable_resources):
            raise CLIError("Database account {} contains no restorable resources in location {} at given restore timestamp {}".format(target_restorable_account, source_location, restore_timestamp_datetime_utc))

    # Trigger restore
    locations = []
    locations.append(Location(location_name=location, failover_priority=0))

    return _create_database_account(client,
                                    resource_group_name=resource_group_name,
                                    account_name=target_database_account_name,
                                    locations=locations,
                                    assign_identity=assign_identity,
                                    default_identity=default_identity,
                                    is_restore_request=True,
                                    restore_source=target_restorable_account.id,
                                    restore_timestamp=restore_timestamp_datetime_utc.isoformat(),
                                    databases_to_restore=databases_to_restore,
                                    gremlin_databases_to_restore=gremlin_databases_to_restore,
                                    tables_to_restore=tables_to_restore,
                                    arm_location=target_restorable_account.location,
                                    public_network_access=public_network_access,
                                    source_backup_location=source_backup_location,
                                    disable_ttl=disable_ttl)


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def _create_database_account(client,
                             resource_group_name,
                             account_name,
                             locations=None,
                             tags=None,
                             kind=DatabaseAccountKind.global_document_db.value,
                             default_consistency_level=None,
                             max_staleness_prefix=100,
                             max_interval=5,
                             ip_range_filter=None,
                             enable_automatic_failover=None,
                             capabilities=None,
                             enable_virtual_network=None,
                             virtual_network_rules=None,
                             enable_multiple_write_locations=None,
                             disable_key_based_metadata_write_access=None,
                             key_uri=None,
                             public_network_access=None,
                             enable_analytical_storage=None,
                             enable_free_tier=None,
                             server_version=None,
                             network_acl_bypass=None,
                             network_acl_bypass_resource_ids=None,
                             backup_interval=None,
                             backup_retention=None,
                             backup_redundancy=None,
                             assign_identity=None,
                             default_identity=None,
                             backup_policy_type=None,
                             continuous_tier=None,
                             analytical_storage_schema_type=None,
                             databases_to_restore=None,
                             gremlin_databases_to_restore=None,
                             tables_to_restore=None,
                             is_restore_request=None,
                             restore_source=None,
                             restore_timestamp=None,
                             arm_location=None,
                             enable_materialized_views=None,
                             enable_burst_capacity=None,
                             source_backup_location=None,
                             enable_priority_based_execution=None,
                             default_priority_level=None,
                             enable_prpp_autoscale=None,
                             disable_ttl=None,
                             enable_partition_merge=None):
    consistency_policy = None
    if default_consistency_level is not None:
        consistency_policy = ConsistencyPolicy(default_consistency_level=default_consistency_level,
                                               max_staleness_prefix=max_staleness_prefix,
                                               max_interval_in_seconds=max_interval)

    if not locations:
        locations = []
        locations.append(Location(location_name=arm_location, failover_priority=0, is_zone_redundant=False))

    managed_service_identity = None
    SYSTEM_ID = '[system]'
    enable_system = False
    if assign_identity is not None:
        if assign_identity == [] or (len(assign_identity) == 1 and assign_identity[0] == '[system]'):
            enable_system = True
            managed_service_identity = ManagedServiceIdentity(type=ResourceIdentityType.system_assigned.value)
        else:
            user_identities = {}
            for x in assign_identity:
                if x != SYSTEM_ID:
                    user_identities[x] = ManagedServiceIdentityUserAssignedIdentity()  # pylint: disable=line-too-long
                else:
                    enable_system = True
            if enable_system:
                managed_service_identity = ManagedServiceIdentity(
                    type=ResourceIdentityType.system_assigned_user_assigned.value,
                    user_assigned_identities=user_identities
                )
            else:
                managed_service_identity = ManagedServiceIdentity(
                    type=ResourceIdentityType.user_assigned.value,
                    user_assigned_identities=user_identities
                )

    api_properties = {}
    if kind == DatabaseAccountKind.mongo_db.value:
        api_properties['ServerVersion'] = server_version
    elif server_version is not None:
        raise CLIError('server-version is a valid argument only when kind is MongoDB.')

    backup_policy = None
    if backup_policy_type is not None:
        if backup_policy_type.lower() == 'periodic':
            backup_policy = PeriodicModeBackupPolicy()
            if backup_interval is not None or backup_retention is not None or backup_redundancy is not None:
                periodic_mode_properties = PeriodicModeProperties(
                    backup_interval_in_minutes=backup_interval,
                    backup_retention_interval_in_hours=backup_retention,
                    backup_storage_redundancy=backup_redundancy
                )
                backup_policy.periodic_mode_properties = periodic_mode_properties
        elif backup_policy_type.lower() == 'continuous':
            backup_policy = ContinuousModeBackupPolicy()
            if continuous_tier is not None:
                continuous_mode_properties = ContinuousModeProperties(
                    tier=continuous_tier
                )
            else:
                continuous_mode_properties = ContinuousModeProperties(
                    tier='Continuous30Days'
                )
            backup_policy.continuous_mode_properties = continuous_mode_properties
        else:
            raise CLIError('backup-policy-type argument is invalid.')

    elif backup_interval is not None or backup_retention is not None:
        backup_policy = PeriodicModeBackupPolicy()
        periodic_mode_properties = PeriodicModeProperties(
            backup_interval_in_minutes=backup_interval,
            backup_retention_interval_in_hours=backup_retention
        )
        backup_policy.periodic_mode_properties = periodic_mode_properties

    analytical_storage_configuration = None
    if analytical_storage_schema_type is not None:
        analytical_storage_configuration = AnalyticalStorageConfiguration()
        analytical_storage_configuration.schema_type = analytical_storage_schema_type

    create_mode = CreateMode.restore.value if is_restore_request else CreateMode.default.value
    params = None
    restore_parameters = None
    if create_mode == 'Restore':
        if restore_source is None or restore_timestamp is None:
            raise CLIError('restore-source and restore-timestamp should be provided for a restore request.')

        restore_parameters = RestoreParameters(
            restore_mode='PointInTime',
            restore_source=restore_source,
            restore_timestamp_in_utc=restore_timestamp
        )

        if databases_to_restore is not None:
            restore_parameters.databases_to_restore = databases_to_restore

        if gremlin_databases_to_restore is not None:
            restore_parameters.gremlin_databases_to_restore = gremlin_databases_to_restore

        if tables_to_restore is not None:
            restore_parameters.tables_to_restore = tables_to_restore

        if source_backup_location is not None:
            restore_parameters.source_backup_location = source_backup_location

        if disable_ttl is not None:
            restore_parameters.restore_with_ttl_disabled = disable_ttl

    params = DatabaseAccountCreateUpdateParameters(
        location=arm_location,
        locations=locations,
        tags=tags,
        kind=kind,
        consistency_policy=consistency_policy,
        ip_rules=ip_range_filter,
        is_virtual_network_filter_enabled=enable_virtual_network,
        enable_automatic_failover=enable_automatic_failover,
        capabilities=capabilities,
        virtual_network_rules=virtual_network_rules,
        enable_multiple_write_locations=enable_multiple_write_locations,
        disable_key_based_metadata_write_access=disable_key_based_metadata_write_access,
        key_vault_key_uri=key_uri,
        public_network_access=public_network_access,
        api_properties=api_properties,
        enable_analytical_storage=enable_analytical_storage,
        enable_free_tier=enable_free_tier,
        network_acl_bypass=network_acl_bypass,
        network_acl_bypass_resource_ids=network_acl_bypass_resource_ids,
        backup_policy=backup_policy,
        identity=managed_service_identity,
        default_identity=default_identity,
        analytical_storage_configuration=analytical_storage_configuration,
        create_mode=create_mode,
        restore_parameters=restore_parameters,
        enable_materialized_views=enable_materialized_views,
        enable_burst_capacity=enable_burst_capacity,
        enable_priority_based_execution=enable_priority_based_execution,
        default_priority_level=default_priority_level,
        enable_per_region_per_partition_autoscale=enable_prpp_autoscale,
        enable_partition_merge=enable_partition_merge
    )

    async_docdb_create = client.begin_create_or_update(resource_group_name, account_name, params)
    docdb_account = async_docdb_create.result()
    docdb_account = client.get(resource_group_name, account_name)  # Workaround
    return docdb_account


def cli_cosmosdb_list(client, resource_group_name=None):
    """ Lists all Azure Cosmos DB database accounts within a given resource group or subscription. """
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)

    return client.list()


# latest restorable timestamp for gremlin graph and table
def cli_gremlin_retrieve_latest_backup_time(client,
                                            resource_group_name,
                                            account_name,
                                            database_name,
                                            graph_name,
                                            location):
    try:
        client.get_gremlin_database(resource_group_name, account_name, database_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Database with name '{}' could not be found.".format(database_name))
        raise CLIError("{}".format(str(ex)))

    try:
        client.get_gremlin_graph(resource_group_name, account_name, database_name, graph_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Graph with name '{}' under database '{}' could not be found.".format(graph_name, database_name))
        raise CLIError("{}".format(str(ex)))

    restoreLocation = ContinuousBackupRestoreLocation(
        location=location
    )

    asyc_backupInfo = client.begin_retrieve_continuous_backup_information(resource_group_name,
                                                                          account_name,
                                                                          database_name,
                                                                          graph_name,
                                                                          restoreLocation)
    return asyc_backupInfo.result()


def cli_table_retrieve_latest_backup_time(client,
                                          resource_group_name,
                                          account_name,
                                          table_name,
                                          location):
    try:
        client.get_table(resource_group_name, account_name, table_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Table with name '{}' could not be found.".format(table_name))
        raise CLIError("{}".format(str(ex)))

    restoreLocation = ContinuousBackupRestoreLocation(
        location=location
    )

    asyc_backupInfo = client.begin_retrieve_continuous_backup_information(resource_group_name,
                                                                          account_name,
                                                                          table_name,
                                                                          restoreLocation)
    return asyc_backupInfo.result()


def cli_cosmosdb_sql_container_create(client,
                                      resource_group_name,
                                      account_name,
                                      database_name,
                                      container_name,
                                      partition_key_path,
                                      partition_key_version=None,
                                      default_ttl=None,
                                      indexing_policy=DEFAULT_INDEXING_POLICY,
                                      client_encryption_policy=None,
                                      throughput=None,
                                      max_throughput=None,
                                      unique_key_policy=None,
                                      conflict_resolution_policy=None,
                                      analytical_storage_ttl=None,
                                      materialized_view_definition=None):
    """Creates an Azure Cosmos DB SQL container """
    sql_container_resource = SqlContainerResource(id=container_name)

    _populate_sql_container_definition(sql_container_resource,
                                       partition_key_path,
                                       default_ttl,
                                       indexing_policy,
                                       unique_key_policy,
                                       client_encryption_policy,
                                       partition_key_version,
                                       conflict_resolution_policy,
                                       analytical_storage_ttl,
                                       materialized_view_definition)

    options = _get_options(throughput, max_throughput)

    sql_container_create_update_resource = SqlContainerCreateUpdateParameters(
        resource=sql_container_resource,
        options=options)

    return client.begin_create_update_sql_container(resource_group_name,
                                                    account_name,
                                                    database_name,
                                                    container_name,
                                                    sql_container_create_update_resource)


def _populate_sql_container_definition(sql_container_resource,
                                       partition_key_path,
                                       default_ttl,
                                       indexing_policy,
                                       unique_key_policy,
                                       client_encryption_policy,
                                       partition_key_version,
                                       conflict_resolution_policy,
                                       analytical_storage_ttl,
                                       materialized_view_definition):
    if all(arg is None for arg in
           [partition_key_path, partition_key_version, default_ttl, indexing_policy, unique_key_policy, client_encryption_policy, conflict_resolution_policy, analytical_storage_ttl, materialized_view_definition]):
        return False

    if partition_key_path is not None:
        container_partition_key = ContainerPartitionKey()
        container_partition_key.paths = [partition_key_path]
        container_partition_key.kind = 'Hash'
        if partition_key_version is not None:
            container_partition_key.version = partition_key_version
        sql_container_resource.partition_key = container_partition_key

    if default_ttl is not None:
        sql_container_resource.default_ttl = default_ttl

    if indexing_policy is not None:
        sql_container_resource.indexing_policy = indexing_policy

    if unique_key_policy is not None:
        sql_container_resource.unique_key_policy = unique_key_policy

    if client_encryption_policy is not None:
        sql_container_resource.client_encryption_policy = client_encryption_policy

    if conflict_resolution_policy is not None:
        sql_container_resource.conflict_resolution_policy = conflict_resolution_policy

    if analytical_storage_ttl is not None:
        sql_container_resource.analytical_storage_ttl = analytical_storage_ttl

    if materialized_view_definition is not None:
        sql_container_resource.materialized_view_definition = materialized_view_definition

    return True


def _get_options(throughput=None, max_throughput=None):
    options = {}
    if throughput and max_throughput:
        raise CLIError("Please provide max-throughput if your resource is autoscale enabled otherwise provide throughput.")
    if throughput:
        options['throughput'] = throughput
    if max_throughput:
        options['autoscaleSettings'] = AutoscaleSettings(max_throughput=max_throughput)
    return options


def cli_cosmosdb_sql_container_update(client,
                                      resource_group_name,
                                      account_name,
                                      database_name,
                                      container_name,
                                      default_ttl=None,
                                      indexing_policy=None,
                                      analytical_storage_ttl=None,
                                      materialized_view_definition=None):
    """Updates an Azure Cosmos DB SQL container """
    logger.debug('reading SQL container')
    sql_container = client.get_sql_container(resource_group_name, account_name, database_name, container_name)

    sql_container_resource = SqlContainerResource(id=container_name)
    sql_container_resource.partition_key = sql_container.resource.partition_key
    sql_container_resource.indexing_policy = sql_container.resource.indexing_policy
    sql_container_resource.default_ttl = sql_container.resource.default_ttl
    sql_container_resource.unique_key_policy = sql_container.resource.unique_key_policy
    sql_container_resource.conflict_resolution_policy = sql_container.resource.conflict_resolution_policy
    sql_container_resource.materialized_view_definition = materialized_view_definition

    # client encryption policy is immutable
    sql_container_resource.client_encryption_policy = sql_container.resource.client_encryption_policy

    if _populate_sql_container_definition(sql_container_resource,
                                          None,
                                          default_ttl,
                                          indexing_policy,
                                          None,
                                          None,
                                          None,
                                          None,
                                          analytical_storage_ttl,
                                          materialized_view_definition):
        logger.debug('replacing SQL container')

    sql_container_create_update_resource = SqlContainerCreateUpdateParameters(
        resource=sql_container_resource,
        options={})

    return client.begin_create_update_sql_container(resource_group_name,
                                                    account_name,
                                                    database_name,
                                                    container_name,
                                                    sql_container_create_update_resource)


def cosmosdb_data_transfer_copy_job(client,
                                    resource_group_name,
                                    account_name,
                                    source_cassandra_table=None,
                                    dest_cassandra_table=None,
                                    source_sql_container=None,
                                    dest_sql_container=None,
                                    source_mongo=None,
                                    dest_mongo=None,
                                    worker_count=0,
                                    job_name=None):
    job_create_properties = {}

    source = None
    if source_cassandra_table is not None:
        if source is not None:
            raise CLIError('Invalid input: multiple source components')
        source = source_cassandra_table

    if source_sql_container is not None:
        if source is not None:
            raise CLIError('Invalid input: multiple source components')
        source = source_sql_container

    if source_mongo is not None:
        if source is not None:
            raise CLIError('Invalid input: multiple source components')
        source = source_mongo

    if source is None:
        raise CLIError('source component is missing')
    job_create_properties['source'] = source

    destination = None
    if dest_cassandra_table is not None:
        if destination is not None:
            raise CLIError('Invalid input: multiple destination components')
        destination = dest_cassandra_table

    if dest_sql_container is not None:
        if destination is not None:
            raise CLIError('Invalid input: multiple destination components')
        destination = dest_sql_container

    if dest_mongo is not None:
        if destination is not None:
            raise CLIError('Invalid input: multiple destination components')
        destination = dest_mongo

    if destination is None:
        raise CLIError('destination component is missing')
    job_create_properties['destination'] = destination

    if worker_count > 0:
        job_create_properties['worker_count'] = worker_count

    job_create_parameters = {}
    job_create_parameters['properties'] = job_create_properties

    if job_name is None:
        job_name = _gen_guid()

    return client.create(resource_group_name=resource_group_name,
                         account_name=account_name,
                         job_name=job_name,
                         job_create_parameters=job_create_parameters)


def cosmosdb_copy_job(client,
                      resource_group_name,
                      dest_account,
                      src_account,
                      src_cassandra=None,
                      dest_cassandra=None,
                      src_nosql=None,
                      dest_nosql=None,
                      src_mongo=None,
                      dest_mongo=None,
                      job_name=None,
                      worker_count=0,
                      host_copy_on_src=False,
                      mode="Offline"):
    job_create_properties = {}
    is_cross_account = src_account != dest_account
    remote_account_name = dest_account if host_copy_on_src else src_account

    source = None
    if src_cassandra is not None:
        if source is not None:
            raise CLIError('Invalid input: multiple source components')
        if is_cross_account and not host_copy_on_src:
            source = CosmosCassandraDataTransferDataSourceSink(keyspace_name=src_cassandra.keyspace_name, table_name=src_cassandra.table_name, remote_account_name=remote_account_name)
        else:
            source = src_cassandra

    if src_nosql is not None:
        if source is not None:
            raise CLIError('Invalid input: multiple source components')
        if is_cross_account and not host_copy_on_src:
            source = CosmosSqlDataTransferDataSourceSink(database_name=src_nosql.database_name, container_name=src_nosql.container_name, remote_account_name=remote_account_name)
        else:
            source = src_nosql

    if src_mongo is not None:
        if source is not None:
            raise CLIError('Invalid input: multiple source components')
        if is_cross_account and not host_copy_on_src:
            source = CosmosMongoDataTransferDataSourceSink(database_name=src_mongo.database_name, collection_name=src_mongo.collection_name, remote_account_name=remote_account_name)
        else:
            source = src_mongo

    if source is None:
        raise CLIError('source component is missing')
    job_create_properties['source'] = source

    destination = None
    if dest_cassandra is not None:
        if destination is not None:
            raise CLIError('Invalid input: multiple destination components')
        destination = dest_cassandra
        if is_cross_account and host_copy_on_src:
            destination = CosmosCassandraDataTransferDataSourceSink(keyspace_name=dest_cassandra.keyspace_name, table_name=dest_cassandra.table_name, remote_account_name=remote_account_name)
        else:
            destination = dest_cassandra

    if dest_nosql is not None:
        if destination is not None:
            raise CLIError('Invalid input: multiple destination components')
        if is_cross_account and host_copy_on_src:
            destination = CosmosSqlDataTransferDataSourceSink(database_name=dest_nosql.database_name, container_name=dest_nosql.container_name, remote_account_name=remote_account_name)
        else:
            destination = dest_nosql

    if dest_mongo is not None:
        if destination is not None:
            raise CLIError('Invalid input: multiple destination components')
        if is_cross_account and host_copy_on_src:
            destination = CosmosMongoDataTransferDataSourceSink(database_name=dest_mongo.database_name, collection_name=dest_mongo.collection_name, remote_account_name=remote_account_name)
        else:
            destination = dest_mongo

    if destination is None:
        raise CLIError('destination component is missing')
    job_create_properties['destination'] = destination

    if worker_count > 0:
        job_create_properties['worker_count'] = worker_count

    job_create_properties['mode'] = mode

    job_create_parameters = {}
    job_create_parameters['properties'] = job_create_properties

    if job_name is None:
        job_name = _gen_guid()

    host_account_name = src_account if host_copy_on_src else dest_account

    return client.create(resource_group_name=resource_group_name,
                         account_name=host_account_name,
                         job_name=job_name,
                         job_create_parameters=job_create_parameters)


def cli_begin_list_sql_container_partition_merge(client,
                                                 resource_group_name,
                                                 account_name,
                                                 database_name,
                                                 container_name):

    try:
        client.get_sql_container(resource_group_name, account_name, database_name, container_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Container with name '{}' in database '{}' could not be found.".format(container_name, database_name))
        raise CLIError("{}".format(str(ex)))

    mergeParameters = MergeParameters(is_dry_run=False)

    async_partition_merge_result = client.begin_list_sql_container_partition_merge(resource_group_name=resource_group_name,
                                                                                   account_name=account_name,
                                                                                   database_name=database_name,
                                                                                   container_name=container_name,
                                                                                   merge_parameters=mergeParameters)

    return async_partition_merge_result.result()


def cli_begin_list_mongo_db_collection_partition_merge(client,
                                                       resource_group_name,
                                                       account_name,
                                                       database_name,
                                                       container_name):

    try:
        client.get_mongo_db_collection(resource_group_name, account_name, database_name, container_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) collection with name '{}' in mongodb '{}' could not be found.".format(container_name, database_name))
        raise CLIError("{}".format(str(ex)))

    mergeParameters = MergeParameters(is_dry_run=False)

    async_partition_merge_result = client.begin_list_mongo_db_collection_partition_merge(resource_group_name=resource_group_name,
                                                                                         account_name=account_name,
                                                                                         database_name=database_name,
                                                                                         collection_name=container_name,
                                                                                         merge_parameters=mergeParameters)

    return async_partition_merge_result.result()


def cli_begin_sql_database_partition_merge(client,
                                           resource_group_name,
                                           account_name,
                                           database_name):

    try:
        client.get_sql_database(resource_group_name, account_name, database_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Database with name '{}' in account '{}' could not be found.".format(database_name, account_name))
        raise CLIError("{}".format(str(ex)))

    mergeParameters = MergeParameters(is_dry_run=False)

    async_partition_merge_result = client.begin_sql_database_partition_merge(resource_group_name=resource_group_name,
                                                                             account_name=account_name,
                                                                             database_name=database_name,
                                                                             merge_parameters=mergeParameters)

    return async_partition_merge_result.result()


def cli_begin_mongo_db_database_partition_merge(client,
                                                resource_group_name,
                                                account_name,
                                                database_name):

    try:
        client.get_mongo_db_database(resource_group_name, account_name, database_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Database with name '{}' in account '{}' could not be found.".format(database_name, account_name))
        raise CLIError("{}".format(str(ex)))

    mergeParameters = MergeParameters(is_dry_run=False)

    async_partition_merge_result = client.begin_mongo_db_database_partition_merge(resource_group_name=resource_group_name,
                                                                                  account_name=account_name,
                                                                                  database_name=database_name,
                                                                                  merge_parameters=mergeParameters)

    return async_partition_merge_result.result()


def _handle_exists_exception(http_response_error):
    if http_response_error.status_code == 404:
        return False
    raise http_response_error


def process_restorable_databases(restorable_databases, database_name):
    latest_database_delete_time = datetime.datetime.utcfromtimestamp(0)
    latest_database_create_or_recreate_time = datetime.datetime.utcfromtimestamp(0)
    database_rid = None

    for restorable_database in restorable_databases:
        resource = restorable_database.resource
        if resource.owner_id == database_name:
            database_rid = resource.owner_resource_id
            event_timestamp = datetime.datetime.strptime(resource.event_timestamp, "%Y-%m-%dT%H:%M:%SZ")
            if resource.operation_type == "Delete" and latest_database_delete_time < event_timestamp:
                latest_database_delete_time = event_timestamp

            if (resource.operation_type in ('Create', 'Recreate')) and latest_database_create_or_recreate_time < event_timestamp:
                latest_database_create_or_recreate_time = event_timestamp

    if database_rid is None:
        raise CLIError("No restorable database found with name: {}".format(database_name))

    # Database never deleted then reset it to max time
    latest_database_delete_time = datetime.datetime.max if latest_database_delete_time == datetime.datetime.utcfromtimestamp(0) else latest_database_delete_time

    logger.debug('process_restorable_databases: latest_database_delete_time {} latest_database_create_or_recreate_time {} database_name {}'.format(latest_database_delete_time, latest_database_create_or_recreate_time, database_name))  # pylint: disable=logging-format-interpolation

    return latest_database_delete_time, latest_database_create_or_recreate_time, database_rid


def process_restorable_collections(restorable_collections, collection_name, database_name):
    latest_collection_delete_time = datetime.datetime.utcfromtimestamp(0)
    latest_collection_create_or_recreate_time = datetime.datetime.utcfromtimestamp(0)
    collection_rid = None

    for restorable_collection in restorable_collections:
        resource = restorable_collection.resource
        if resource.owner_id == collection_name:
            collection_rid = resource.owner_resource_id
            event_timestamp = datetime.datetime.strptime(resource.event_timestamp, "%Y-%m-%dT%H:%M:%SZ")
            if resource.operation_type == "Delete" and latest_collection_delete_time < event_timestamp:
                latest_collection_delete_time = event_timestamp

            if (resource.operation_type in ('Create', 'Recreate')) and latest_collection_create_or_recreate_time < event_timestamp:
                latest_collection_create_or_recreate_time = event_timestamp

    if collection_rid is None:
        raise CLIError("No restorable collection with name: {} found in the database with name: {}".format(collection_name, database_name))

    # Collection never deleted then reset it to max time
    latest_collection_delete_time = datetime.datetime.max if latest_collection_delete_time == datetime.datetime.utcfromtimestamp(0) else latest_collection_delete_time

    logger.debug('process_restorable_databases: latest_collection_delete_time {} latest_collection_create_or_recreate_time {} database_name {} collection_name {}'.format(latest_collection_delete_time, latest_collection_create_or_recreate_time, database_name, collection_name))  # pylint: disable=logging-format-interpolation

    return latest_collection_delete_time, latest_collection_create_or_recreate_time


def cli_cosmosdb_sql_database_restore(cmd,
                                      client,
                                      resource_group_name,
                                      account_name,
                                      database_name,
                                      restore_timestamp=None,
                                      disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted database account {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online".format(account_name))

        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_sql_databases
            restorable_databases_client = cf_restorable_sql_databases(cmd.cli_ctx, [])
            restorable_databases = restorable_databases_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_database_delete_time, latest_database_create_or_recreate_time, database_rid = process_restorable_databases(restorable_databases, database_name)  # pylint: disable=unused-variable

            # Database is alive if create or recreate timestamp is later than latest delete timestamp
            database_alive = latest_database_create_or_recreate_time > latest_database_delete_time or latest_database_delete_time == datetime.datetime.max

            if database_alive:
                raise CLIError("Database with name {} already exists in this account with name {} in location {}".format(database_name, account_name, restorable_database_account.location))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_database_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a database account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB SQL database"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    sql_database_resource = SqlDatabaseCreateUpdateParameters(
        resource=SqlDatabaseResource(
            id=database_name,
            create_mode=create_mode,
            restore_parameters=restore_parameters)
    )

    return client.begin_create_update_sql_database(resource_group_name,
                                                   account_name,
                                                   database_name,
                                                   sql_database_resource)


def cli_cosmosdb_sql_container_restore(cmd,
                                       client,
                                       resource_group_name,
                                       account_name,
                                       database_name,
                                       container_name,
                                       restore_timestamp=None,
                                       disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    # """Restores the deleted Azure Cosmos DB SQL container """
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted database account {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore
        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online".format(account_name))

        database_rid = None

        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_sql_databases
            restorable_databases_client = cf_restorable_sql_databases(cmd.cli_ctx, [])
            restorable_databases = restorable_databases_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_database_delete_time, latest_database_create_or_recreate_time, database_rid = process_restorable_databases(restorable_databases, database_name)

            # Database is alive if create or recreate timestamp is later than latest delete timestamp
            database_alive = latest_database_delete_time == datetime.datetime.max or latest_database_create_or_recreate_time > latest_database_delete_time

            if not database_alive:
                raise CLIError("No active database with name {} found that contains the collection {}".format(database_name, container_name))

            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_sql_containers
            restorable_containers_client = cf_restorable_sql_containers(cmd.cli_ctx, [])
            restorable_containers = restorable_containers_client.list(
                restorable_database_account.location,
                restorable_database_account.name,
                database_rid)

            latest_container_delete_time, latest_container_create_or_recreate_time = process_restorable_collections(restorable_containers, container_name, database_name)

            # Container is alive if create or recreate timestamp is later than latest delete timestamp
            container_alive = latest_container_create_or_recreate_time > latest_container_delete_time or latest_container_delete_time == datetime.datetime.max

            if container_alive:
                raise CLIError("The collection {} is currently online. Please delete the collection and provide a restore timestamp for restoring different instance of the collection.".format(container_name))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_container_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a database account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB SQL container"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    sql_container_resource = SqlContainerResource(
        id=container_name,
        create_mode=create_mode,
        restore_parameters=restore_parameters)

    sql_container_create_update_resource = SqlContainerCreateUpdateParameters(
        resource=sql_container_resource,
        options={})

    return client.begin_create_update_sql_container(resource_group_name,
                                                    account_name,
                                                    database_name,
                                                    container_name,
                                                    sql_container_create_update_resource)


def cli_cosmosdb_mongodb_database_restore(cmd,
                                          client,
                                          resource_group_name,
                                          account_name,
                                          database_name,
                                          restore_timestamp=None,
                                          disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    # """Restores the deleted Azure Cosmos DB MongoDB database"""
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted database account {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online".format(account_name))

        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_mongodb_databases
            restorable_databases_client = cf_restorable_mongodb_databases(cmd.cli_ctx, [])
            restorable_databases = restorable_databases_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_database_delete_time, latest_database_create_or_recreate_time, database_rid = process_restorable_databases(restorable_databases, database_name)  # pylint: disable=unused-variable

            # Database is alive if create or recreate timestamp is later than latest delete timestamp
            database_alive = latest_database_create_or_recreate_time > latest_database_delete_time or latest_database_delete_time == datetime.datetime.max

            if database_alive:
                raise CLIError("Database with name {} already exists in this account with name {} in location {}".format(database_name, account_name, restorable_database_account.location))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_database_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a database account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB MongoDB database"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    mongodb_database_resource = MongoDBDatabaseCreateUpdateParameters(
        resource=MongoDBDatabaseResource(id=database_name,
                                         create_mode=create_mode,
                                         restore_parameters=restore_parameters),
        options={})

    return client.begin_create_update_mongo_db_database(resource_group_name,
                                                        account_name,
                                                        database_name,
                                                        mongodb_database_resource)


def cli_cosmosdb_mongodb_collection_restore(cmd,
                                            client,
                                            resource_group_name,
                                            account_name,
                                            database_name,
                                            collection_name,
                                            restore_timestamp=None,
                                            disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    # """Restores the Azure Cosmos DB MongoDB collection """
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted database account {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online".format(account_name))

        database_rid = None
        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_mongodb_databases
            restorable_databases_client = cf_restorable_mongodb_databases(cmd.cli_ctx, [])
            restorable_databases = restorable_databases_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_database_delete_time, latest_database_create_or_recreate_time, database_rid = process_restorable_databases(restorable_databases, database_name)

            # Database is alive if create or recreate timestamp is later than latest delete timestamp
            database_alive = latest_database_delete_time == datetime.datetime.max or latest_database_create_or_recreate_time > latest_database_delete_time

            if not database_alive:
                raise CLIError("Cannot find a database account with name {} that is online when latest collection instance was deleted".format(account_name))

            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_mongodb_collections
            restorable_collections_client = cf_restorable_mongodb_collections(cmd.cli_ctx, [])
            restorable_collections = restorable_collections_client.list(
                restorable_database_account.location,
                restorable_database_account.name,
                database_rid)

            latest_collection_delete_time, latest_collection_create_or_recreate_time = process_restorable_collections(restorable_collections, collection_name, database_name)

            # Collection is alive if create or recreate timestamp is later than latest delete timestamp
            collection_alive = latest_collection_create_or_recreate_time > latest_collection_delete_time or latest_collection_delete_time == datetime.datetime.max

            if collection_alive:
                raise CLIError("The collection {} is currently online. Please delete the collection and provide a restore timestamp for restoring different instance of the collection.".format(collection_name))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_collection_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a database account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB MongoDB collection"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    mongodb_collection_resource = MongoDBCollectionResource(id=collection_name,
                                                            create_mode=create_mode,
                                                            restore_parameters=restore_parameters
                                                            )

    mongodb_collection_create_update_resource = MongoDBCollectionCreateUpdateParameters(
        resource=mongodb_collection_resource,
        options={})

    return client.begin_create_update_mongo_db_collection(resource_group_name,
                                                          account_name,
                                                          database_name,
                                                          collection_name,
                                                          mongodb_collection_create_update_resource)


# pylint: disable=dangerous-default-value
def cli_begin_retrieve_sql_container_partition_throughput(client,
                                                          resource_group_name,
                                                          account_name,
                                                          database_name,
                                                          container_name,
                                                          physical_partition_ids=[],
                                                          all_partitions=False):

    try:
        client.get_sql_container(
            resource_group_name, account_name, database_name, container_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Container with name '{}' in database '{} could not be found.".format(container_name, database_name))

    if len(physical_partition_ids) == 0 and all_partitions is False:
        raise CLIError(
            'Either of --physical-partition-ids/--all-partitions needs to be specified.')

    if len(physical_partition_ids) > 0 and all_partitions:
        raise CLIError(
            'Both --physical-partition-ids and --all-partitions cannot be specified together.')

    if all_partitions is True:
        physical_partition_ids = [PhysicalPartitionId(id='-1')]

    retrieve_throughput_properties_resource = RetrieveThroughputPropertiesResource(
        physical_partition_ids=physical_partition_ids
    )

    retrieve_throughput_parameters = RetrieveThroughputParameters(
        resource=retrieve_throughput_properties_resource
    )

    async_partition_retrieve_throughput_result = client.begin_sql_container_retrieve_throughput_distribution(resource_group_name=resource_group_name,
                                                                                                             account_name=account_name,
                                                                                                             database_name=database_name,
                                                                                                             container_name=container_name,
                                                                                                             retrieve_throughput_parameters=retrieve_throughput_parameters)

    return async_partition_retrieve_throughput_result.result()


# pylint: disable=dangerous-default-value
def cli_begin_redistribute_sql_container_partition_throughput(client,
                                                              resource_group_name,
                                                              account_name,
                                                              database_name,
                                                              container_name,
                                                              evenly_distribute=False,
                                                              target_partition_info=[],
                                                              source_partition_info=[]):

    try:
        client.get_sql_container(
            resource_group_name, account_name, database_name, container_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Container with name '{}' in database '{} could not be found.".format(container_name, database_name))

    if evenly_distribute:
        redistribute_throughput_properties_resource = RedistributeThroughputPropertiesResource(
            throughput_policy=ThroughputPolicyType.EQUAL,
            target_physical_partition_throughput_info=[],
            source_physical_partition_throughput_info=[])
    else:
        redistribute_throughput_properties_resource = RedistributeThroughputPropertiesResource(
            throughput_policy=ThroughputPolicyType.CUSTOM,
            target_physical_partition_throughput_info=target_partition_info,
            source_physical_partition_throughput_info=source_partition_info
        )

    redistribute_throughput_parameters = RedistributeThroughputParameters(
        resource=redistribute_throughput_properties_resource
    )

    async_partition_redistribute_throughput_result = client.begin_sql_container_redistribute_throughput(resource_group_name=resource_group_name,
                                                                                                        account_name=account_name,
                                                                                                        database_name=database_name,
                                                                                                        container_name=container_name,
                                                                                                        redistribute_throughput_parameters=redistribute_throughput_parameters)

    return async_partition_redistribute_throughput_result.result()


# pylint: disable=dangerous-default-value
def cli_begin_retrieve_mongo_container_partition_throughput(client,
                                                            resource_group_name,
                                                            account_name,
                                                            database_name,
                                                            collection_name,
                                                            physical_partition_ids=[],
                                                            all_partitions=False):

    try:
        client.get_mongo_db_collection(
            resource_group_name, account_name, database_name, collection_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Container with name '{}' in database '{} could not be found.".format(collection_name, database_name))

    if len(physical_partition_ids) == 0 and all_partitions is False:
        raise CLIError(
            'Either of --physical-partition-ids/--all-partitions needs to be specified.')

    if len(physical_partition_ids) > 0 and all_partitions:
        raise CLIError(
            'Both --physical-partition-ids and --all-partitions cannot be specified together.')

    if all_partitions is True:
        physical_partition_ids = [PhysicalPartitionId(id='-1')]

    retrieve_throughput_properties_resource = RetrieveThroughputPropertiesResource(
        physical_partition_ids=physical_partition_ids
    )

    retrieve_throughput_parameters = RetrieveThroughputParameters(
        resource=retrieve_throughput_properties_resource
    )

    async_partition_retrieve_throughput_result = client.begin_mongo_db_container_retrieve_throughput_distribution(resource_group_name=resource_group_name,
                                                                                                                  account_name=account_name,
                                                                                                                  database_name=database_name,
                                                                                                                  collection_name=collection_name,
                                                                                                                  retrieve_throughput_parameters=retrieve_throughput_parameters)

    return async_partition_retrieve_throughput_result.result()


# pylint: disable=dangerous-default-value
def cli_begin_redistribute_mongo_container_partition_throughput(client,
                                                                resource_group_name,
                                                                account_name,
                                                                database_name,
                                                                collection_name,
                                                                evenly_distribute=False,
                                                                target_partition_info=[],
                                                                source_partition_info=[]):

    try:
        client.get_mongo_db_collection(
            resource_group_name, account_name, database_name, collection_name)
    except Exception as ex:
        if ex.error.code == "NotFound":
            raise CLIError("(NotFound) Container with name '{}' in database '{} could not be found.".format(collection_name, database_name))

    if evenly_distribute:
        redistribute_throughput_properties_resource = RedistributeThroughputPropertiesResource(
            throughput_policy=ThroughputPolicyType.EQUAL,
            target_physical_partition_throughput_info=[],
            source_physical_partition_throughput_info=[])
    else:
        redistribute_throughput_properties_resource = RedistributeThroughputPropertiesResource(
            throughput_policy=ThroughputPolicyType.CUSTOM,
            target_physical_partition_throughput_info=target_partition_info,
            source_physical_partition_throughput_info=source_partition_info
        )

    redistribute_throughput_parameters = RedistributeThroughputParameters(
        resource=redistribute_throughput_properties_resource
    )

    async_partition_redistribute_throughput_result = client.begin_mongo_db_container_redistribute_throughput(resource_group_name=resource_group_name,
                                                                                                             account_name=account_name,
                                                                                                             database_name=database_name,
                                                                                                             collection_name=collection_name,
                                                                                                             redistribute_throughput_parameters=redistribute_throughput_parameters)

    return async_partition_redistribute_throughput_result.result()


def cli_cosmosdb_gremlin_database_restore(cmd,
                                          client,
                                          resource_group_name,
                                          account_name,
                                          database_name,
                                          restore_timestamp=None,
                                          disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted database account {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a Gremlin database account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore

        if restorable_database_account is None:
            raise CLIError("Cannot find a Gremlin database account with name {} that is online".format(account_name))

        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_gremlin_databases
            restorable_databases_client = cf_restorable_gremlin_databases(cmd.cli_ctx, [])
            restorable_databases = restorable_databases_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_database_delete_time, latest_database_create_or_recreate_time, database_rid = process_restorable_databases(restorable_databases, database_name)  # pylint: disable=unused-variable

            # Database is alive if create or recreate timestamp is later than latest delete timestamp
            database_alive = latest_database_create_or_recreate_time > latest_database_delete_time or latest_database_delete_time == datetime.datetime.max

            if database_alive:
                raise CLIError("Database with name {} already exists in this account with name {} in location {}".format(database_name, account_name, restorable_database_account.location))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_database_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a Gremlin database account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB Gremlin database"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    gremlin_database_resource = GremlinDatabaseCreateUpdateParameters(
        resource=SqlDatabaseResource(
            id=database_name,
            create_mode=create_mode,
            restore_parameters=restore_parameters)
    )

    return client.begin_create_update_gremlin_database(resource_group_name,
                                                       account_name,
                                                       database_name,
                                                       gremlin_database_resource)


def cli_cosmosdb_gremlin_graph_restore(cmd,
                                       client,
                                       resource_group_name,
                                       account_name,
                                       database_name,
                                       graph_name,
                                       restore_timestamp=None,
                                       disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    # """Restores the deleted Azure Cosmos DB Gremlin graph """
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted gremlin database account {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online".format(account_name))

        database_rid = None
        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_gremlin_databases
            restorable_databases_client = cf_restorable_gremlin_databases(cmd.cli_ctx, [])
            restorable_databases = restorable_databases_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_database_delete_time, latest_database_create_or_recreate_time, database_rid = process_restorable_databases(restorable_databases, database_name)

            # Database is alive if create or recreate timestamp is later than latest delete timestamp
            database_alive = latest_database_delete_time == datetime.datetime.max or latest_database_create_or_recreate_time > latest_database_delete_time

            if not database_alive:
                raise CLIError("No active database with name {} found that contains the graph {}".format(database_name, graph_name))

            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_gremlin_graphs
            restorable_graphs_client = cf_restorable_gremlin_graphs(cmd.cli_ctx, [])
            restorable_graphs = restorable_graphs_client.list(
                restorable_database_account.location,
                restorable_database_account.name,
                database_rid)

            latest_graph_delete_time, latest_graph_create_or_recreate_time = process_restorable_collections(restorable_graphs, graph_name, database_name)

            # Graph is alive if create or recreate timestamp is later than latest delete timestamp
            graph_alive = latest_graph_create_or_recreate_time > latest_graph_delete_time or latest_graph_delete_time == datetime.datetime.max

            if graph_alive:
                raise CLIError("The graph {} is currently online. Please delete the graph and provide a restore timestamp for restoring different instance of the graph.".format(graph_name))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_graph_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a database account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB Gremlin graph"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    gremlin_graph_resource = GremlinGraphResource(
        id=graph_name,
        create_mode=create_mode,
        restore_parameters=restore_parameters)

    gremlin_graph_create_update_resource = GremlinGraphCreateUpdateParameters(
        resource=gremlin_graph_resource,
        options={})

    return client.begin_create_update_gremlin_graph(resource_group_name,
                                                    account_name,
                                                    database_name,
                                                    graph_name,
                                                    gremlin_graph_create_update_resource)


def cli_cosmosdb_table_restore(cmd,
                               client,
                               resource_group_name,
                               account_name,
                               table_name,
                               restore_timestamp=None,
                               disable_ttl=None):

    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts  # pylint: disable=redefined-outer-name,reimported
    # """Restores the deleted Azure Cosmos DB Table"""
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    restorable_database_account = None

    if restore_timestamp is not None:
        restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if account.deletion_time is not None:
                    if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                        raise CLIError("Cannot perform inaccount restore on a deleted table {}".format(account_name))
                else:
                    if restore_timestamp_datetime_utc >= account.creation_time:
                        restorable_database_account = account
                        break

        if restorable_database_account is None:
            raise CLIError("Cannot find a account with name {} that is online at {}".format(account_name, restore_timestamp))
    else:
        latest_account_to_restore = None
        for account in restorable_database_accounts_list:
            if account.account_name == account_name:
                if latest_account_to_restore is None or account.creation_time > latest_account_to_restore.creation_time:
                    if account.deletion_time is None:
                        latest_account_to_restore = account

        restorable_database_account = latest_account_to_restore

        if restorable_database_account is None:
            raise CLIError("Cannot find a database account with name {} that is online".format(account_name))

        try:
            from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_tables
            restorable_tables_client = cf_restorable_tables(cmd.cli_ctx, [])
            restorable_tables = restorable_tables_client.list(
                restorable_database_account.location,
                restorable_database_account.name)

            latest_table_delete_time, latest_table_create_or_recreate_time, table_rid = process_restorable_databases(restorable_tables, table_name)  # pylint: disable=unused-variable

            # Table is alive if create or recreate timestamp is later than latest delete timestamp
            table_alive = latest_table_create_or_recreate_time > latest_table_delete_time or latest_table_delete_time == datetime.datetime.max

            if table_alive:
                raise CLIError("Table with name {} already exists in this account with name {} in location {}".format(table_name, account_name, restorable_database_account.location))

            # """Subtracting -1 second from the deleted timestamp to restore till end of logchain"""
            restore_time = latest_table_delete_time + datetime.timedelta(seconds=-1)
            restore_timestamp = restore_time.strftime("%Y-%m-%dT%H:%M:%S%Z")
        except ResourceNotFoundError:
            raise CLIError("Cannot find a table account with name {} that is online in location {}".format(account_name, restorable_database_account.location))

    # """Restores the deleted Azure Cosmos DB Table"""
    create_mode = CreateMode.restore.value
    restore_parameters = RestoreParameters(
        restore_source=restorable_database_account.id,
        restore_timestamp_in_utc=restore_timestamp
    )

    if disable_ttl is not None:
        restore_parameters.restore_with_ttl_disabled = disable_ttl

    table_resource = TableCreateUpdateParameters(
        resource=TableResource(id=table_name,
                               create_mode=create_mode,
                               restore_parameters=restore_parameters),
        options={})

    return client.begin_create_update_table(resource_group_name,
                                            account_name,
                                            table_name,
                                            table_resource)
