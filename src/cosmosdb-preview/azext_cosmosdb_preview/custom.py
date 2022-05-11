# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements, consider-using-f-string, broad-except, no-member, raise-missing-from

from knack.util import CLIError
from knack.log import get_logger
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    ClusterResource,
    ClusterResourceProperties,
    DataCenterResource,
    DataCenterResourceProperties,
    ManagedCassandraManagedServiceIdentity,
    AuthenticationMethodLdapProperties,
    ServiceResourceCreateUpdateParameters,
    MongoRoleDefinitionCreateUpdateParameters,
    MongoUserDefinitionCreateUpdateParameters,
    DatabaseAccountKind,
    ContinuousBackupRestoreLocation,
    DatabaseAccountCreateUpdateParameters,
    DatabaseAccountUpdateParameters,
    RestoreParameters
)

from azext_cosmosdb_preview._client_factory import (
    cf_restorable_gremlin_resources,
    cf_restorable_table_resources
)

from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.core.exceptions import ResourceNotFoundError

from azure.mgmt.cosmosdb.models import (
    Location,
    CreateMode,
    ConsistencyPolicy,
    ResourceIdentityType,
    ManagedServiceIdentity,
    PeriodicModeBackupPolicy,
    PeriodicModeProperties,
    AnalyticalStorageConfiguration,
    ContinuousModeBackupPolicy,
    Components1Jq1T4ISchemasManagedserviceidentityPropertiesUserassignedidentitiesAdditionalproperties
)

from azure.cli.command_modules.cosmosdb.custom import _convert_to_utc_timestamp

from azure.cli.command_modules.cosmosdb._client_factory import (
    cf_restorable_sql_resources,
    cf_restorable_mongodb_resources
)


logger = get_logger(__name__)


def _handle_exists_exception(cloud_error):
    if cloud_error.status_code == 404:
        return False
    raise cloud_error


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
                                                  repair_enabled=None):

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
        repair_enabled=repair_enabled)

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
                                                  repair_enabled=None):

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
        seed_nodes=cluster_resource.properties.seed_nodes
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


def _handle_exists_exception(http_response_error):
    if http_response_error.status_code == 404:
        return False
    raise http_response_error


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
                        enable_public_network=None,
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
                        databases_to_restore=None,
                        gremlin_databases_to_restore=None,
                        tables_to_restore=None,
                        is_restore_request=None,
                        restore_source=None,
                        restore_timestamp=None,
                        enable_materialized_views=None):
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
                                    enable_public_network=enable_public_network,
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
                                    backup_interval=backup_interval,
                                    backup_redundancy=backup_redundancy,
                                    assign_identity=assign_identity,
                                    default_identity=default_identity,
                                    backup_retention=backup_retention,
                                    databases_to_restore=databases_to_restore,
                                    gremlin_databases_to_restore=gremlin_databases_to_restore,
                                    tables_to_restore=tables_to_restore,
                                    arm_location=resource_group_location,
                                    enable_materialized_views=enable_materialized_views)


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
                        enable_public_network=None,
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
                        enable_materialized_views=None):
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

    public_network_access = None
    if enable_public_network is not None:
        public_network_access = 'Enabled' if enable_public_network else 'Disabled'

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
        enable_materialized_views=enable_materialized_views)

    async_docdb_update = client.begin_update(resource_group_name, account_name, params)
    docdb_account = async_docdb_update.result()
    docdb_account = client.get(resource_group_name, account_name)  # Workaround
    return docdb_account


