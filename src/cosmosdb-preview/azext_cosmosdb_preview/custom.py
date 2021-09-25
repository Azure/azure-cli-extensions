# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger
from azure.core.exceptions import HttpResponseError
from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    ClusterResource,
    ClusterResourceProperties,
    DataCenterResource,
    DataCenterResourceProperties,
    GraphResource,
    GraphResourceCreateUpdateParameters,
    ServiceResourceCreateUpdateParameters
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
                                                  identity=None,
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

    cluster_resource_create_update_parameters = ClusterResource(
        location=location,
        tags=tags,
        identity=identity,
        properties=cluster_properties)

    return client.begin_create_update(resource_group_name, cluster_name, cluster_resource_create_update_parameters)


def cli_cosmosdb_managed_cassandra_cluster_update(client,
                                                  resource_group_name,
                                                  cluster_name,
                                                  tags=None,
                                                  identity=None,
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

    if identity is None:
        identity = cluster_resource.identity

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


def cli_cosmosdb_managed_cassandra_fetch_node_status(client,
                                                     resource_group_name,
                                                     cluster_name):

    """Get Azure Managed Cassandra Cluster Node Status"""

    return client.begin_fetch_node_status(resource_group_name, cluster_name)


def cli_cosmosdb_managed_cassandra_datacenter_create(client,
                                                     resource_group_name,
                                                     cluster_name,
                                                     data_center_name,
                                                     data_center_location,
                                                     delegated_subnet_id,
                                                     node_count,
                                                     base64_encoded_cassandra_yaml_fragment=None):

    """Creates an Azure Managed Cassandra Datacenter"""

    data_center_properties = DataCenterResourceProperties(
        data_center_location=data_center_location,
        delegated_subnet_id=delegated_subnet_id,
        node_count=node_count,
        base64_encoded_cassandra_yaml_fragment=base64_encoded_cassandra_yaml_fragment
    )

    data_center_resource = DataCenterResource(
        properties=data_center_properties
    )

    return client.begin_create_update(resource_group_name, cluster_name, data_center_name, data_center_resource)


def cli_cosmosdb_managed_cassandra_datacenter_update(client, resource_group_name,
                                                     cluster_name,
                                                     data_center_name,
                                                     node_count=None,
                                                     base64_encoded_cassandra_yaml_fragment=None):

    """Updates an Azure Managed Cassandra Datacenter"""

    data_center_resource = client.get(resource_group_name, cluster_name, data_center_name)

    if node_count is None:
        node_count = data_center_resource.properties.node_count

    if base64_encoded_cassandra_yaml_fragment is None:
        base64_encoded_cassandra_yaml_fragment = data_center_resource.properties.base64_encoded_cassandra_yaml_fragment

    data_center_properties = DataCenterResourceProperties(
        data_center_location=data_center_resource.properties.data_center_location,
        delegated_subnet_id=data_center_resource.properties.delegated_subnet_id,
        node_count=node_count,
        seed_nodes=data_center_resource.properties.seed_nodes,
        base64_encoded_cassandra_yaml_fragment=base64_encoded_cassandra_yaml_fragment)

    data_center_resource = DataCenterResource(
        properties=data_center_properties
    )

    return client.begin_create_update(resource_group_name, cluster_name, data_center_name, data_center_resource)
  

def cli_cosmosdb_identity_show(client, resource_group_name, account_name):
    """ Show the identity associated with a Cosmos DB account """

    cosmos_db_account = client.get(resource_group_name, account_name)
    return cosmos_db_account.identity


def cli_cosmosdb_identity_assign(client,
                                 resource_group_name,
                                 account_name,
                                 identities=None):
    """ Update the identities associated with a Cosmos DB account """

    existing = client.get(resource_group_name, account_name)

    SYSTEM_ID = '[system]'
    enable_system = identities is None or SYSTEM_ID in identities
    new_user_identities = []
    if identities is not None:
        new_user_identities = [x for x in identities if x != SYSTEM_ID]

    only_enabling_system = enable_system and len(new_user_identities) == 0
    system_already_added = existing.identity.type == ResourceIdentityType.system_assigned or existing.identity.type == ResourceIdentityType.system_assigned_user_assigned
    all_new_users_already_added = new_user_identities and existing.identity and existing.identity.user_assigned_identities and all(x in existing.identity.user_assigned_identities for x in new_user_identities)
    if only_enabling_system and system_already_added:
        return existing.identity
    if (not enable_system) and all_new_users_already_added:
        return existing.identity
    if enable_system and system_already_added and all_new_users_already_added:
        return existing.identity

    if existing.identity and existing.identity.type == ResourceIdentityType.system_assigned_user_assigned:
        identity_type = ResourceIdentityType.system_assigned_user_assigned
    elif existing.identity and existing.identity.type == ResourceIdentityType.system_assigned and new_user_identities:
        identity_type = ResourceIdentityType.system_assigned_user_assigned
    elif existing.identity and existing.identity.type == ResourceIdentityType.user_assigned and enable_system:
        identity_type = ResourceIdentityType.system_assigned_user_assigned
    elif new_user_identities and enable_system:
        identity_type = ResourceIdentityType.system_assigned_user_assigned
    elif new_user_identities:
        identity_type = ResourceIdentityType.user_assigned
    else:
        identity_type = ResourceIdentityType.system_assigned

    if identity_type in [ResourceIdentityType.system_assigned, ResourceIdentityType.none]:
        new_identity = ManagedServiceIdentity(type=identity_type.value)
    else:
        new_assigned_identities = existing.identity.user_assigned_identities or {}
        for identity in new_user_identities:
            new_assigned_identities[identity] = Components1Jq1T4ISchemasManagedserviceidentityPropertiesUserassignedidentitiesAdditionalproperties()

        new_identity = ManagedServiceIdentity(type=identity_type.value, user_assigned_identities=new_assigned_identities)

    params = DatabaseAccountUpdateParameters(identity=new_identity)
    async_cosmos_db_update = client.begin_update(resource_group_name, account_name, params)
    cosmos_db_account = async_cosmos_db_update.result()
    return cosmos_db_account.identity


def cli_cosmosdb_identity_remove(client,
                                 resource_group_name,
                                 account_name,
                                 identities=None):
    """ Remove the identities associated with a Cosmos DB account """

    existing = client.get(resource_group_name, account_name)

    SYSTEM_ID = '[system]'
    remove_system_assigned_identity = False
    if not identities:
        remove_system_assigned_identity = True
    elif SYSTEM_ID in identities:
        remove_system_assigned_identity = True
        identities.remove(SYSTEM_ID)

    if existing.identity is None:
        return ManagedServiceIdentity(type=ResourceIdentityType.none.value)
    if existing.identity.user_assigned_identities:
        existing_identities = existing.identity.user_assigned_identities.keys()
    else:
        existing_identities = []
    if identities:
        identities_to_remove = identities
    else:
        identities_to_remove = []
    non_existing = [x for x in identities_to_remove if x not in set(existing_identities)]

    if non_existing:
        raise CLIError("'{}' are not associated with '{}'".format(','.join(non_existing), account_name))
    identities_remaining = [x for x in existing_identities if x not in set(identities_to_remove)]
    if remove_system_assigned_identity and ((not existing.identity) or (existing.identity and existing.identity.type in [ResourceIdentityType.none, ResourceIdentityType.user_assigned])):
        raise CLIError("System-assigned identity is not associated with '{}'".format(account_name))

    if identities_remaining and not remove_system_assigned_identity and existing.identity.type == ResourceIdentityType.system_assigned_user_assigned:
        set_type = ResourceIdentityType.system_assigned_user_assigned
    elif identities_remaining and remove_system_assigned_identity and existing.identity.type == ResourceIdentityType.system_assigned_user_assigned:
        set_type = ResourceIdentityType.user_assigned
    elif identities_remaining and not remove_system_assigned_identity and existing.identity.type == ResourceIdentityType.user_assigned:
        set_type = ResourceIdentityType.user_assigned
    elif not identities_remaining and not remove_system_assigned_identity and existing.identity.type == ResourceIdentityType.system_assigned_user_assigned:
        set_type = ResourceIdentityType.system_assigned
    elif not identities_remaining and not remove_system_assigned_identity and existing.identity.type == ResourceIdentityType.system_assigned:
        set_type = ResourceIdentityType.system_assigned
    else:
        set_type = ResourceIdentityType.none

    new_user_identities = {}
    for identity in identities_remaining:
        new_user_identities[identity] = Components1Jq1T4ISchemasManagedserviceidentityPropertiesUserassignedidentitiesAdditionalproperties()
    if set_type in [ResourceIdentityType.system_assigned_user_assigned, ResourceIdentityType.user_assigned]:
        for removed_identity in identities_to_remove:
            new_user_identities[removed_identity] = None
    if not new_user_identities:
        new_user_identities = None

    params = DatabaseAccountUpdateParameters(identity=ManagedServiceIdentity(type=set_type, user_assigned_identities=new_user_identities))
    async_cosmos_db_update = client.begin_update(resource_group_name, account_name, params)
    cosmos_db_account = async_cosmos_db_update.result()
    return cosmos_db_account.identity


def _handle_exists_exception(http_response_error):
    if http_response_error.status_code == 404:
        return False
    raise http_response_error


def cli_cosmosdb_graph_create(client, account_name, resource_group_name, graph_name):
    graph = GraphResourceCreateUpdateParameters(resource=GraphResource(id=graph_name))
    return client.begin_create_update_graph(resource_group_name, account_name, graph_name, graph)


def cli_cosmosdb_graph_exists(client, account_name, resource_group_name, graph_name):
    try:
        client.get_graph(resource_group_name, account_name, graph_name)
    except HttpResponseError as ex:
        return _handle_exists_exception(ex)

    return True


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


def _gen_guid():
    import uuid
    return uuid.uuid4()
