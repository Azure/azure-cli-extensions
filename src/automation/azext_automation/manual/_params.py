# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements

from azure.cli.core.commands.parameters import (
    tags_type,
    get_three_state_flag,
    get_enum_type,
    resource_group_name_type,
    get_location_type
)
from azure.cli.core.commands.validators import get_default_location_from_resource_group
from azure.cli.core.commands.parameters import get_datetime_type
from azext_automation.action import (
    AddPropertiesParameters, validator_duration
)
from azext_automation.vendored_sdks.automation.models import SkuNameEnum, RunbookTypeEnum, OperatingSystemType


def load_arguments(self, _):

    with self.argument_context('automation account list') as c:
        c.argument('resource_group_name', resource_group_name_type)

    with self.argument_context('automation account show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', options_list=['--name', '-n', '--automation-account-name'], type=str,
                   help='The name of the automation account.', id_part='name')

    with self.argument_context('automation account delete') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', options_list=['--name', '-n', '--automation-account-name'], type=str,
                   help='The name of the automation account.', id_part='name')

    with self.argument_context('automation account create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', options_list=['--name', '-n', '--automation-account-name'],
                   help='The name of the automation account.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('sku', help='Account SKU.', arg_type=get_enum_type(SkuNameEnum))

    with self.argument_context('automation account update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', options_list=['--name', '-n', '--automation-account-name'],
                   help='The name of the automation account.', id_part='name')
        c.argument('tags', tags_type)
        c.argument('sku', help='Account SKU.', arg_type=get_enum_type(SkuNameEnum))

    with self.argument_context('automation runbook create') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.')
        c.argument('name', options_list=['--name', '-n', '--runbook-name'], type=str, help='The runbook name.')
        c.argument('location', arg_type=get_location_type(self.cli_ctx),
                   validator=get_default_location_from_resource_group)
        c.argument('tags', tags_type)
        c.argument('runbook_type', options_list=['--type'], help='Type of the runbook.',
                   arg_type=get_enum_type(RunbookTypeEnum))
        c.argument('description', type=str, help='Description of the runbook.')
        c.argument('log_verbose', arg_type=get_three_state_flag(), help='Verbose log option of the runbook.')
        c.argument('log_progress', arg_type=get_three_state_flag(), help='Progress log option of the runbook.')
        c.argument('log_activity_trace', type=int, help='Activity level tracing options of the runbook.')

    with self.argument_context('automation runbook update') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('name', options_list=['--name', '-n', '--runbook-name'], type=str, help='The runbook name.',
                   id_part='child_name_1')
        c.argument('tags', tags_type)
        c.argument('description', type=str, help='Description of the runbook.')
        c.argument('log_verbose', arg_type=get_three_state_flag(), help='Verbose log option of the runbook.')
        c.argument('log_progress', arg_type=get_three_state_flag(), help='Progress log option of the runbook.')
        c.argument('log_activity_trace', type=int, help='Activity level tracing options of the runbook.')

    with self.argument_context('automation runbook replace-content') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('name', options_list=['--name', '-n', '--runbook-name'], help='The runbook name.',
                   id_part='child_name_1')
        c.argument('content', help='The runbook content.')

    with self.argument_context('automation runbook revert-to-published') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('name', options_list=['--name', '-n', '--runbook-name'], help='The runbook name.',
                   id_part='child_name_1')

    with self.argument_context('automation runbook start') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('name', options_list=['--name', '-n', '--runbook-name'], type=str, help='The runbook name.',
                   id_part='child_name_1')
        c.argument('properties_parameters', options_list=['--parameters'], action=AddPropertiesParameters, nargs='*',
                   help='Parameters of the job. Expect value: KEY1=VALUE1 KEY2=VALUE2 ...')
        c.argument('run_on', type=str, help='RunOn which specifies the group name where the job is to be executed.')

    with self.argument_context('automation job list') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.')

    with self.argument_context('automation job show') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('job_name', options_list=['--name', '-n', '--job-name'], type=str, help='The job name.',
                   id_part='child_name_1')

    # with self.argument_context('automation job get-output') as c:
    #     c.argument('resource_group_name', resource_group_name_type)
    #     c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
    #     c.argument('job_name', options_list=['--name', '-n', '--job-name'], type=str, help='The job name.',
    #                id_part='child_name_1')

    with self.argument_context('automation job resume') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('job_name', options_list=['--name', '-n', '--job-name'], type=str, help='The job name.',
                   id_part='child_name_1')

    with self.argument_context('automation job stop') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('job_name', options_list=['--name', '-n', '--job-name'], type=str, help='The job name.',
                   id_part='child_name_1')

    with self.argument_context('automation job suspend') as c:
        c.argument('resource_group_name', resource_group_name_type)
        c.argument('automation_account_name', type=str, help='The name of the automation account.', id_part='name')
        c.argument('job_name', options_list=['--name', '-n', '--job-name'], type=str, help='The job name.',
                   id_part='child_name_1')

    with self.argument_context('automation schedule') as c:
        c.argument('automation_account_name', help='The name of the automation account.')
        c.argument('schedule_name', options_list=['--name', '-n', '--schedule-name'], help='The schedule name.')

    with self.argument_context('automation schedule create') as c:
        c.argument('description', help='The description of the schedule.')
        c.argument('start_time', arg_type=get_datetime_type(help='The start time of the schedule.'))
        c.argument('expiry_time', arg_type=get_datetime_type(help='The end time of the schedule.'))
        c.argument('interval', type=int, help='The interval of the schedule.')
        c.argument('frequency', help='The frequency of the schedule.')
        c.argument('time_zone', help='The time zone of the schedule.')

    with self.argument_context('automation schedule update') as c:
        c.argument('description', help='The description of the schedule.')
        c.argument('is_enabled', arg_type=get_three_state_flag(), help='Indicate whether this schedule is enabled.')

    with self.argument_context('automation schedule list') as c:
        c.argument('automation_account_name', help='The name of the automation account.', id_part=None)

    with self.argument_context('automation software-update-configuration') as c:
        c.argument('automation_account_name', help='The name of the automation account.')
        c.argument('software_update_configuration_name', options_list=['--name', '-n', '--configuration-name'],
                   help='The name of the software update configuration.')

    with self.argument_context('automation software-update-configuration create') as c:
        c.argument('operating_system', arg_type=get_enum_type(OperatingSystemType),
                   help='Operating system of target machines.')
        c.argument('included_update_classifications',
                   help='Update classification included in the software update configuration.'
                        ' A comma separated string with required values.')
        c.argument('excluded_kb_numbers', nargs='+',
                   help='Space-separated list of KB numbers excluded from the software update configuration.')
        c.argument('included_kb_numbers', nargs='+',
                   help='Space-separated list of KB numbers included from the software update configuration.')
        c.argument('reboot_setting', help='Reboot setting for the software update configuration.')
        c.argument('duration', validator=validator_duration,
                   help='Maximum time allowed for the software update configuration run.'
                        ' Duration needs to be specified using the format PT[n]H[n]M[n]S as per ISO8601.')
        c.argument('azure_virtual_machines', nargs='+',
                   help='Space-separated list of azure resource Ids for azure virtual machines targeted'
                        ' by the software update configuration.')
        c.argument('non_azure_computer_names', nargs='+',
                   help='Space-separated list of names of non-azure machines targeted'
                        ' by the software update configuration.')
        c.argument('azure_queries_scope', nargs='+',
                   help='Space-separated list of Azure queries scope in the software update configuration.')
        c.argument('azure_queries_locations', nargs='+',
                   help='Space-separated list of Azure queries location in the software update configuration.')
        c.argument('azure_queries_tags', nargs='+',
                   help='Space-separated list of Azure queries tag settings in the software update configuration.')
        c.argument('non_azure_queries_function_alias', help='Log Analytics Saved Search name.')
        c.argument('non_azure_queries_workspace_id', help='Workspace Id for Log Analytics.')
        c.argument('start_time', arg_type=get_datetime_type(help='The start time of the schedule.'))
        c.argument('expiry_time', arg_type=get_datetime_type(help='The end time of the schedule.'))
        c.argument('expiry_time_offset_minutes', type=float, help="the expiry time's offset in minutes")
        c.argument('is_enabled', arg_type=get_three_state_flag(), help='Indicating whether this schedule is enabled.')
        c.argument('next_run', arg_type=get_datetime_type(help='The next run time of the schedule.'))
        c.argument('next_run_offset_minutes', type=float, help="The next run time's offset in minutes.")
        c.argument('interval', type=int, help='The interval of the schedule.')
        c.argument('frequency', help='The frequency of the schedule.')
        c.argument('time_zone', help='The time zone of the schedule.')
        c.argument('creation_time', arg_type=get_datetime_type(help='The creation time.'))
        c.argument('last_modified_time', arg_type=get_datetime_type(help='The last modified time.'))
        c.argument('description', help='The description of the schedule.')
        c.argument('pre_task_status', help='The status of the task.')
        c.argument('pre_task_source', help='The name of the source of the task.')
        c.argument('pre_task_job_id', help='The job id of the task.')
        c.argument('post_task_status', help='The status of the task.')
        c.argument('post_task_source', help='The name of the source of the task.')
        c.argument('post_task_job_id', help='The job id of the task.')

    with self.argument_context('automation software-update-configuration runs') as c:
        c.argument('automation_account_name', help='The name of the automation account.')

    with self.argument_context('automation software-update-configuration runs show') as c:
        c.argument('software_update_configuration_run_id', help='The Id of the software update configuration run.')

    with self.argument_context('automation software-update-configuration machine-runs') as c:
        c.argument('automation_account_name', help='The name of the automation account.')

    with self.argument_context('automation software-update-configuration machine-runs') as c:
        c.argument('software_update_configuration_machine_run_id',
                   help='The Id of the software update configuration machine run.')
