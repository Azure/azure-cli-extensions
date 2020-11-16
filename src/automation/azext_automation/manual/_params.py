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
from azext_automation.action import (
    AddPropertiesParameters
)
from azext_automation.vendored_sdks.automation.models import SkuNameEnum, RunbookTypeEnum


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
