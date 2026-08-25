# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Command registration for the ``migrate runbook`` feature package."""

from azure.cli.core.commands import CliCommandType
from azext_migrate.runbook.transformers import (
    runbook_table,
    definition_table,
    execution_table,
    executions_table,
)


def load_runbook_command_table(self):
    runbook_cmds = CliCommandType(
        operations_tmpl='azext_migrate.runbook.cmds.{}')

    with self.command_group(
            'migrate runbook',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command(
            'generate', 'runbook#generate',
            supports_no_wait=True,
            table_transformer=runbook_table)
        g.custom_show_command(
            'show', 'runbook#show',
            table_transformer=runbook_table)
        g.custom_command(
            'list', 'runbook#list_',
            table_transformer=runbook_table)
        g.custom_command(
            'update', 'runbook#update',
            table_transformer=runbook_table)
        g.custom_command(
            'regenerate', 'runbook#regenerate',
            supports_no_wait=True,
            table_transformer=runbook_table)
        g.custom_command(
            'delete', 'runbook#delete',
            supports_no_wait=True,
            confirmation=True)
        g.custom_command('wait', 'runbook#wait')

    with self.command_group(
            'migrate runbook definition',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_show_command(
            'show', 'definition#show',
            table_transformer=definition_table)
        g.custom_command('download', 'definition#download')
        g.custom_command('visualize', 'definition#visualize')

    with self.command_group(
            'migrate runbook definition step',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command(
            'add', 'definition_step#add',
            table_transformer=definition_table)
        g.custom_command(
            'update', 'definition_step#update',
            table_transformer=definition_table)
        g.custom_command(
            'remove', 'definition_step#remove',
            confirmation=True)

    with self.command_group(
            'migrate runbook definition workstream',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command(
            'split', 'definition_workstream#split',
            table_transformer=definition_table)
        g.custom_command(
            'merge', 'definition_workstream#merge',
            table_transformer=definition_table)

    with self.command_group(
            'migrate runbook parameter',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command('download', 'parameter#download')
        g.custom_command('upload', 'parameter#upload')

    with self.command_group(
            'migrate runbook execution',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command(
            'start', 'execution#start',
            supports_no_wait=True)
        g.custom_show_command(
            'show', 'execution#show',
            table_transformer=execution_table)
        g.custom_command(
            'list', 'execution#list_',
            table_transformer=executions_table)
        g.custom_command('pause', 'execution#pause')
        g.custom_command('resume', 'execution#resume')
        g.custom_command(
            'cancel', 'execution#cancel',
            confirmation=True)
        g.custom_command('visualize', 'execution#visualize')

    with self.command_group(
            'migrate runbook execution parameter',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command('download', 'execution_parameter#download')
        g.custom_command('upload', 'execution_parameter#upload')

    with self.command_group(
            'migrate runbook execution step',
            custom_command_type=runbook_cmds,
            is_preview=True) as g:
        g.custom_command('retry', 'execution_step#retry')
        g.custom_command('approve', 'execution_step#approve')
        g.custom_command('complete', 'execution_step#complete')
