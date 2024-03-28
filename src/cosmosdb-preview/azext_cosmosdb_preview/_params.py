# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements

import argparse
from argcomplete.completers import FilesCompleter

from azext_cosmosdb_preview._validators import (
    validate_gossip_certificates,
    validate_client_certificates,
    validate_server_certificates,
    validate_seednodes,
    validate_node_count,
    validate_mongo_role_definition_body,
    validate_mongo_role_definition_id,
    validate_mongo_user_definition_body,
    validate_mongo_user_definition_id)

from azext_cosmosdb_preview.actions import (
    CreateGremlinDatabaseRestoreResource,
    CreateTableRestoreResource,
    AddCassandraTableAction,
    AddMongoCollectionAction,
    AddSqlContainerAction,
    CreateTargetPhysicalPartitionThroughputInfoAction,
    CreateSourcePhysicalPartitionThroughputInfoAction,
    CreatePhysicalPartitionIdListAction)

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    ContinuousTier, DefaultPriorityLevel
)

from azure.cli.core.util import shell_safe_json_parse

from azure.cli.core.commands.parameters import (
    tags_type, get_resource_name_completion_list, name_type, get_enum_type, get_three_state_flag, get_location_type)

from azure.mgmt.cosmosdb.models import (
    DefaultConsistencyLevel, DatabaseAccountKind, ServerVersion, NetworkAclBypass, BackupPolicyType, AnalyticalStorageSchemaType, BackupStorageRedundancy)

from azure.cli.command_modules.cosmosdb.actions import (
    CreateLocation, CreateDatabaseRestoreResource, UtcDatetimeAction)

from azure.cli.command_modules.cosmosdb._validators import (
    validate_capabilities, validate_virtual_network_rules, validate_ip_range_filter,
    validate_client_encryption_policy)


MONGO_ROLE_DEFINITION_EXAMPLE = """--body "{
\\"Id\\": \\"be79875a-2cc4-40d5-8958-566017875b39\\",
\\"RoleName\\": \\"MyRWRole\\",
\\"Type\\": \\"CustomRole\\"
\\"DatabaseName\\": \\"MyDb\\",
\\"Privileges\\": [ {\\"Resource\\": {\\"Db\\": \\"MyDB\\",\\"Collection\\": \\"MyCol\\"},\\"Actions\\": [\\"insert\\",\\"find\\"]}],
\\"Roles\\": [ {\\"Role\\": \\"myInheritedRole\\",\\"Db\\": \\"MyTestDb\\"}]
}"
"""

MONGO_USER_DEFINITION_EXAMPLE = """--body "{
\\"Id\\": \\"be79875a-2cc4-40d5-8958-566017875b39\\",
\\"UserName\\": \\"MyUserName\\",
\\"Password\\": \\"MyPass\\",
\\"CustomData\\": \\"MyCustomData\\",
\\"Mechanisms\\": \\"SCRAM-SHA-256\\"
\\"DatabaseName\\": \\"MyDb\\",
\\"Roles\\": [ {\\"Role\\": \\"myReadRole\\",\\"Db\\": \\"MyDb\\"}]
}"
"""

SQL_MATERIALIZEDVIEW_DEFINITION_EXAMPLE = """--materialized-view-definition -m '{
    \"sourceCollectionId\": \"MySourceCollectionName\",
    \"definition\": \"SELECT * FROM root r\"}'
"""

SQL_GREMLIN_INDEXING_POLICY_EXAMPLE = """--idx "{
    \\"indexingMode\\": \\"consistent\\",
    \\"automatic\\": true,
    \\"includedPaths\\": [{\\"path\\": \\"/*\\"}],
    \\"excludedPaths\\": [{ \\"path\\": \\"/headquarters/employees/?\\"}, { \\"path\\": \\"/\\\\"_etag\\\\"/?\\"}]
}"
"""

SQL_UNIQUE_KEY_POLICY_EXAMPLE = """--unique-key-policy "{
    \\"uniqueKeys\\": [{\\"paths\\": [\\"/path/to/key1\\"]}, {\\"paths\\": [\\"/path/to/key2\\"]}]
}"
"""

SQL_CLIENT_ENCRYPTION_POLICY_EXAMPLE = """--cep "{
    \\"includedPaths\\": [{\\"path\\": \\"/path1\\",\\"clientEncryptionKeyId\\": \\"key1\\",\\"encryptionAlgorithm\\": \\"AEAD_AES_256_CBC_HMAC_SHA256\\",\\"encryptionType\\": \\"Deterministic\\"}],
    \\"policyFormatVersion\\": 2}"
"""

SQL_GREMLIN_CONFLICT_RESOLUTION_POLICY_EXAMPLE = """--conflict-resolution-policy "{
    \\"mode\\": \\"lastWriterWins\\",
    \\"conflictResolutionPath\\": \\"/path\\"
}"
"""


