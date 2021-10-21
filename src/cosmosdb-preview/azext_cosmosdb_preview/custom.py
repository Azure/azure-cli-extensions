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
    CommandPostBody,
    DataCenterResource,
    DataCenterResourceProperties,
    ManagedCassandraManagedServiceIdentity,
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


def cli_cosmosdb_managed_cassandra_cluster_invoke_command(client,
                                                          resource_group_name,
                                                          cluster_name,
                                                          command_name,
                                                          host,
                                                          arguments=None,
                                                          cassandra_stop_start=None,
                                                          readwrite=None):

    """Invokes a command in Azure Managed Cassandra Cluster host"""

    cluster_invoke_command = CommandPostBody(
        command=command_name,
        host=host,
        arguments=arguments,
        cassandra_stop_start=cassandra_stop_start,
        readwrite=readwrite
    )

    return client.begin_invoke_command(resource_group_name, cluster_name, cluster_invoke_command)


def cli_cosmosdb_managed_cassandra_cluster_status(client,
                                                  resource_group_name,
                                                  cluster_name):

    """Get Azure Managed Cassandra Cluster Node Status"""

    return client.status(resource_group_name, cluster_name)


def cli_cosmosdb_managed_cassandra_cluster_deallocate(client,
                                                      resource_group_name,
                                                      cluster_name):

    """Deallocate Azure Managed Cassandra Cluster"""

    return client.begin_deallocate(resource_group_name, cluster_name)


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


def cli_cosmosdb_managed_cassandra_cluster_start(client,
                                                 resource_group_name,
                                                 cluster_name):

    """Start Azure Managed Cassandra Cluster"""

    return client.begin_start(resource_group_name, cluster_name)


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
                                                     availability_zone=None):

    """Creates an Azure Managed Cassandra Datacenter"""

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
        backup_storage_customer_key_uri=backup_storage_customer_key_uri
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
                                                     backup_storage_customer_key_uri=None):

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
        base64_encoded_cassandra_yaml_fragment=base64_encoded_cassandra_yaml_fragment,
        managed_disk_customer_key_uri=managed_disk_customer_key_uri,
        backup_storage_customer_key_uri=backup_storage_customer_key_uri
    )

    data_center_resource = DataCenterResource(
        properties=data_center_properties
    )

    return client.begin_create_update(resource_group_name, cluster_name, data_center_name, data_center_resource)


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
