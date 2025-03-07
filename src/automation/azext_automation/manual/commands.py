# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_automation.manual._client_factory import cf_runbook_draft, cf_job, cf_automation_account, \
        cf_schedule, cf_software_update_configuration, cf_software_update_configuration_runs, \
        cf_software_update_configuration_machine_runs
    from azext_automation.generated._client_factory import cf_runbook

    automation_runbook_draft = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations._runbook_draft_operations#RunbookDraftOpe'
        'rations.{}',
        client_factory=cf_runbook_draft)

    automation_runbook = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations._runbook_operations#RunbookOperations.{}',
        client_factory=cf_runbook)

    automation_job = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations._job_operations#JobOperations.{}',
        client_factory=cf_job)

    automation_schedule = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations.'
                        '_schedule_operations#ScheduleOperations.{}',
        client_factory=cf_schedule)

    automation_software_update_configuration = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations.'
                        '_software_update_configuration_operations#SoftwareUpdateConfigurationMachineRunsOperations.{}',
        client_factory=cf_software_update_configuration)

    automation_software_update_configuration_runs = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations.'
                        '_software_update_configuration_runs_operations#'
                        'SoftwareUpdateConfigurationMachineRunsOperations.{}',
        client_factory=cf_software_update_configuration_runs)

    automation_software_update_configuration_machine_runs = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations.'
                        '_software_update_configuration_machine_runs_operations#'
                        'SoftwareUpdateConfigurationMachineRunsOperations.{}',
        client_factory=cf_software_update_configuration_machine_runs)

    with self.command_group('automation runbook', automation_runbook_draft, client_factory=cf_runbook_draft,
                            is_experimental=True) as g:
        g.custom_command('replace-content', 'automation_runbook_draft_replace_content', supports_no_wait=True)
        g.custom_command('revert-to-published', 'automation_runbook_draft_undo_edit')

    with self.command_group('automation runbook', automation_job, client_factory=cf_job, is_experimental=True) as g:
        g.custom_command('start', 'automation_runbook_start')

    with self.command_group('automation runbook', automation_runbook, client_factory=cf_runbook,
                            is_experimental=True) as g:
        g.custom_command('create', 'automation_runbook_create')

    with self.command_group('automation job', automation_job, client_factory=cf_job, is_experimental=True) as g:
        g.custom_command('list', 'automation_job_list')
        g.custom_show_command('show', 'automation_job_show')
        # g.custom_command('get-output', 'automation_job_get_output')
        g.custom_command('resume', 'automation_job_resume')
        g.custom_command('stop', 'automation_job_stop')
        g.custom_command('suspend', 'automation_job_suspend')

    automation_automation_account = CliCommandType(
        operations_tmpl='azext_automation.vendored_sdks.automation.operations._automation_account_operations#Automation'
                        'AccountOperations.{}',
        client_factory=cf_automation_account)
    with self.command_group('automation account', automation_automation_account,
                            client_factory=cf_automation_account, is_experimental=True) as g:
        g.custom_command('list', 'automation_account_list')
        g.custom_show_command('show', 'automation_account_show')
        g.custom_command('create', 'automation_account_create')
        g.custom_command('update', 'automation_account_update')
        g.custom_command('delete', 'automation_account_delete', confirmation=True)

    with self.command_group('automation schedule', automation_schedule,
                            client_factory=cf_schedule) as g:
        g.custom_command('list', 'automation_schedule_list')
        g.custom_show_command('show', 'automation_schedule_show')
        g.custom_command('create', 'automation_schedule_create')
        g.custom_command('update', 'automation_schedule_update')
        g.custom_command('delete', 'automation_schedule_delete', confirmation=True)

    with self.command_group('automation software-update-configuration', automation_software_update_configuration,
                            client_factory=cf_software_update_configuration) as g:
        g.custom_command('list', 'automation_software_update_configuration_list')
        g.custom_show_command('show', 'automation_software_update_configuration_show')
        g.custom_command('create', 'automation_software_update_configuration_create')
        g.custom_command('delete', 'automation_software_update_configuration_delete', confirmation=True)

    with self.command_group('automation software-update-configuration runs',
                            automation_software_update_configuration_runs,
                            client_factory=cf_software_update_configuration_runs) as g:
        g.custom_command('list', 'automation_software_update_configuration_runs_list')
        g.custom_show_command('show', 'automation_software_update_configuration_runs_show')

    with self.command_group('automation software-update-configuration machine-runs',
                            automation_software_update_configuration_machine_runs,
                            client_factory=cf_software_update_configuration_machine_runs) as g:
        g.custom_command('list', 'automation_software_update_configuration_machine_runs_list')
        g.custom_show_command('show', 'automation_software_update_configuration_machine_runs_show')
