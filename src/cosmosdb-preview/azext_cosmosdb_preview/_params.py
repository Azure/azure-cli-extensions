# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements

from enum import Enum

from argcomplete.completers import FilesCompleter

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, name_type, get_enum_type, get_three_state_flag, get_location_type)

from azext_cosmosdb_preview._validators import (
    validate_capabilities, validate_virtual_network_rules, validate_ip_range_filter,
    validate_role_definition_body,
    validate_role_definition_id,
    validate_fully_qualified_role_definition_id,
    validate_role_assignment_id,
    validate_scope,
    validate_gossip_certificates,
    validate_client_certificates,
    validate_seednodes,
    validate_node_count)

from azext_cosmosdb_preview.actions import (
    CreateLocation, CreateDatabaseRestoreResource, UtcDatetimeAction)

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import DefaultConsistencyLevel, DatabaseAccountKind, ServerVersion


class BackupPolicyTypes(str, Enum):
    periodic = "Periodic"
    continuous = "Continuous"


SQL_ROLE_DEFINITION_EXAMPLE = """--body "{ \\"Id\\": \\"be79875a-2cc4-40d5-8958-566017875b39\\", \\"RoleName\\": \\"My Read Write Role\\", \\"Type\\": \\"CustomRole\\", \\"AssignableScopes\\": [ \\"/\\" ], \\"DataActions\\": [ \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/create\\", \\"Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read\\" ]}"
"""


