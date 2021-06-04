
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import (
    validate_file_or_dict
)

from azext_dataprotection.manual._validators import datetime_type, schedule_days_type
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
    get_datasource_types
)


def load_arguments(self, _):
    with self.argument_context('dataprotection backup-instance create') as c:
        c.argument('backup_instance', type=validate_file_or_dict, help='Request body for operation Expected value: '
                   'json-string/@json-file.')

    with self.argument_context('dataprotection backup-instance validate-for-backup') as c:
        c.argument('backup_instance', type=validate_file_or_dict, help='Request body for operation Expected value: '
                   'json-string/@json-file.')

    with self.argument_context('dataprotection backup-instance initialize') as c:
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type of the resource to be backed up")
        c.argument('datasource_id', type=str, help="ARM Id of the resource to be backed up")
        c.argument('datasource_location', options_list=['--datasource-location', '-l'], arg_type=get_location_type(self.cli_ctx))
        c.argument('policy_id', type=str, help="Id of the backup policy the datasource will be associated")

    with self.argument_context('dataprotection backup-instance update-policy') as c:
        c.argument('backup_instance_name', type=str, help="Backup instance name.")
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('vault_name', type=str, help="Name of the vault.")
        c.argument('policy_id', type=str, help="specify the ID of the new policy with which backup instance will be associated with.")

    with self.argument_context('dataprotection recovery-point list') as c:
        c.argument('start_time', type=datetime_type, help="specify the start date in UTC (yyyy-mm-ddTHH:MM:SS)")
        c.argument('end_time', type=datetime_type, help="specify the end date in UTC (yyyy-mm-ddTHH:MM:SS)")

    with self.argument_context('dataprotection backup-policy create') as c:
        c.argument('policy', type=validate_file_or_dict, help='Request body for operation Expected value: '
                   'json-string/@json-file.')

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

    with self.argument_context('dataprotection backup-instance restore initialize-for-data-recovery') as c:
        c.argument('target_resource_id', type=str, help="specify the resource ID to which the data will be restored.")
        c.argument('recovery_point_id', type=str, help="specify the recovery point ID which will be used for restoring the data.")
        c.argument('point_in_time', type=datetime_type, help="specify the point in time which will be used for restoring the data in UTC (yyyy-mm-ddTHH:MM:SS)")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('source_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify the datastore type of the given recovery point or point in time.")
        c.argument('restore_location', type=str, help="specify the restore location.")

    with self.argument_context('dataprotection backup-instance restore initialize-for-item-recovery') as c:
        c.argument('restore_location', type=str, help="specify the restore location.")
        c.argument('recovery_point_id', type=str, help="specify the recovery point ID which will be used for restoring the data.")
        c.argument('point_in_time', type=datetime_type, help="specify the point in time which will be used for restoring the data in UTC (yyyy-mm-ddTHH:MM:SS).")
        c.argument('source_datastore', arg_type=get_enum_type(get_datastore_type_values()), help="Specify the datastore type of the given recovery point or point in time.")
        c.argument('backup_instance_id', type=str, help="specify the backup instance ID.")
        c.argument('datasource_type', arg_type=get_enum_type(get_datasource_types()), help="Specify the datasource type")
        c.argument('container_list', type=str, nargs='+', help="specify the list of containers to restore.")
        c.argument('from_prefix_pattern', type=str, nargs='+', help="specify the prefix pattern for start range.")
        c.argument('to_prefix_pattern', type=str, nargs='+', help="specify the prefix pattern for end range.")

    with self.argument_context('dataprotection backup-vault list') as c:
        c.argument('resource_group_name', resource_group_name_type)
