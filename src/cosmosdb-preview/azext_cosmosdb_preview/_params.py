# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements


from azext_cosmosdb_preview._validators import (
    validate_gossip_certificates,
    validate_client_certificates,
    validate_server_certificates,
    validate_seednodes,
    validate_node_count)

from azext_cosmosdb_preview.actions import (
    InvokeCommandArgumentsAddAction)


def load_arguments(self, _):
    from azure.cli.core.commands.parameters import tags_type, get_enum_type, get_three_state_flag

    # Managed Cassandra Cluster
    for scope in [
            'managed-cassandra cluster create',
            'managed-cassandra cluster update',
            'managed-cassandra cluster show',
            'managed-cassandra cluster delete',
            'managed-cassandra cluster backup list',
            'managed-cassandra cluster backup show']:
        with self.argument_context(scope) as c:
            c.argument('cluster_name', options_list=['--cluster-name', '-c'], help="Cluster Name", required=True)

    # Managed Cassandra Cluster
    for scope in [
            'managed-cassandra cluster create',
            'managed-cassandra cluster update']:
        with self.argument_context(scope) as c:
            c.argument('tags', arg_type=tags_type)
            c.argument('external_gossip_certificates', nargs='+', validator=validate_gossip_certificates, options_list=['--external-gossip-certificates', '-e'], help="A list of certificates that the managed cassandra data center's should accept.")
            c.argument('cassandra_version', help="The version of Cassandra chosen.")
            c.argument('authentication_method', arg_type=get_enum_type(['None', 'Cassandra', 'Ldap']), help="Authentication mode can be None, Cassandra or Ldap. If None, no authentication will be required to connect to the Cassandra API. If Cassandra, then passwords will be used. Ldap is in preview")
            c.argument('hours_between_backups', help="The number of hours between backup attempts.")
            c.argument('repair_enabled', help="Enables automatic repair.")
            c.argument('client_certificates', nargs='+', validator=validate_client_certificates, help="If specified, enables client certificate authentication to the Cassandra API.")
            c.argument('gossip_certificates', help="A list of certificates that should be accepted by on-premise data centers.")
            c.argument('external_seed_nodes', nargs='+', validator=validate_seednodes, help="A list of ip addresses of the seed nodes of on-premise data centers.")
            c.argument('identity_type', options_list=['--identity-type'], arg_type=get_enum_type(['None', 'SystemAssigned']), help="Type of identity used for Customer Managed Disk Key.")

    # Managed Cassandra Cluster
    with self.argument_context('managed-cassandra cluster create') as c:
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the Cluster", required=True)
        c.argument('delegated_management_subnet_id', options_list=['--delegated-management-subnet-id', '-s'], help="The resource id of a subnet where the ip address of the cassandra management server will be allocated. This subnet must have connectivity to the delegated_subnet_id subnet of each data center.", required=True)
        c.argument('initial_cassandra_admin_password', options_list=['--initial-cassandra-admin-password', '-i'], help="The intial password to be configured when a cluster is created for authentication_method Cassandra.")
        c.argument('restore_from_backup_id', help="The resource id of a backup. If provided on create, the backup will be used to prepopulate the cluster. The cluster data center count and node counts must match the backup.")
        c.argument('cluster_name_override', help="If a cluster must have a name that is not a valid azure resource name, this field can be specified to choose the Cassandra cluster name. Otherwise, the resource name will be used as the cluster name.")

    # Managed Cassandra Cluster
    for scope in ['managed-cassandra cluster backup show']:
        with self.argument_context(scope) as c:
            c.argument('backup_id', options_list=['--backup-id'], help="The resource id of the backup", required=True)

    # Managed Cassandra Datacenter
    for scope in [
            'managed-cassandra datacenter create',
            'managed-cassandra datacenter update',
            'managed-cassandra datacenter show',
            'managed-cassandra datacenter delete']:
        with self.argument_context(scope) as c:
            c.argument('cluster_name', options_list=['--cluster-name', '-c'], help="Cluster Name", required=True)
            c.argument('data_center_name', options_list=['--data-center-name', '-d'], help="Datacenter Name", required=True)

    # Managed Cassandra Datacenter
    for scope in [
            'managed-cassandra datacenter create',
            'managed-cassandra datacenter update']:
        with self.argument_context(scope) as c:
            c.argument('node_count', options_list=['--node-count', '-n'], validator=validate_node_count, help="The number of Cassandra virtual machines in this data center. The minimum value is 3.")
            c.argument('base64_encoded_cassandra_yaml_fragment', options_list=['--base64-encoded-cassandra-yaml-fragment', '-b'], help="This is a Base64 encoded yaml file that is a subset of cassandra.yaml.  Supported fields will be honored and others will be ignored.")
            c.argument('data_center_location', options_list=['--data-center-location', '-l'], help="The region where the virtual machine for this data center will be located.")
            c.argument('delegated_subnet_id', options_list=['--delegated-subnet-id', '-s'], help="The resource id of a subnet where ip addresses of the Cassandra virtual machines will be allocated. This must be in the same region as data_center_location.")
            c.argument('managed_disk_customer_key_uri', options_list=['--managed-disk-customer-key-uri', '-k'], help="Key uri to use for encryption of managed disks. Ensure the system assigned identity of the cluster has been assigned appropriate permissions(key get/wrap/unwrap permissions) on the key.")
            c.argument('backup_storage_customer_key_uri', options_list=['--backup-storage-customer-key-uri', '-p'], help="Indicates the Key Uri of the customer key to use for encryption of the backup storage account.")
            c.argument('server_hostname', options_list=['--ldap-server-hostname'], help="Hostname of the LDAP server.")
            c.argument('server_port', options_list=['--ldap-server-port'], help="Port of the LDAP server.")
            c.argument('service_user_distinguished_name', options_list=['--ldap-user-name'], help="Distinguished name of the look up user account, who can look up user details on authentication.")
            c.argument('service_user_password', options_list=['--ldap-user-password'], help="Password of the look up user.")
            c.argument('search_base_distinguished_name', options_list=['--ldap-base-name'], help="Distinguished name of the object to start the recursive search of users from.")
            c.argument('search_filter_template', options_list=['--ldap-filter-template'], help="Template to use for searching. Defaults to (cn=%s) where %s will be replaced by the username used to login.")
            c.argument('server_certificates', nargs='+', validator=validate_server_certificates, options_list=['--ldap-certificates'], help="LDAP server certificate.")

    # Managed Cassandra Datacenter
    with self.argument_context('managed-cassandra datacenter create') as c:
        c.argument('data_center_location', options_list=['--data-center-location', '-l'], help="Azure Location of the Datacenter", required=True)
        c.argument('delegated_subnet_id', options_list=['--delegated-subnet-id', '-s'], help="The resource id of a subnet where ip addresses of the Cassandra virtual machines will be allocated. This must be in the same region as data_center_location.", required=True)
        c.argument('node_count', options_list=['--node-count', '-n'], validator=validate_node_count, help="The number of Cassandra virtual machines in this data center. The minimum value is 3.", required=True)
        c.argument('sku', options_list=['--sku'], help="Virtual Machine SKU used for data centers. Default value is Standard_DS14_v2")
        c.argument('disk_sku', options_list=['--disk-sku'], help="Disk SKU used for data centers. Default value is P30.")
        c.argument('disk_capacity', options_list=['--disk-capacity'], help="Number of disk used for data centers. Default value is 4.")
        c.argument('availability_zone', options_list=['--availability-zone', '-z'], arg_type=get_three_state_flag(), help="If the data center haves Availability Zone feature, apply it to the Virtual Machine ScaleSet that host the data center virtual machines.")

    # Managed Cassandra Datacenter
    with self.argument_context('managed-cassandra datacenter list') as c:
        c.argument('cluster_name', options_list=['--cluster-name', '-c'], help="Cluster Name", required=True)

    # Graph
    with self.argument_context('cosmosdb graph') as c:
        c.argument('account_name', completer=None, options_list=['--account-name', '-a'], help='Name of the Cosmos DB database account.', id_part=None)
        c.argument('resource_group_name', completer=None, options_list=['--resource-group-name', '-g'], help='Name of the resource group of the database account.', id_part=None)
        c.argument('graph_name', options_list=['--name', '-n'], help="Graph name")

    # Services
        with self.argument_context('cosmosdb service') as c:
            c.argument('account_name', completer=None, options_list=['--account-name', '-a'], help='Name of the Cosmos DB database account.', id_part=None)
            c.argument('resource_group_name', completer=None, options_list=['--resource-group-name', '-g'], help='Name of the resource group of the database account.', id_part=None)
            c.argument('service_kind', options_list=['--kind', '-k'], help="Service kind")
            c.argument('service_name', options_list=['--name', '-n'], help="Service Name.")
            c.argument('instance_count', options_list=['--count', '-c'], help="Instance Count.")
            c.argument('instance_size', options_list=['--size'], help="Instance Size. Possible values are: Cosmos.D4s, Cosmos.D8s, Cosmos.D16s etc")