def load_arguments(self, _):
    from knack.arguments import CLIArgumentType
    from azure.cli.core.commands.parameters import tags_type

    with self.argument_context('cosmosdb') as c:
        c.argument('account_name', arg_type=name_type, help='Name of the Cosmos DB database account', completer=get_resource_name_completion_list('Microsoft.DocumentDb/databaseAccounts'), id_part='name')
        c.argument('database_id', options_list=['--db-name', '-d'], help='Database Name')

    with self.argument_context('cosmosdb create') as c:
        c.argument('account_name', completer=None)
        c.argument('key_uri', help="The URI of the key vault", is_preview=True)
        c.argument('enable_free_tier', arg_type=get_three_state_flag(), help="If enabled the account is free-tier.", is_preview=True)
        c.argument('server_version', arg_type=get_enum_type(ServerVersion), help="Valid only for MongoDB accounts.", is_preview=True)
        c.argument('is_restore_request', options_list=['--is-restore-request', '-r'], arg_type=get_three_state_flag(), help="Restore from an existing/deleted account.", is_preview=True, arg_group='Restore')
        c.argument('restore_source', help="The restorable-database-account Id of the source account from which the account has to be restored. Required if --is-restore-request is set to true.", is_preview=True, arg_group='Restore')
        c.argument('restore_timestamp', action=UtcDatetimeAction, help="The timestamp to which the account has to be restored to. Required if --is-restore-request is set to true.", is_preview=True, arg_group='Restore')
        c.argument('databases_to_restore', nargs='+', action=CreateDatabaseRestoreResource, is_preview=True, arg_group='Restore')
        c.argument('backup_policy_type', arg_type=get_enum_type(BackupPolicyTypes), help="The type of backup policy of the account to create", arg_group='Backup Policy')

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
            c.argument('enable_public_network', options_list=['--enable-public-network', '-e'], arg_type=get_three_state_flag(), help="Enable or disable public network access to server.")
            c.argument('enable_analytical_storage', arg_type=get_three_state_flag(), help="Flag to enable log storage on the account.", is_preview=True)
            c.argument('backup_interval', type=int, help="the frequency(in minutes) with which backups are taken (only for accounts with periodic mode backups)", arg_group='Backup Policy')
            c.argument('backup_retention', type=int, help="the time(in hours) for which each backup is retained (only for accounts with periodic mode backups)", arg_group='Backup Policy')

    with self.argument_context('cosmosdb restore') as c:
        c.argument('target_database_account_name', options_list=['--target-database-account-name', '-n'], help='Name of the new target Cosmos DB database account after the restore')
        c.argument('account_name', completer=None, options_list=['--account-name', '-a'], help='Name of the source Cosmos DB database account for the restore', id_part=None)
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], action=UtcDatetimeAction, help="The timestamp to which the account has to be restored to.")
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help="The location of the source account from which restore is triggered. This will also be the write region of the restored account")
        c.argument('databases_to_restore', nargs='+', action=CreateDatabaseRestoreResource)

    # Restorable Database Accounts
    with self.argument_context('cosmosdb restorable-database-account show') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=False)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=False)

    with self.argument_context('cosmosdb restorable-database-account list') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=False)
        c.argument('account_name', options_list=['--account-name', '-n'], help="Name of the Account", required=False, id_part=None)

    # Restorable Sql Databases
    with self.argument_context('cosmosdb sql restorable-database') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)

    # Restorable Sql Containers
    with self.argument_context('cosmosdb sql restorable-container') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restorable_sql_database_rid', options_list=['--database-rid', '-d'], help="Rid of the database", required=True)

    # Restorable Sql Resources
    with self.argument_context('cosmosdb sql restorable-resource') as c:
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the account", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restore_location', options_list=['--restore-location', '-r'], help="The region of the restore.", required=True)
        c.argument('restore_timestamp_in_utc', options_list=['--restore-timestamp', '-t'], help="The timestamp of the restore", required=True)

    # Restorable Mongodb Databases
    with self.argument_context('cosmosdb mongodb restorable-database') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)

    # Restorable Mongodb Collections
    with self.argument_context('cosmosdb mongodb restorable-collection') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restorable_mongodb_database_rid', options_list=['--database-rid', '-d'], help="Rid of the database", required=True)

    # Restorable mongodb Resources
    with self.argument_context('cosmosdb mongodb restorable-resource') as c:
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the account", required=True)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=True)
        c.argument('restore_location', options_list=['--restore-location', '-r'], help="The region of the restore.", required=True)
        c.argument('restore_timestamp_in_utc', options_list=['--restore-timestamp', '-t'], help="The timestamp of the restore", required=True)

    account_name_type = CLIArgumentType(options_list=['--account-name', '-a'], help="Cosmosdb account name.")

    # SQL role definition
    with self.argument_context('cosmosdb sql role definition') as c:
        c.argument('account_name', account_name_type, id_part=None)
        c.argument('role_definition_id', options_list=['--id', '-i'], validator=validate_role_definition_id, help="Unique ID for the Role Definition.")
        c.argument('role_definition_body', options_list=['--body', '-b'], validator=validate_role_definition_body, completer=FilesCompleter(), help="Role Definition body with Id (Optional for create), DataActions or Permissions, Type (Default is CustomRole), and AssignableScopes.  You can enter it as a string or as a file, e.g., --body @rdbody-file.json or " + SQL_ROLE_DEFINITION_EXAMPLE)

    # SQL role assignment
    with self.argument_context('cosmosdb sql role assignment') as c:
        c.argument('account_name', account_name_type, id_part=None)
        c.argument('role_assignment_id', options_list=['--role-assignment-id', '-i'], validator=validate_role_assignment_id, help="Optional for Create. Unique ID for the Role Assignment. If not provided, a new GUID will be used.")
        c.argument('role_definition_id', options_list=['--role-definition-id', '-d'], validator=validate_fully_qualified_role_definition_id, help="Unique ID of the Role Definition that this Role Assignment refers to.")
        c.argument('role_definition_name', options_list=['--role-definition-name', '-n'], help="Unique Name of the Role Definition that this Role Assignment refers to. Eg. 'Contoso Reader Role'.")
        c.argument('scope', validator=validate_scope, options_list=['--scope', '-s'], help="Data plane resource path at which this Role Assignment is being granted.")
        c.argument('principal_id', options_list=['--principal-id', '-p'], help="AAD Object ID of the principal to which this Role Assignment is being granted.")

    # Managed Cassandra Cluster
    for scope in [
            'managed-cassandra cluster create',
            'managed-cassandra cluster update',
            'managed-cassandra cluster show',
            'managed-cassandra cluster delete',
            'managed-cassandra cluster node-status']:
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
            c.argument('authentication_method', help="Authentication mode can be None or Cassandra. If None, no authentication will be required to connect to the Cassandra API. If Cassandra, then passwords will be used.")
            c.argument('hours_between_backups', help="The number of hours between backup attempts.")
            c.argument('repair_enabled', help="Enables automatic repair.")
            c.argument('client_certificates', nargs='+', validator=validate_client_certificates, help="If specified, enables client certificate authentication to the Cassandra API.")
            c.argument('gossip_certificates', help="A list of certificates that should be accepted by on-premise data centers.")
            c.argument('external_seed_nodes', nargs='+', validator=validate_seednodes, help="A list of ip addresses of the seed nodes of on-premise data centers.")
            c.argument('identity', help="Identity used to authenticate.")

    # Managed Cassandra Cluster
    with self.argument_context('managed-cassandra cluster create') as c:
        c.argument('location', options_list=['--location', '-l'], help="Azure Location of the Cluster", required=True)
        c.argument('delegated_management_subnet_id', options_list=['--delegated-management-subnet-id', '-s'], help="The resource id of a subnet where the ip address of the cassandra management server will be allocated. This subnet must have connectivity to the delegated_subnet_id subnet of each data center.", required=True)
        c.argument('initial_cassandra_admin_password', options_list=['--initial-cassandra-admin-password', '-i'], help="The intial password to be configured when a cluster is created for authentication_method Cassandra.")
        c.argument('restore_from_backup_id', help="The resource id of a backup. If provided on create, the backup will be used to prepopulate the cluster. The cluster data center count and node counts must match the backup.")
        c.argument('cluster_name_override', help="If a cluster must have a name that is not a valid azure resource name, this field can be specified to choose the Cassandra cluster name. Otherwise, the resource name will be used as the cluster name.")

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

    # Managed Cassandra Datacenter
    with self.argument_context('managed-cassandra datacenter create') as c:
        c.argument('data_center_location', options_list=['--data-center-location', '-l'], help="Azure Location of the Datacenter", required=True)
        c.argument('delegated_subnet_id', options_list=['--delegated-subnet-id', '-s'], help="The resource id of a subnet where ip addresses of the Cassandra virtual machines will be allocated. This must be in the same region as data_center_location.", required=True)
        c.argument('node_count', options_list=['--node-count', '-n'], validator=validate_node_count, help="The number of Cassandra virtual machines in this data center. The minimum value is 3.", required=True)

    # Managed Cassandra Datacenter
    with self.argument_context('managed-cassandra datacenter list') as c:
        c.argument('cluster_name', options_list=['--cluster-name', '-c'], help="Cluster Name", required=True)
