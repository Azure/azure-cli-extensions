# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long, too-many-statements

from enum import Enum

from azure.cli.core.commands.parameters import (
    get_resource_name_completion_list, name_type, get_enum_type, get_three_state_flag, get_datetime_type, get_location_type)

from azext_cosmosdb_preview._validators import (
    validate_capabilities, validate_virtual_network_rules, validate_ip_range_filter)

from azext_cosmosdb_preview.actions import (
    CreateLocation, CreateDatabaseRestoreResource)

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import DefaultConsistencyLevel, DatabaseAccountKind, ServerVersion


class BackupPolicyTypes(str, Enum):
    periodic = "Periodic"
    continuous = "Continuous"


def load_arguments(self, _):

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
        c.argument('restore_timestamp', arg_type=get_datetime_type(help="The timestamp to which the account has to be restored to. Required if --is-restore-request is set to true."), is_preview=True, arg_group='Restore')
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
        c.argument('restore_timestamp', options_list=['--restore-timestamp', '-t'], arg_type=get_datetime_type(help="The timestamp to which the account has to be restored to."))
        c.argument('location', arg_type=get_location_type(self.cli_ctx), help="The location of the source account from which restore is triggered. This will also be the write region of the restored account")
        c.argument('databases_to_restore', nargs='+', action=CreateDatabaseRestoreResource)

    # Restorable Database Accounts
    with self.argument_context('cosmosdb restorable-database-account') as c:
        c.argument('location', options_list=['--location', '-l'], help="Location", required=False)
        c.argument('instance_id', options_list=['--instance-id', '-i'], help="InstanceId of the Account", required=False)

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