def load_arguments(self, _):
    from knack.arguments import CLIArgumentType
    account_name_type = CLIArgumentType(options_list=['--account-name', '-a'], help="Cosmosdb account name.")

    # Managed Cassandra Cluster
    for scope in [
            'managed-cassandra cluster create',
            'managed-cassandra cluster update',
            'managed-cassandra cluster show',
            'managed-cassandra cluster delete',
            'managed-cassandra cluster deallocate',
            'managed-cassandra cluster backup list',
            'managed-cassandra cluster backup show']:
        with self.argument_context(scope) as c:
            c.argument('cluster_name', options_list=['--cluster-name', '-c'], help="Cluster Name", required=True)

        # Managed Cassandra Cluster
        with self.argument_context('managed-cassandra cluster deallocate') as c:
            c.argument('force', options_list=['--force', '-f'], help="Force to deallocate the cluster", required=False)

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
            c.argument("cluster_type", options_list=['--cluster-type'], help="Type of the cluster, can be Production or NonProduction. If set to Production, operations on cluster might have restrictions.", arg_type=get_enum_type(['Production', 'NonProduction']))
            c.argument('extensions', nargs='*', help="A set of extensions that will be effective on the cluster. It will replace the entire set of extensions with new set. Use \"\" to remove all. Now Available: cassandra-lucene-index.")

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
            c.argument('server_port', options_list=['--ldap-server-port'], help="Port of the LDAP server. Defaults to 636")
            c.argument('service_user_distinguished_name', options_list=['--ldap-service-user-dn'], help="Distinguished name of the look up user account, who can look up user details on authentication.")
            c.argument('service_user_password', options_list=['--ldap-svc-user-pwd'], help="Password of the look up user.")
            c.argument('search_base_distinguished_name', options_list=['--ldap-search-base-dn'], help="Distinguished name of the object to start the recursive search of users from.")
            c.argument('search_filter_template', options_list=['--ldap-search-filter'], help="Template to use for searching. Defaults to (cn=%s) where %s will be replaced by the username used to login. While using this parameter from Windows Powershell (not Windows CommandPrompt or Linux) there is a known issue with escaping special characters, so pass as \"\"\"(cn=%s)\"\"\" instead.")
            c.argument('server_certificates', nargs='+', validator=validate_server_certificates, options_list=['--ldap-server-certs'], help="LDAP server certificate. It should have subject alternative name(SAN) DNS Name entry matching the hostname of the LDAP server.")

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

    # Mongo Cluster
    with self.argument_context('cosmosdb mongocluster') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the Cluster", required=True)

    with self.argument_context('cosmosdb mongocluster create') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the Cluster", required=True)
        c.argument('tags', arg_type=tags_type)
        c.argument('administrator_login', options_list=['--administrator-login', '-a'], help="The initial administrator user to be configured when a cluster is created", required=True)
        c.argument('administrator_login_password', options_list=['--administrator-login-password', '-p'], help="The initial administrator password to be configured when a cluster is created", required=True)
        c.argument('server_version', options_list=['--server-version'], help="The server version of the mongo cluster", required=True)
        c.argument('shard_node_tier', options_list=['--shard-node-tier'], help="The node tier for mongo cluster.", required=True, arg_group='Shard')
        c.argument('shard_node_ha', arg_type=get_three_state_flag(), options_list=['--shard-node-ha'], help="If enabled the cluster has HA.", required=True, arg_group='Shard')
        c.argument('shard_node_disk_size_gb', options_list=['--shard-node-disk-size-gb', '-d'], help="The node disk size for mongo cluster.", required=True, arg_group='Shard')
        c.argument('shard_node_count', options_list=['--shard-node-count'], help="The node count for mongo cluster.", required=True, arg_group='Shard')

    with self.argument_context('cosmosdb mongocluster update') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)
        c.argument('tags', arg_type=tags_type)
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the Cluster", required=True)
        c.argument('administrator_login', options_list=['--administrator-login', '-a'], help="The initial administrator user to be configured when a cluster is created")
        c.argument('administrator_login_password', options_list=['--administrator-login-password', '-p'], help="The initial administrator password to be configured when a cluster is created")
        c.argument('server_version', options_list=['--server-version'], help="The server version of the mongo cluster")
        c.argument('shard_node_tier', options_list=['--shard-node-tier'], help="The node tier for mongo cluster.", arg_group='Shard')
        c.argument('shard_node_ha', arg_type=get_three_state_flag(), options_list=['--shard-node-ha'], help="If enabled the cluster has HA.", arg_group='Shard')
        c.argument('shard_node_disk_size_gb', options_list=['--shard-node-disk-size-gb', '-d'], help="The node disk size for mongo cluster.", arg_group='Shard')

    with self.argument_context('cosmosdb mongocluster list') as c:
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.')

    with self.argument_context('cosmosdb mongocluster show') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', required=True)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', required=True)

    with self.argument_context('cosmosdb mongocluster delete') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)

    with self.argument_context('cosmosdb mongocluster firewall rule') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)

    with self.argument_context('cosmosdb mongocluster firewall rule create') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)
        c.argument('rule_name', options_list=['--rule-name'], help="Name of the firewall rule.", required=True)
        c.argument('start_ip_address', options_list=['--start-ip-address'], help="Start IP address of the firewall rule", required=True)
        c.argument('end_ip_address', options_list=['--end-ip-address'], help="End IP address of the firewall rule", required=True)

    with self.argument_context('cosmosdb mongocluster firewall rule update') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)
        c.argument('rule_name', options_list=['--rule-name'], help="Name of the firewall rule.", required=True)
        c.argument('start_ip_address', options_list=['--start-ip-address'], help="Start IP address of the firewall rule")
        c.argument('end_ip_address', options_list=['--end-ip-address'], help="End IP address of the firewall rule")

    with self.argument_context('cosmosdb mongocluster firewall rule list') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', required=True)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', required=True)

    with self.argument_context('cosmosdb mongocluster firewall rule show') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', required=True)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', required=True)
        c.argument('rule_name', options_list=['--rule-name'], help="Name of the firewall rule.", required=True)

    with self.argument_context('cosmosdb mongocluster firewall rule delete') as c:
        c.argument('cluster_name', completer=None, options_list=['--cluster-name', '-c'], help='Name of the Cosmos DB Mongo Cluster.', id_part=None)
        c.argument('resource_group', completer=None, options_list=['--resource-group', '-g'], help='Name of the resource group of mongo cluster.', id_part=None)
        c.argument('rule_name', options_list=['--rule-name'], help="Name of the firewall rule.", required=True)

    # Services
    with self.argument_context('cosmosdb service') as c:
        c.argument('account_name', completer=None, options_list=['--account-name', '-a'], help='Name of the Cosmos DB database account.', id_part=None)
        c.argument('resource_group_name', completer=None, options_list=['--resource-group-name', '-g'], help='Name of the resource group of the database account.', id_part=None)
        c.argument('service_kind', options_list=['--kind', '-k'], help="Service kind")
        c.argument('service_name', options_list=['--name', '-n'], help="Service Name.")
        c.argument('instance_count', options_list=['--count', '-c'], help="Instance Count.")
        c.argument('instance_size', options_list=['--size'], help="Instance Size. Possible values are: Cosmos.D4s, Cosmos.D8s, Cosmos.D16s etc")

    with self.argument_context('cosmosdb service create') as c:
        c.argument('instance_size', options_list=['--size'], help="Instance Size. Possible values are: Cosmos.D4s, Cosmos.D8s, Cosmos.D16s etc")

    # Mongo role definition
    with self.argument_context('cosmosdb mongodb role definition') as c:
        c.argument('account_name', account_name_type, id_part=None)
        c.argument('mongo_role_definition_id', options_list=['--id', '-i'], validator=validate_mongo_role_definition_id, help="Unique ID for the Mongo Role Definition.")
        c.argument('mongo_role_definition_body', options_list=['--body', '-b'], validator=validate_mongo_role_definition_body, completer=FilesCompleter(), help="Role Definition body with Id (Optional for create), Type (Default is CustomRole), DatabaseName, Privileges, Roles.  You can enter it as a string or as a file, e.g., --body @mongo-role_definition-body-file.json or " + MONGO_ROLE_DEFINITION_EXAMPLE)

    # Mongo user definition
    with self.argument_context('cosmosdb mongodb user definition') as c:
        c.argument('account_name', account_name_type, id_part=None)
        c.argument('mongo_user_definition_id', options_list=['--id', '-i'], validator=validate_mongo_user_definition_id, help="Unique ID for the Mongo User Definition.")
        c.argument('mongo_user_definition_body', options_list=['--body', '-b'], validator=validate_mongo_user_definition_body, completer=FilesCompleter(), help="User Definition body with Id (Optional for create), UserName, Password, DatabaseName, CustomData, Mechanisms, Roles.  You can enter it as a string or as a file, e.g., --body @mongo-user_definition-body-file.json or " + MONGO_USER_DEFINITION_EXAMPLE)

    with self.argument_context('cosmosdb') as c:
        c.argument('account_name', arg_type=name_type, help='Name of the Cosmos DB database account', completer=get_resource_name_completion_list('Microsoft.DocumentDb/databaseAccounts'), id_part='name')
        c.argument('database_id', options_list=['--db-name', '-d'], help='Database Name')

    # CosmosDB account create with gremlin and tables to restore
    with self.argument_context('cosmosdb create') as c:
        c.argument('account_name', completer=None)
        c.argument('enable_free_tier', arg_type=get_three_state_flag(), help="If enabled the account is free-tier.", is_preview=True)
        c.argument('assign_identity', nargs='*', help="Assign system or user assigned identities separated by spaces. Use '[system]' to refer system assigned identity.")
        c.argument('key_uri', help="The URI of the key vault")
        c.argument('is_restore_request', options_list=['--is-restore-request', '-r'], arg_type=get_three_state_flag(), help="Restore from an existing/deleted account.", is_preview=True, arg_group='Restore')
        c.argument('restore_source', help="The restorable-database-account Id of the source account from which the account has to be restored. Required if --is-restore-request is set to true.", is_preview=True, arg_group='Restore')
        c.argument('restore_timestamp', action=UtcDatetimeAction, help="The timestamp to which the account has to be restored to. Required if --is-restore-request is set to true.", is_preview=True, arg_group='Restore')
        c.argument('databases_to_restore', nargs='+', action=CreateDatabaseRestoreResource, is_preview=True, arg_group='Restore')
        c.argument('gremlin_databases_to_restore', nargs='+', action=CreateGremlinDatabaseRestoreResource, is_preview=True, arg_group='Restore')
        c.argument('tables_to_restore', nargs='+', action=CreateTableRestoreResource, is_preview=True, arg_group='Restore')
        c.argument('enable_partition_merge', arg_type=get_three_state_flag(), help="Flag to enable partition merge on the account.")

    for scope in ['cosmosdb create', 'cosmosdb update']:
        with self.argument_context(scope) as c:
            c.ignore('resource_group_location')
            c.argument('locations', nargs='+', action=CreateLocation)
            c.argument('tags', arg_type=tags_type)
            c.argument('default_consistency_level', arg_type=get_enum_type(DefaultConsistencyLevel), help="default consistency level of the Cosmos DB database account")
            c.argument('max_staleness_prefix', type=int, help="when used with Bounded Staleness consistency, this value represents the number of stale requests tolerated. Accepted range for this value is 1 - 2,147,483,647")
            c.argument('max_interval', type=int, help="when used with Bounded Staleness consistency, this value represents the time amount of staleness (in seconds) tolerated. Accepted range for this value is 1 - 100")
            c.argument('ip_range_filter', nargs='+', options_list=['--ip-range-filter'], validator=validate_ip_range_filter, help="firewall support. Specifies the set of IP addresses or IP address ranges in CIDR form to be included as the allowed list of client IPs for a given database account. IP addresses/ranges must be comma-separated and must not contain any spaces")
            c.argument('kind', arg_type=get_enum_type(DatabaseAccountKind), help='The type of Cosmos DB database account to create')
            c.argument('enable_automatic_failover', arg_type=get_three_state_flag(), help='Enables automatic failover of the write region in the rare event that the region is unavailable due to an outage. Automatic failover will result in a new write region for the account and is chosen based on the failover priorities configured for the account.')
            c.argument('capabilities', nargs='+', validator=validate_capabilities, help='set custom capabilities on the Cosmos DB database account.')
            c.argument('enable_virtual_network', arg_type=get_three_state_flag(), help='Enables virtual network on the Cosmos DB database account')
            c.argument('virtual_network_rules', nargs='+', validator=validate_virtual_network_rules, help='ACL\'s for virtual network')
            c.argument('enable_multiple_write_locations', arg_type=get_three_state_flag(), help="Enable Multiple Write Locations")
            c.argument('disable_key_based_metadata_write_access', arg_type=get_three_state_flag(), help="Disable write operations on metadata resources (databases, containers, throughput) via account keys")
            c.argument('public_network_access', options_list=['--public-network-access', '-p'], arg_type=get_enum_type(['ENABLED', 'DISABLED', 'SECUREDBYPERIMETER']), help="Sets public network access in server to either Enabled, Disabled, or SecuredByPerimeter.")
            c.argument('enable_analytical_storage', arg_type=get_three_state_flag(), help="Flag to enable log storage on the account.")
            c.argument('network_acl_bypass', arg_type=get_enum_type(NetworkAclBypass), options_list=['--network-acl-bypass'], help="Flag to enable or disable Network Acl Bypass.")
            c.argument('network_acl_bypass_resource_ids', nargs='+', options_list=['--network-acl-bypass-resource-ids', '-i'], help="List of Resource Ids to allow Network Acl Bypass.")
            c.argument('backup_interval', type=int, help="the frequency(in minutes) with which backups are taken (only for accounts with periodic mode backups)", arg_group='Backup Policy')
            c.argument('backup_retention', type=int, help="the time(in hours) for which each backup is retained (only for accounts with periodic mode backups)", arg_group='Backup Policy')
            c.argument('backup_redundancy', arg_type=get_enum_type(BackupStorageRedundancy), help="The redundancy type of the backup Storage account", arg_group='Backup Policy')
            c.argument('server_version', arg_type=get_enum_type(ServerVersion), help="Valid only for MongoDB accounts.")
            c.argument('default_identity', help="The primary identity to access key vault in CMK related features. e.g. 'FirstPartyIdentity', 'SystemAssignedIdentity' and more.")
            c.argument('analytical_storage_schema_type', options_list=['--analytical-storage-schema-type', '--as-schema'], arg_type=get_enum_type(AnalyticalStorageSchemaType), help="Schema type for analytical storage.", arg_group='Analytical Storage Configuration')
            c.argument('backup_policy_type', arg_type=get_enum_type(BackupPolicyType), help="The type of backup policy of the account to create", arg_group='Backup Policy')
            c.argument('continuous_tier', arg_type=get_enum_type(ContinuousTier), help="The tier of Continuous backup", arg_group='Backup Policy')
            c.argument('enable_materialized_views', options_list=['--enable-materialized-views', '--enable-mv'], arg_type=get_three_state_flag(), help="Flag to enable MaterializedViews on the account.", is_preview=True)
            c.argument('enable_burst_capacity', arg_type=get_three_state_flag(), help="Flag to enable burst capacity on the account.", is_preview=True)
            c.argument('enable_priority_based_execution', options_list=['--enable-priority-based-execution', '--enable-pbe'], arg_type=get_three_state_flag(), help="Flag to enable priority based execution on the account.", is_preview=True)
            c.argument('default_priority_level', arg_type=get_enum_type(DefaultPriorityLevel), help="Default Priority Level of Request if not specified.", is_preview=True)
            c.argument('enable_prpp_autoscale', arg_type=get_three_state_flag(), help="Enable or disable PerRegionPerPartitionAutoscale.", is_preview=True)
            c.argument('enable_partition_merge', arg_type=get_three_state_flag(), help="Flag to enable partition merge on the account.")

    with self.argument_context('cosmosdb update') as c:
        c.argument('key_uri', help="The URI of the key vault", is_preview=True)

    with self.argument_context('cosmosdb restore') as c:
        c.argument('target_database_account_name', options_list=['--target-database-account-name', '-n'], help='Name of the new target Cosmos DB database account after the restore')
        c.argument('account_name', completer=None, options_list=['--account-name', '-a'], help='Name of the source Cosmos DB database account for the restore', id_part=None)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the account has to be restored to.")
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help="This is the write region of the restored account. This is also the location of the source account where its backups are located if source_backup_location is not provided.")
        c.argument('databases_to_restore', nargs='+', action=CreateDatabaseRestoreResource)
        c.argument('gremlin_databases_to_restore', nargs='+', action=CreateGremlinDatabaseRestoreResource, is_preview=True)
        c.argument('tables_to_restore', nargs='+', action=CreateTableRestoreResource, is_preview=True)
        c.argument('assign_identity', nargs='*', help="Assign system or user assigned identities separated by spaces. Use '[system]' to refer system assigned identity.")
        c.argument('default_identity', help="The primary identity to access key vault in CMK related features. e.g. 'FirstPartyIdentity', 'SystemAssignedIdentity' and more.")
        c.argument('public_network_access', options_list=['--public-network-access', '-p'], arg_type=get_enum_type(['ENABLED', 'DISABLED']), help="Sets public network access in server to either Enabled or Disabled.")
        c.argument('source_backup_location', help="This is the location of the source account where backups are located. Provide this value if the source and target are in different locations.", is_preview=True)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True)

    # Restorable Database Accounts
    with self.argument_context('cosmosdb restorable-database-account show') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=False)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=False)

    with self.argument_context('cosmosdb restorable-database-account list') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=False)
        c.argument('account_name', options_list=['--account-name', '-n'], help="Name of the Account", required=False, id_part=None)

    # Restorable Sql Containers
    with self.argument_context('cosmosdb sql restorable-container') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restorable_sql_database_rid', options_list=['--database-rid', '-d'], help="Rid of the database", required=True)
        c.argument('start_time', options_list=['--start-time', '-s'], help="Start time of restorable Sql container event feed", required=False)
        c.argument('end_time', options_list=['--end-time', '-e'], help="End time of restorable Sql container event feed", required=False)

    # Restorable Mongodb Collections
    with self.argument_context('cosmosdb mongodb restorable-collection') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restorable_mongodb_database_rid', options_list=['--database-rid', '-d'], help="Rid of the database", required=True)
        c.argument('start_time', options_list=['--start-time', '-s'], help="Start time of restorable MongoDB collections event feed", required=False)
        c.argument('end_time', options_list=['--end-time', '-e'], help="End time of restorable MongoDB collections event feed", required=False)

    # Restorable Gremlin Databases
    with self.argument_context('cosmosdb gremlin restorable-database') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)

    # Restorable Gremlin Graphs
    with self.argument_context('cosmosdb gremlin restorable-graph') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restorable_gremlin_database_rid', options_list=['--database-rid', '-d'], help="Rid of the gremlin database", required=True)
        c.argument('start_time', options_list=['--start-time', '-s'], help="Start time of restorable Gremlin graph event feed", required=False)
        c.argument('end_time', options_list=['--end-time', '-e'], help="End time of restorable Gremlin graph event feed", required=False)

    # Restorable Gremlin Resources
    with self.argument_context('cosmosdb gremlin restorable-resource') as c:
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the account", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restore_location', options_list=['--restore-location', '-r'], help="The region of the restore.", required=True)
        c.argument('restore_timestamp_in_utc', options_list=['--restore-timestamp', '-t'], help="The timestamp of the restore", required=True)

    # Restorable Tables
    with self.argument_context('cosmosdb table restorable-table') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('start_time', options_list=['--start-time', '-s'], help="Start time of restorable tables event feed", required=False)
        c.argument('end_time', options_list=['--end-time', '-e'], help="End time of restorable tables event feed", required=False)

    # Restorable table Resources
    with self.argument_context('cosmosdb table restorable-resource') as c:
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the account", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restore_location', options_list=['--restore-location', '-r'], help="The region of the restore.", required=True)
        c.argument('restore_timestamp_in_utc', options_list=['--restore-timestamp', '-t'], help="The timestamp of the restore", required=True)

    # Retrive Gremlin Graph Backup Info
    database_name_type = CLIArgumentType(options_list=['--database-name', '-d'], help='Database name.')
    with self.argument_context('cosmosdb gremlin retrieve-latest-backup-time') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB Gremlin database name')
        c.argument('graph_name', options_list=['--graph-name', '-n'], required=True, help='Name of the CosmosDB Gremlin graph name')
        c.argument('location', options_list=['--location', '-l'], help="Location of the account", required=True)

    # Retrive Table Backup Info
    with self.argument_context('cosmosdb table retrieve-latest-backup-time') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('table_name', options_list=['--table-name', '-n'], required=True, help='Name of the CosmosDB Table name')
        c.argument('location', options_list=['--location', '-l'], help="Location of the account", required=True)

    with self.argument_context('cosmosdb dts') as c:
        c.argument('account_name', account_name_type, id_part=None, help='Name of the CosmosDB database account.')

    job_name_type = CLIArgumentType(options_list=['--job-name', '-n'], help='Name of the Data Transfer Job. A random job name will be generated if not passed.')
    with self.argument_context('cosmosdb dts copy') as c:
        c.argument('job_name', job_name_type)
        c.argument('source_cassandra_table', nargs='+', action=AddCassandraTableAction, help='Source cassandra table')
        c.argument('source_mongo', nargs='+', action=AddMongoCollectionAction, help='Source mongo collection')
        c.argument('source_sql_container', nargs='+', action=AddSqlContainerAction, help='Source sql container')
        c.argument('dest_cassandra_table', nargs='+', action=AddCassandraTableAction, help='Destination cassandra table')
        c.argument('dest_mongo', nargs='+', action=AddMongoCollectionAction, help='Destination mongo collection')
        c.argument('dest_sql_container', nargs='+', action=AddSqlContainerAction, help='Destination sql container')
        c.argument('worker_count', type=int, help='Worker count')

    for scope in [
            'cosmosdb dts show',
            'cosmosdb dts pause',
            'cosmosdb dts resume',
            'cosmosdb dts cancel']:
        with self.argument_context(scope) as c:
            c.argument('job_name', options_list=['--job-name', '-n'], help='Name of the Data Transfer Job.', required=True)

    with self.argument_context('cosmosdb copy create') as c:
        c.argument('job_name', job_name_type)
        c.argument('src_account', help='Name of the Azure Cosmos DB source database account.', completer=get_resource_name_completion_list('Microsoft.DocumentDb/databaseAccounts'), id_part='name')
        c.argument('dest_account', help='Name of the Azure Cosmos DB destination database account.', completer=get_resource_name_completion_list('Microsoft.DocumentDb/databaseAccounts'), id_part='name')
        c.argument('src_cassandra', nargs='+', arg_group='Azure Cosmos DB API for Apache Cassandra table copy', action=AddCassandraTableAction, help='Source Cassandra table details')
        c.argument('src_mongo', nargs='+', arg_group='Azure Cosmos DB API for MongoDB collection copy', action=AddMongoCollectionAction, help='Source Mongo collection details')
        c.argument('src_nosql', nargs='+', arg_group='Azure Cosmos DB API for NoSQL container copy', action=AddSqlContainerAction, help='Source NoSql container details')
        c.argument('dest_cassandra', nargs='+', arg_group='Azure Cosmos DB API for Apache Cassandra table copy', action=AddCassandraTableAction, help='Destination Cassandra table details')
        c.argument('dest_mongo', nargs='+', arg_group='Azure Cosmos DB API for MongoDB collection copy', action=AddMongoCollectionAction, help='Destination Mongo collection details')
        c.argument('dest_nosql', nargs='+', arg_group='Azure Cosmos DB API for NoSQL container copy', action=AddSqlContainerAction, help='Destination NoSql container details')
        c.argument('host_copy_on_src', arg_type=get_three_state_flag(), help=argparse.SUPPRESS)
        c.argument('worker_count', type=int, help=argparse.SUPPRESS)
        c.argument('mode', help='Copy Mode (Online / Offline)')

    for scope in [
            'cosmosdb copy list',
            'cosmosdb copy show',
            'cosmosdb copy pause',
            'cosmosdb copy resume',
            'cosmosdb copy cancel',
            'cosmosdb copy complete']:
        with self.argument_context(scope) as c:
            c.argument('account_name', options_list=["--account-name", "-a"], id_part=None, required=True, help='Azure Cosmos DB account name where the job is created. Use --dest-account value from create job command.')

    for scope in [
            'cosmosdb copy show',
            'cosmosdb copy pause',
            'cosmosdb copy resume',
            'cosmosdb copy cancel',
            'cosmosdb copy complete']:
        with self.argument_context(scope) as c:
            c.argument('job_name', options_list=['--job-name', '-n'], help='Name of the container copy job.', required=True)

    max_throughput_type = CLIArgumentType(options_list=['--max-throughput'], help='The maximum throughput resource can scale to (RU/s). Provided when the resource is autoscale enabled. The minimum value can be 4000 (RU/s)')


