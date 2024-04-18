
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    resource_group_name_type,
    get_location_type,
    get_three_state_flag
)

from azure.cli.core.commands.validators import (
    validate_file_or_dict
)

from azext_dataprotection.manual._validators import datetime_type, schedule_days_type, namespaced_name_resource_type
from azext_dataprotection.manual.enums import (
    get_protection_status_values,
    get_backup_frequency_values,
    get_datastore_type_values,
    get_duration_type_values,
    get_copy_option_values,
    get_retention_rule_name_values,
    get_absolute_criteria_values,
    get_days_of_week_values,
    get_weeks_of_month_values,
    get_months_of_year_values,
    get_tag_name_values,
    get_job_status_values,
    get_job_operation_values,
    get_datasource_types,
    get_rehydration_priority_values,
    get_secret_store_type_values,
    get_backup_operation_values,
    get_permission_scope_values,
    get_resource_type_values,
    get_persistent_volume_restore_mode_values,
    get_conflict_policy_values
)

vault_name_type = CLIArgumentType(help='Name of the backup vault.', options_list=['--vault-name', '-v'], type=str)


def load_arguments(self, _):

    with self.argument_context('dataprotection recovery-point list') as c:
        c.argument('backup_instance_name', type=str, help="Backup instance name.")
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type)
        c.argument('start_time', type=str, help="Specify the start date time in UTC (yyyy-mm-ddTHH:MM:SS)")
        c.argument('end_time', type=str, help="Specify the end date time in UTC (yyyy-mm-ddTHH:MM:SS)")
        c.argument('use_secondary_region', arg_type=get_three_state_flag(),
                   help='Use this flag to fetch recovery points from the secondary region')
        c.argument('max_items', type=int, help="Total number of items to return in the command's output. If the "
                                               "total number of items available is more than the value "
                                               "specified, a token is provided in the command's output. To "
                                               "resume pagination, provide the token value in `--next-token` "
                                               "argument of a subsequent command.")
        c.argument('next_token', type=str, help="Token to specify where to start paginating. This is the token "
                                                "value from a previously truncated response.")

    with self.argument_context('dataprotection backup-vault list-from-resourcegraph') as c:
        c.argument('subscriptions', type=str, nargs='+', help="List of subscription Ids.")
        c.argument('resource_groups', type=str, nargs='+', help="List of resource groups.")
        c.argument('vaults', type=str, nargs='+', help="List of vault names.")
        c.argument('vault_id', type=str, nargs='+', help="Specify vault id filter to apply.")

    with self.argument_context('dataprotection backup-instance validate-for-backup') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type, id_part='name')
        c.argument('backup_instance', type=validate_file_or_dict, help='Request body for operation Expected value: '
                   'json-string/@json-file.')

    with self.argument_context('dataprotection backup-instance initialize-backupconfig') as c:
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type of the resource to be backed up.")
        c.argument('excluded_resource_types', type=str, nargs='+', options_list=["--excluded-resource-types", "--excluded-resource-type"],
                   help="List of resource types to be excluded for backup.")
        c.argument('included_resource_types', type=str, nargs='+', options_list=["--included-resource-types", "--included-resource-type"],
                   help="List of resource types to be included for backup.")
        c.argument('excluded_namespaces', type=str, nargs='+', help="List of namespaces to be excluded for backup.")
        c.argument('included_namespaces', type=str, nargs='+', help="List of namespaces to be included for backup.")
        c.argument('label_selectors', type=str, nargs='+', help="List of labels for internal filtering for backup.")
        c.argument('snapshot_volumes', arg_type=get_three_state_flag(), help="Boolean parameter to decide whether snapshot volumes are included for backup. By default this is taken as true.")
        c.argument('include_cluster_scope_resources', arg_type=get_three_state_flag(),
                   options_list=['--include-cluster-scope-resources', '--include-cluster-scope'],
                   help="Boolean parameter to decide whether cluster scope resources are included for restore. By default this is taken as true.")
        c.argument('backup_hook_references',
                   type=namespaced_name_resource_type,
                   options_list=['--backup-hook-references', '--backup-hook-refs'],
                   help='Property sets the hook reference to be executed during backup.')

    with self.argument_context('dataprotection backup-instance initialize') as c:
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type of the resource to be backed up")
        c.argument('datasource_id', type=str, help="ARM Id of the resource to be backed up")
        c.argument('datasource_location', options_list=['--datasource-location', '-l'], arg_type=get_location_type(self.cli_ctx))
        c.argument('friendly_name', type=str, help="User-defined friendly name for the backup instance")
        c.argument('backup_configuration', type=validate_file_or_dict, help="Backup configuration for backup. Use this parameter to configure protection for AzureKubernetesService.")
        c.argument('policy_id', type=str, help="Id of the backup policy the datasource will be associated")
        c.argument('secret_store_type', arg_type=get_enum_type(get_secret_store_type_values()), help="Specify the secret store type to use for authentication")
        c.argument('secret_store_uri', type=str, help="specify the secret store uri to use for authentication")
        c.argument('snapshot_resource_group_name', options_list=['--snapshot-resource-group-name', '--snapshot-rg'], type=str, help="Name of the resource group in which the backup snapshots should be stored")
        c.argument('tags', tags_type)

    with self.argument_context('dataprotection backup-instance update-policy') as c:
        c.argument('backup_instance_name', type=str, help="Backup instance name.")
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type)
        c.argument('policy_id', type=str, help="specify the ID of the new policy with which backup instance will be associated with.")

    with self.argument_context('dataprotection backup-policy get-default-policy-template') as c:
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type of the resource to be backed up")

    with self.argument_context('dataprotection backup-instance list-from-resourcegraph') as c:
        c.argument('subscriptions', type=str, nargs='+', help="List of subscription Ids.")
        c.argument('resource_groups', type=str, nargs='+', help="List of resource groups.")
        c.argument('vaults', type=str, nargs='+', help="List of vault names.")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('subscriptions', type=str, nargs='+', help="List of subscription Ids.")
        c.argument('protection_status', arg_type=get_enum_type(get_protection_status_values()), nargs='+', help="specify protection status.")
        c.argument('datasource_id', type=str, nargs='+', help="specify datasource id filter to apply.")
        c.argument('backup_instance_id', type=str, nargs='+', help="specify backup instance id filter to apply.")
        c.argument('backup_instance_name', type=str, nargs='+', help="specify backup instance name filter to apply.")

    with self.argument_context('dataprotection backup-instance update-msi-permissions') as c:
        c.argument('operation', arg_type=get_enum_type(get_backup_operation_values()), help="List of possible operations")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type of the resource to be backed up")
        c.argument('vault_name', vault_name_type)
        c.argument('permissions_scope', arg_type=get_enum_type(get_permission_scope_values()), help="Scope for assigning permissions to the backup vault")
        c.argument('keyvault_id', type=str, help='ARM id of the key vault. Required when --datasource-type is AzureDatabaseForPostgreSQL')
        c.argument('yes', options_list=['--yes', '-y'], help='Do not prompt for confirmation.', action='store_true')
        c.argument('snapshot_resource_group_id', options_list=['--snapshot-resource-group-id', '--snapshot-rg-id'], type=str,
                   help='ARM id of the snapshot resource group. Required when assigning permissions over snapshot resource group and the --operation is Restore')
        c.argument('target_storage_account_id', options_list=['--target-storage-account-id'], type=str,
                   help='ARM id of the target storage account. Required when assigning permissions over target storage account and the --operation is Restore')
        c.argument('backup_instance', type=validate_file_or_dict, help='Request body for operation "Backup" Expected value: '
                   'json-string/@json-file. Required when --operation is Backup')
        c.argument('restore_request_object', type=validate_file_or_dict, help='Request body for operation "Restore" Expected value: '
                   'json-string/@json-file. Required when --operation is Restore')

    with self.argument_context('dataprotection job show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type, id_part='name')
        c.argument('job_id', type=str, help='The Job ID. This is a GUID-formatted string (e.g. 00000000-0000-0000-0000-000000000000).', id_part='child_name_1')
        c.argument('use_secondary_region', arg_type=get_three_state_flag(),
                   help='Use this flag fetch list of jobs from secondary region')

    with self.argument_context('dataprotection job list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type)
        c.argument('use_secondary_region', arg_type=get_three_state_flag(),
                   help='Use this flag fetch list of jobs from secondary region')
        c.argument('max_items', type=int, help="Total number of items to return in the command's output. If the "
                                               "total number of items available is more than the value "
                                               "specified, a token is provided in the command's output. To "
                                               "resume pagination, provide the token value in `--next-token` "
                                               "argument of a subsequent command.")
        c.argument('next_token', type=str, help="Token to specify where to start paginating. This is the token "
                                                "value from a previously truncated response.")

    with self.argument_context('dataprotection job list-from-resourcegraph') as c:
        c.argument('subscriptions', type=str, nargs='+', help="List of subscription Ids.")
        c.argument('resource_groups', type=str, nargs='+', help="List of resource groups.")
        c.argument('vaults', type=str, nargs='+', help="List of vault names.")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('subscriptions', type=str, nargs='+', help="List of subscription Ids.")
        c.argument('start_time', type=schedule_days_type, help="specify start time of the job in UTC (yyyy-mm-ddTHH:MM:SS).")
        c.argument('end_time', type=schedule_days_type, help="specify end time of the job in UTC (yyyy-mm-ddTHH:MM:SS).")
        c.argument('status', arg_type=get_enum_type(get_job_status_values()), nargs='+', help="specify job status values for filter.")
        c.argument('operation', arg_type=get_enum_type(get_job_operation_values()), nargs='+', help="specify job operation values for filter.")
        c.argument('datasource_id', type=str, nargs='+', help="specify datasource id filter to apply")

    with self.argument_context('dataprotection backup-policy trigger create-schedule') as c:
        c.argument('interval_type', arg_type=get_enum_type(get_backup_frequency_values()), help="Specify Backup Frequency.")
        c.argument('interval_count', type=int, help="Specify duration of backup frequency.")
        c.argument('schedule_days', type=schedule_days_type, nargs='+', help="specify the backup schedule time in UTC (yyyy-mm-ddTHH:MM:SS)")

    with self.argument_context('dataprotection backup-policy trigger set') as c:
        c.argument('policy', type=validate_file_or_dict, help="Existing policy Json string or file.")
        c.argument('schedule', type=str, nargs='+', help="Specify schedule time intervals for backup rule.")

    with self.argument_context('dataprotection backup-policy retention-rule create-lifecycle') as c:
        c.argument('source_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify source datastore.")
        c.argument('target_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify target datastore.")
        c.argument('retention_duration_type', options_list=['--retention-duration-type', '--type'], arg_type=get_enum_type(get_duration_type_values()), help="Retention duration type.")
        c.argument('retention_duration_count', options_list=['--retention-duration-count', '--count'], type=int, help="Retention duration count.")
        c.argument('copy_option', arg_type=get_enum_type(get_copy_option_values()), help="Specify copy option from source datastore to target datastore.")

    with self.argument_context('dataprotection backup-policy retention-rule set') as c:
        c.argument('name', arg_type=get_enum_type(get_retention_rule_name_values()), help="Specify the retention rule name to be edited in policy.")
        c.argument('policy', type=validate_file_or_dict, help="Policy Json string or file.")
        c.argument('lifecycles', type=validate_file_or_dict, nargs='+', help="lifecycles to be associated with the retention rule. Specify space separated json file names.")

    with self.argument_context('dataprotection backup-policy retention-rule remove') as c:
        c.argument('name', arg_type=get_enum_type(get_retention_rule_name_values()), help="Specify the retention rule name to be removed in policy.")
        c.argument('policy', type=validate_file_or_dict, help="Existing policy Json string or file.")

    with self.argument_context('dataprotection backup-policy tag create-absolute-criteria') as c:
        c.argument('absolute_criteria', arg_type=get_enum_type(get_absolute_criteria_values()), help="Specify retention criteria.")

    with self.argument_context('dataprotection backup-policy tag create-generic-criteria') as c:
        c.argument('days_of_week', nargs='+', arg_type=get_enum_type(get_days_of_week_values()), help="Specify days of week.")
        c.argument('weeks_of_month', nargs='+', arg_type=get_enum_type(get_weeks_of_month_values()), help="Specify weeks of month")
        c.argument('months_of_year', nargs='+', arg_type=get_enum_type(get_months_of_year_values()), help="Specify months of year.")
        c.argument('days_of_month', nargs='+', type=str, help="Specify days of month. Allowed values are 1 to 28 and Last")

    with self.argument_context('dataprotection backup-policy tag set') as c:
        c.argument('name', arg_type=get_enum_type(get_tag_name_values()), help="Specify the tag name to be edited in policy.")
        c.argument('policy', type=validate_file_or_dict, help="Policy Json string or file.")
        c.argument('criteria', type=validate_file_or_dict, nargs='+', help="crtierias to be associated with the tag. Specify space separated json file names.")

    with self.argument_context('dataprotection backup-policy tag remove') as c:
        c.argument('name', arg_type=get_enum_type(get_tag_name_values()), help="Specify the tag name to be removed in policy.")
        c.argument('policy', type=validate_file_or_dict, help="Existing policy Json string or file.")

    with self.argument_context('dataprotection backup-instance initialize-restoreconfig') as c:
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type of the resource to be backed up")
        c.argument('excluded_resource_types', type=str, nargs='+', options_list=["--excluded-resource-types", "--excluded-resource-type"],
                   help="List of resource types to be excluded for restore.")
        c.argument('included_resource_types', type=str, nargs='+', options_list=["--included-resource-types", "--included-resource-type"],
                   help="List of resource types to be included for restore.")
        c.argument('excluded_namespaces', type=str, nargs='+', help="List of namespaces to be excluded for restore.")
        c.argument('included_namespaces', type=str, nargs='+', help="List of namespaces to be included for restore.")
        c.argument('label_selectors', type=str, nargs='+', help="List of labels for internal filtering for restore.")
        c.argument("persistent_volume_restore_mode", arg_type=get_enum_type(get_persistent_volume_restore_mode_values()),
                   options_list=['--persistent-volume-restore-mode', '--persistent-restoremode'],
                   help="Restore mode for persistent volumes. Allowed values are RestoreWithVolumeData, RestoreWithoutVolumeData. Default value is RestoreWithVolumeData.")
        c.argument('conflict_policy', arg_type=get_enum_type(get_conflict_policy_values()), help="Conflict policy for restore. Allowed values are Skip, Patch. Default value is Skip.")
        c.argument('namespace_mappings', type=validate_file_or_dict, help="Namespaces mapping from source namespaces to target namespaces to resolve namespace naming conflicts in the target cluster.")
        c.argument('include_cluster_scope_resources', arg_type=get_three_state_flag(),
                   options_list=['--include-cluster-scope-resources', '--include-cluster-scope'],
                   help="Boolean parameter to decide whether cluster scope resources are included for restore. By default this is taken as true.")
        c.argument('restore_hook_references',
                   type=namespaced_name_resource_type,
                   options_list=['--restore-hook-references', '--restore-hook-refs'],
                   help='Property sets the hook reference to be executed during restore.')

    with self.argument_context('dataprotection backup-instance restore initialize-for-data-recovery') as c:
        c.argument('target_resource_id', type=str, help="specify the resource ID to which the data will be restored.")
        c.argument('backup_instance_id', type=str, help="specify the backup instance ID.")
        c.argument('recovery_point_id', type=str, help="specify the recovery point ID which will be used for restoring the data.")
        c.argument('point_in_time', type=datetime_type, help="specify the point in time which will be used for restoring the data in UTC (yyyy-mm-ddTHH:MM:SS)")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('source_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify the datastore type of the given recovery point or point in time.")
        c.argument('restore_location', type=str, help="Specify the restore location.")
        c.argument('secret_store_type', arg_type=get_enum_type(get_secret_store_type_values()), help="Specify the secret store type to use for authentication")
        c.argument('secret_store_uri', type=str, help="Specify the secret store uri to use for authentication")
        c.argument('rehydration_priority', arg_type=get_enum_type(get_rehydration_priority_values()), help="Specify the rehydration priority for rehydrate restore.")
        c.argument('rehydration_duration', type=int, help="Specify the rehydration duration for rehydrate restore.")
        c.argument('restore_configuration', type=validate_file_or_dict, help="Restore configuration for restore. Use this parameter to restore with AzureKubernetesService.")

    with self.argument_context('dataprotection backup-instance restore initialize-for-data-recovery-as-files') as c:
        c.argument('target_blob_container_url', type=str, help="specify the blob container url to which the data will be restored.")
        c.argument('target_file_name', type=str, help="specify the file name to which the data will be restored.")
        c.argument('target_resource_id', type=str, help="specify the target storage container ARM ID to which data will be restored, "
                   'required for restoring as files to another subscription')
        c.argument('recovery_point_id', type=str, help="specify the recovery point ID which will be used for restoring the data.")
        c.argument('point_in_time', type=datetime_type, help="specify the point in time which will be used for restoring the data in UTC (yyyy-mm-ddTHH:MM:SS)")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('source_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify the datastore type of the given recovery point or point in time.")
        c.argument('restore_location', type=str, help="specify the restore location.")
        c.argument('rehydration_priority', arg_type=get_enum_type(get_rehydration_priority_values()), help="Specify the rehydration priority for rehydrate restore.")
        c.argument('rehydration_duration', type=int, help="Specify the rehydration duration for rehydrate restore.")

    with self.argument_context('dataprotection backup-instance restore initialize-for-item-recovery') as c:
        c.argument('target_resource_id', type=str, help="specify the resource ID to which the data will be restored.")
        c.argument('restore_location', type=str, help="specify the restore location.")
        c.argument('recovery_point_id', type=str, help="specify the recovery point ID which will be used for restoring the data.")
        c.argument('point_in_time', type=datetime_type, help="specify the point in time which will be used for restoring the data in UTC (yyyy-mm-ddTHH:MM:SS).")
        c.argument('source_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify the datastore type of the given recovery point or point in time.")
        c.argument('backup_instance_id', type=str, help="specify the backup instance ID.")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('container_list', type=str, nargs='+', help="specify the list of containers to restore.")
        c.argument('from_prefix_pattern', type=str, nargs='+', help="specify the prefix pattern for start range.")
        c.argument('to_prefix_pattern', type=str, nargs='+', help="specify the prefix pattern for end range.")
        c.argument('restore_configuration', type=validate_file_or_dict, help="Restore configuration for restore. Use this parameter to restore with AzureKubernetesService.")

    with self.argument_context('dataprotection backup-instance validate-for-restore') as c:
        c.argument('backup_instance_name', options_list=['--backup-instance-name', '--name', '-n'], type=str, help="Backup instance name.")
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type, id_part='name')
        c.argument('restore_request_object', type=validate_file_or_dict, help='Request body for operation. Expected value: '
                   'json-string/@json-file.')
        c.argument('use_secondary_region', arg_type=get_three_state_flag(),
                   help='Use this flag to restore from a recoverypoint in secondary region.')

    with self.argument_context('dataprotection backup-instance restore trigger') as c:
        c.argument('backup_instance_name', options_list=['--backup-instance-name', '--name', '-n'], type=str, help="Backup instance name.")
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', vault_name_type, id_part='name')
        c.argument('restore_request_object', type=validate_file_or_dict, help='Request body for operation. Expected value: '
                   'json-string/@json-file.')
        c.argument('use_secondary_region', arg_type=get_three_state_flag(),
                   help='Use this flag to restore from a recoverypoint in secondary region.')

    with self.argument_context('dataprotection resource-guard list-protected-operations') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('resource_guard_name', options_list=['--resource-guard-name', '--name', '-n'], type=str, help='The name of '
                   'ResourceGuard', id_part='name')
        c.argument('resource_type', arg_type=get_enum_type(get_resource_type_values()), help='Type of the resource associated with the protected operations')