# restore cosmosdb account with gremlin databases and tables to restore
# pylint: disable=too-many-statements
def cli_cosmosdb_restore(cmd,
                         client,
                         resource_group_name,
                         account_name,
                         target_database_account_name,
                         restore_timestamp,
                         location,
                         databases_to_restore=None,
                         gremlin_databases_to_restore=None,
                         tables_to_restore=None):
    from azure.cli.command_modules.cosmosdb._client_factory import cf_restorable_database_accounts
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    target_restorable_account = None
    restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)

    # If restore timestamp is timezone aware, get the utcnow as timezone aware as well
    from datetime import datetime, timezone
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
        if api_type == "sql":
            try:
                restorable_sql_resources_client = cf_restorable_sql_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_sql_resources_client.list(
                    target_restorable_account.location,
                    target_restorable_account.name,
                    location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, location))
        elif api_type == "mongodb":
            try:
                restorable_mongodb_resources_client = cf_restorable_mongodb_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_mongodb_resources_client.list(
                    target_restorable_account.location,
                    target_restorable_account.name,
                    location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, location))
        elif "sql" in api_type and "gremlin" in api_type:
            try:
                restorable_gremlin_resources_client = cf_restorable_gremlin_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_gremlin_resources_client.list(
                    target_restorable_account.location,
                    target_restorable_account.name,
                    location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, location))
        elif "sql" in api_type and "table" in api_type:
            try:
                restorable_table_resources_client = cf_restorable_table_resources(cmd.cli_ctx, [])
                restorable_resources = restorable_table_resources_client.list(
                    target_restorable_account.location,
                    target_restorable_account.name,
                    location,
                    restore_timestamp_datetime_utc)
            except ResourceNotFoundError:
                raise CLIError("Cannot find a database account with name {} that is online at {} in location {}".format(account_name, restore_timestamp, location))
        else:
            raise CLIError("Provided API Type {} is not supported for account {}".format(target_restorable_account.api_type, account_name))

        if restorable_resources is None or not any(restorable_resources):
            raise CLIError("Database account {} contains no restorable resources in location {} at given restore timestamp {}".format(target_restorable_account, location, restore_timestamp_datetime_utc))

    # Trigger restore
    locations = []
    locations.append(Location(location_name=location, failover_priority=0))

    return _create_database_account(client,
                                    resource_group_name=resource_group_name,
                                    account_name=target_database_account_name,
                                    locations=locations,
                                    is_restore_request=True,
                                    restore_source=target_restorable_account.id,
                                    restore_timestamp=restore_timestamp_datetime_utc.isoformat(),
                                    databases_to_restore=databases_to_restore,
                                    gremlin_databases_to_restore=gremlin_databases_to_restore,
                                    tables_to_restore=tables_to_restore,
                                    arm_location=target_restorable_account.location)


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
                             enable_public_network=None,
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
                             analytical_storage_schema_type=None,
                             databases_to_restore=None,
                             gremlin_databases_to_restore=None,
                             tables_to_restore=None,
                             is_restore_request=None,
                             restore_source=None,
                             restore_timestamp=None,
                             arm_location=None,
                             enable_materialized_views=None):

    consistency_policy = None
    if default_consistency_level is not None:
        consistency_policy = ConsistencyPolicy(default_consistency_level=default_consistency_level,
                                               max_staleness_prefix=max_staleness_prefix,
                                               max_interval_in_seconds=max_interval)

    if not locations:
        locations = []
        locations.append(Location(location_name=arm_location, failover_priority=0, is_zone_redundant=False))

    public_network_access = None
    if enable_public_network is not None:
        public_network_access = 'Enabled' if enable_public_network else 'Disabled'

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
                    user_identities[x] = Components1Jq1T4ISchemasManagedserviceidentityPropertiesUserassignedidentitiesAdditionalproperties()  # pylint: disable=line-too-long
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
        enable_materialized_views=enable_materialized_views
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


def cosmosdb_data_transfer_copy_job(client,
                                    resource_group_name,
                                    account_name,
                                    source_cassandra_table=None,
                                    dest_cassandra_table=None,
                                    source_sql_container=None,
                                    dest_sql_container=None,
                                    worker_count=0,
                                    job_name=None):
    if source_cassandra_table is None and source_sql_container is None:
        raise CLIError('source component ismissing')

    if source_cassandra_table is not None and source_sql_container is not None:
        raise CLIError('Invalid input: multiple source components')

    if dest_cassandra_table is None and dest_sql_container is None:
        raise CLIError('destination component is missing')

    if dest_cassandra_table is not None and dest_sql_container is not None:
        raise CLIError('Invalid input: multiple destination components')

    job_create_properties = {}

    if source_cassandra_table is not None:
        job_create_properties['source'] = source_cassandra_table

    if source_sql_container is not None:
        job_create_properties['source'] = source_sql_container

    if dest_cassandra_table is not None:
        job_create_properties['destination'] = dest_cassandra_table

    if dest_sql_container is not None:
        job_create_properties['destination'] = dest_sql_container

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
