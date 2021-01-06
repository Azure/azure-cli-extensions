# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.util import CLIError
from knack.log import get_logger

from azext_cosmosdb_preview.vendored_sdks.azure_mgmt_cosmosdb.models import (
    ConsistencyPolicy,
    DatabaseAccountCreateUpdateParameters,
    DatabaseAccountUpdateParameters,
    RestoreReqeustDatabaseAccountCreateUpdateProperties,
    DefaultRequestDatabaseAccountCreateUpdateProperties,
    Location,
    DatabaseAccountKind,
    RestoreParameters,
    PeriodicModeBackupPolicy,
    PeriodicModeProperties,
    ContinuousModeBackupPolicy
)

logger = get_logger(__name__)


# pylint: disable=too-many-locals,too-many-statements,line-too-long
def cli_cosmosdb_create(cmd, client,
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
                        is_restore_request=None,
                        restore_source=None,
                        restore_timestamp=None,
                        backup_policy_type=None,
                        backup_interval=None,
                        backup_retention=None,
                        databases_to_restore=None):
    """Create a new Azure Cosmos DB database account."""
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    resource_client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    rg = resource_client.resource_groups.get(resource_group_name)
    resource_group_location = rg.location  # pylint: disable=no-member

    restore_timestamp_utc = None
    if restore_timestamp is not None:
        restore_timestamp_utc = _convert_to_utc_timestamp(restore_timestamp).isoformat()

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
                                    is_restore_request=is_restore_request,
                                    restore_source=restore_source,
                                    restore_timestamp=restore_timestamp_utc,
                                    backup_policy_type=backup_policy_type,
                                    backup_interval=backup_interval,
                                    backup_retention=backup_retention,
                                    databases_to_restore=databases_to_restore,
                                    arm_location=resource_group_location)


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
                             is_restore_request=None,
                             restore_source=None,
                             restore_timestamp=None,
                             backup_policy_type=None,
                             backup_interval=None,
                             backup_retention=None,
                             databases_to_restore=None,
                             arm_location=None):
    """Create a new Azure Cosmos DB database account."""
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

    api_properties = {}
    if kind == DatabaseAccountKind.mongo_db.value:
        api_properties['ServerVersion'] = server_version
    elif server_version is not None:
        raise CLIError('server-version is a valid argument only when kind is MongoDB.')

    create_mode = 'Default'
    if is_restore_request is not None:
        create_mode = 'Restore' if is_restore_request else 'Default'

    properties = None
    if create_mode == 'Restore':
        if restore_source is None or restore_timestamp is None:
            raise CLIError('restore-source and restore-timestamp should be provided for a restore request.')
        restore_parameters = RestoreParameters(
            restore_mode='PointInTime',
            restore_source=restore_source,
            restore_timestamp_in_utc=restore_timestamp
        )
        if databases_to_restore is not None:
            logger.debug(databases_to_restore)
            restore_parameters.databases_to_restore = databases_to_restore
        logger.debug(restore_parameters)
        properties = RestoreReqeustDatabaseAccountCreateUpdateProperties(
            locations=locations,
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
            restore_parameters=restore_parameters
        )
    else:
        properties = DefaultRequestDatabaseAccountCreateUpdateProperties(
            locations=locations,
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
            enable_free_tier=enable_free_tier
        )

    backup_policy = None
    if backup_policy_type is not None:
        if backup_policy_type.lower() == 'periodic':
            backup_policy = PeriodicModeBackupPolicy()
            if backup_interval is not None or backup_retention is not None:
                periodic_mode_properties = PeriodicModeProperties(
                    backup_interval_in_minutes=backup_interval,
                    backup_retention_interval_in_hours=backup_retention
                )
            backup_policy.periodic_mode_properties = periodic_mode_properties
        elif backup_policy_type.lower() == 'continuous':
            backup_policy = ContinuousModeBackupPolicy()
        else:
            raise CLIError('backup-policy-type argument is invalid.')
        properties.backup_policy = backup_policy
    elif backup_interval is not None or backup_retention is not None:
        backup_policy = PeriodicModeBackupPolicy()
        periodic_mode_properties = PeriodicModeProperties(
            backup_interval_in_minutes=backup_interval,
            backup_retention_interval_in_hours=backup_retention
        )
        backup_policy.periodic_mode_properties = periodic_mode_properties

    params = DatabaseAccountCreateUpdateParameters(
        location=arm_location,
        properties=properties,
        tags=tags,
        kind=kind)

    async_docdb_create = client.create_or_update(resource_group_name, account_name, params)
    docdb_account = async_docdb_create.result()
    docdb_account = client.get(resource_group_name, account_name)  # Workaround
    return docdb_account


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
                        backup_interval=None,
                        backup_retention=None):
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

    backup_policy = None
    if backup_interval is not None or backup_retention is not None:
        if isinstance(existing.backup_policy, PeriodicModeBackupPolicy):
            periodic_mode_properties = PeriodicModeProperties(
                backup_interval_in_minutes=backup_interval,
                backup_retention_interval_in_hours=backup_retention
            )
            backup_policy = existing.backup_policy
            backup_policy.periodic_mode_properties = periodic_mode_properties
        else:
            raise CLIError(
                'backup-interval and backup-retention can only be set for accounts with periodic backup policy.')

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
        backup_policy=backup_policy)
    async_docdb_update = client.update(resource_group_name, account_name, params)
    docdb_account = async_docdb_update.result()
    docdb_account = client.get(resource_group_name, account_name)  # Workaround
    return docdb_account


def cli_cosmosdb_restore(cmd,
                         client,
                         resource_group_name,
                         account_name,
                         target_database_account_name,
                         restore_timestamp,
                         location,
                         databases_to_restore=None):
    from azext_cosmosdb_preview._client_factory import cf_restorable_database_accounts
    restorable_database_accounts_client = cf_restorable_database_accounts(cmd.cli_ctx, [])
    restorable_database_accounts = restorable_database_accounts_client.list()
    restorable_database_accounts_list = list(restorable_database_accounts)
    target_restorable_account = None
    restore_timestamp_datetime_utc = _convert_to_utc_timestamp(restore_timestamp)
    for account in restorable_database_accounts_list:
        if account.account_name == account_name:
            if account.deletion_time is not None:
                if account.deletion_time >= restore_timestamp_datetime_utc >= account.creation_time:
                    target_restorable_account = account
                    break
            else:
                if restore_timestamp_datetime_utc >= account.creation_time:
                    target_restorable_account = account
                    break
    if target_restorable_account is None:
        raise CLIError("Cannot find a database account with name {} that is online at {}".format(account_name, restore_timestamp))

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
                                    arm_location=target_restorable_account.location)


def _convert_to_utc_timestamp(timestamp_string):
    import dateutil
    import datetime
    import dateutil.parser
    timestamp_datetime = dateutil.parser.parse(timestamp_string)
    timestamp_datetime_utc = None
    # Convert to utc only if timezone aware
    if timestamp_datetime.tzinfo is not None and timestamp_datetime.tzinfo.utcoffset(timestamp_datetime) is not None:
        timestamp_datetime_utc = timestamp_datetime.astimezone(datetime.timezone.utc)
    else:
        timestamp_datetime_utc = timestamp_datetime
    return timestamp_datetime_utc


def cli_cosmosdb_list(client, resource_group_name=None):
    """ Lists all Azure Cosmos DB database accounts within a given resource group or subscription. """
    if resource_group_name:
        return client.list_by_resource_group(resource_group_name)

    return client.list()