# SQL container
    with self.argument_context('cosmosdb sql container') as c:
        c.argument('account_name', account_name_type, id_part=None)
        c.argument('database_name', database_name_type)
        c.argument('container_name', options_list=['--name', '-n'], help="Container name")
        c.argument('partition_key_path', options_list=['--partition-key-path', '-p'], help='Partition Key Path, e.g., \'/address/zipcode\'')
        c.argument('partition_key_version', type=int, options_list=['--partition-key-version'], help='The version of partition key.')
        c.argument('default_ttl', options_list=['--ttl'], type=int, help='Default TTL. If the value is missing or set to "-1", items don’t expire. If the value is set to "n", items will expire "n" seconds after last modified time.')
        c.argument('indexing_policy', options_list=['--idx'], type=shell_safe_json_parse, completer=FilesCompleter(), help='Indexing Policy, you can enter it as a string or as a file, e.g., --idx @policy-file.json or ' + SQL_GREMLIN_INDEXING_POLICY_EXAMPLE)
        c.argument('client_encryption_policy', options_list=['--cep'], type=shell_safe_json_parse, completer=FilesCompleter(), validator=validate_client_encryption_policy, help='Client Encryption Policy, you can enter it as a string or as a file, e.g., --cep @policy-file.json or ' + SQL_CLIENT_ENCRYPTION_POLICY_EXAMPLE)
        c.argument('unique_key_policy', options_list=['--unique-key-policy', '-u'], type=shell_safe_json_parse, completer=FilesCompleter(), help='Unique Key Policy, you can enter it as a string or as a file, e.g., --unique-key-policy @policy-file.json or ' + SQL_UNIQUE_KEY_POLICY_EXAMPLE)
        c.argument('conflict_resolution_policy', options_list=['--conflict-resolution-policy', '-c'], type=shell_safe_json_parse, completer=FilesCompleter(), help='Conflict Resolution Policy, you can enter it as a string or as a file, e.g., --conflict-resolution-policy @policy-file.json or ' + SQL_GREMLIN_CONFLICT_RESOLUTION_POLICY_EXAMPLE)
        c.argument('max_throughput', max_throughput_type)
        c.argument('throughput', help='The throughput of SQL container (RU/s). Default value is 400. Omit this parameter if the database has shared throughput unless the container should have dedicated throughput.')
        c.argument('analytical_storage_ttl', options_list=['--analytical-storage-ttl', '-t'], type=int, help='Analytical TTL, when analytical storage is enabled.')
        c.argument('materialized_view_definition', options_list=['--materialized-view-definition', '-m'], type=shell_safe_json_parse, help='Materialized View Definition, you can enter it as a string or as a file, e.g., --materialized-view-definition @materializedview-definition-file.json or ' + SQL_MATERIALIZEDVIEW_DEFINITION_EXAMPLE)

    # Sql container partition merge
    database_name_type = CLIArgumentType(options_list=['--database-name', '-d'], help='Database name.')
    with self.argument_context('cosmosdb sql container merge') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB database name')
        c.argument('container_name', options_list=['--name', '-n'], required=True, help='Name of the CosmosDB collection')

    # mongodb collection partition merge
    with self.argument_context('cosmosdb mongodb collection merge') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the mongoDB database')
        c.argument('container_name', options_list=['--name', '-n'], required=True, help='Name of the mongoDB collection')

    # Sql database partition merge
    with self.argument_context('cosmosdb sql database merge') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', options_list=['--name', '-n'], required=True, help='Name of the CosmosDB database name')

    # mongodb database partition merge
    with self.argument_context('cosmosdb mongodb database merge') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', options_list=['--name', '-n'], required=True, help='Name of the mongoDB database')

    # Sql container partition retrieve throughput
    with self.argument_context('cosmosdb sql container retrieve-partition-throughput') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB database name')
        c.argument('container_name', options_list=['--name', '-n'], required=True, help='Name of the CosmosDB container')
        c.argument('physical_partition_ids', options_list=['--physical-partition-ids', '-p'], nargs='+', action=CreatePhysicalPartitionIdListAction, required=False, help='space separated list of physical partition ids')
        c.argument('all_partitions', arg_type=get_three_state_flag(), help="switch to retrieve throughput for all physical partitions")

    # Sql container partition redistribute throughput
    with self.argument_context('cosmosdb sql container redistribute-partition-throughput') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB database name')
        c.argument('container_name', options_list=['--name', '-n'], required=True, help='Name of the CosmosDB collection')
        c.argument('evenly_distribute', arg_type=get_three_state_flag(), help="switch to distribute throughput equally among all physical partitions")
        c.argument('target_partition_info', nargs='+', action=CreateTargetPhysicalPartitionThroughputInfoAction, required=False, help="information about desired target physical partition throughput eg: 0=1200 1=1200")
        c.argument('source_partition_info', nargs='+', action=CreateSourcePhysicalPartitionThroughputInfoAction, required=False, help="space separated source physical partition ids eg: 1 2")

    # Mongodb collection partition retrieve throughput
    with self.argument_context('cosmosdb mongodb collection retrieve-partition-throughput') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB database name')
        c.argument('collection_name', options_list=['--name', '-n'], required=True, help='Name of the CosmosDB container')
        c.argument('physical_partition_ids', options_list=['--physical-partition-ids', '-p'], nargs='+', action=CreatePhysicalPartitionIdListAction, required=False, help='space separated list of physical partition ids')
        c.argument('all_partitions', arg_type=get_three_state_flag(), help="switch to retrieve throughput for all physical partitions")

    # Mongodb collection partition redistribute throughput
    with self.argument_context('cosmosdb mongodb collection redistribute-partition-throughput') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True, help='Name of the CosmosDB database account')
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB database name')
        c.argument('collection_name', options_list=['--name', '-n'], required=True, help='Name of the CosmosDB collection')
        c.argument('evenly_distribute', arg_type=get_three_state_flag(), help="switch to distribute throughput equally among all physical partitions")
        c.argument('target_partition_info', nargs='+', action=CreateTargetPhysicalPartitionThroughputInfoAction, required=False, help="information about desired target physical partition throughput eg: '0=1200 1=1200'")
        c.argument('source_partition_info', nargs='+', action=CreateSourcePhysicalPartitionThroughputInfoAction, required=False, help="space separated source physical partition ids eg: 1 2")

    # SQL database restore
    with self.argument_context('cosmosdb sql database restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('database_name', options_list=['--name', '-n'], help="Database name", required=True)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the database needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)

    # SQL collection restore
    with self.argument_context('cosmosdb sql container restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('database_name', database_name_type, required=True)
        c.argument('container_name', options_list=['--name', '-n'], help="Container name", required=True)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the container needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)

    # MongoDB database restore
    with self.argument_context('cosmosdb mongodb database restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('database_name', options_list=['--name', '-n'], help="Database name", required=True)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the database needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)

    # MongoDB collection restore
    with self.argument_context('cosmosdb mongodb collection restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('database_name', database_name_type, required=True)
        c.argument('collection_name', options_list=['--name', '-n'], help="Collection name", required=True)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the collection needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)

    # Gremlin database restore
    with self.argument_context('cosmosdb gremlin database restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('database_name', options_list=['--name', '-n'], help="Name of the CosmosDB Gremlin database name", required=True)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the database needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)

    # Gremlin Graph restore
    with self.argument_context('cosmosdb gremlin graph restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('database_name', database_name_type, required=True, help='Name of the CosmosDB Gremlin database name')
        c.argument('graph_name', options_list=['--name', '-n'], help="Name of the CosmosDB Gremlin graph name", required=True)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the graph needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)

    # Table restore
    with self.argument_context('cosmosdb table restore') as c:
        c.argument('account_name', account_name_type, id_part=None, required=True)
        c.argument('table_name', options_list=['--table-name', '-n'], required=True, help='Name of the CosmosDB Table name')
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the Table needs to be restored to.", required=False)
        c.argument('disable_ttl', options_list=['--disable-ttl'], arg_type=get_three_state_flag(), help="Enable or disable restoring with ttl disabled.", is_preview=True, required=False)
