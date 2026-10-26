# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from ._connection import connection_list_table_format, connection_show_table_format
from ._managed_connection import acl_list_table_format, acl_show_table_format
from ._workflow_discovery import workflow_list_table_format, workflow_show_table_format
from ._run_execution import execution_table_format
from ._runtime_doctor import doctor_table_format
from ._context import context_list_table_format, context_show_table_format
from ._test_report import table_format as test_table_format


def load_command_table(self, _):
    with self.command_group('logicapp test') as g:
        g.custom_command('create', 'test_create')
        g.custom_command('plan', 'test_plan', table_transformer=test_table_format)
        g.custom_command('run', 'test_run', table_transformer=test_table_format)

    with self.command_group('logicapp test results') as g:
        g.custom_show_command('show', 'test_results_show', table_transformer=test_table_format)

    with self.command_group('logicapp context') as g:
        g.custom_command('create', 'context_create')
        g.custom_command('use', 'context_use')
        g.custom_command('list', 'context_list', table_transformer=context_list_table_format)
        g.custom_show_command('show', 'context_show', table_transformer=context_show_table_format)
        g.custom_command('update', 'context_update', confirmation=False)
        g.custom_command('delete', 'context_delete', confirmation=False)

    with self.command_group('logicapp project') as g:
        g.custom_command('create', 'project_create')

    with self.command_group('logicapp workflow') as g:
        g.custom_command('create', 'workflow_create')
        g.custom_command('validate', 'workflow_validate')
        g.custom_command('list', 'workflow_list', table_transformer=workflow_list_table_format)
        g.custom_show_command('show', 'workflow_show', table_transformer=workflow_show_table_format)
        g.custom_command('export', 'workflow_export')
        g.custom_command('set', 'workflow_set', confirmation=False)
        g.custom_command('delete', 'workflow_delete', confirmation=False)
        g.custom_command('enable', 'workflow_enable', confirmation=False)
        g.custom_command('disable', 'workflow_disable', confirmation=False)

    with self.command_group('logicapp connection') as g:
        g.custom_command('create', 'connection_create')
        g.custom_command('list', 'connection_list', table_transformer=connection_list_table_format)
        g.custom_show_command('show', 'connection_show', table_transformer=connection_show_table_format)
        g.custom_command('test', 'connection_test')
        g.custom_command('delete', 'connection_delete', confirmation=False)

    with self.command_group('logicapp connection managed') as g:
        g.custom_command('create', 'connection_managed_create')

    with self.command_group('logicapp deployment') as g:
        g.custom_command('package', 'deployment_package')

    with self.command_group('logicapp dependency') as g:
        g.custom_command('check', 'dependency_check')
        g.custom_command('install', 'dependency_install')
        g.custom_command('uninstall', 'dependency_uninstall')

    with self.command_group('logicapp connection acl') as g:
        g.custom_command('list', 'connection_acl_list', table_transformer=acl_list_table_format)
        g.custom_show_command('show', 'connection_acl_show', table_transformer=acl_show_table_format)
        g.custom_command('add', 'connection_acl_add', table_transformer=acl_show_table_format)
        g.custom_command('remove', 'connection_acl_remove', confirmation=False)

    with self.command_group('logicapp connector') as g:
        g.custom_command('list', 'connector_list')
        g.custom_show_command('show', 'connector_show')

    with self.command_group('logicapp connector operation') as g:
        g.custom_command('list', 'connector_operation_list')
        g.custom_show_command('show', 'connector_operation_show')

    with self.command_group('logicapp connector managed') as g:
        g.custom_command('list', 'connector_managed_list')
        g.custom_show_command('show', 'connector_managed_show')

    with self.command_group('logicapp connector managed operation') as g:
        g.custom_command('list', 'connector_managed_operation_list')
        g.custom_show_command('show', 'connector_managed_operation_show')

    with self.command_group('logicapp runtime') as g:
        g.custom_command('doctor', 'runtime_doctor', table_transformer=doctor_table_format)
        g.custom_command('start', 'runtime_start')
        g.custom_show_command('show', 'runtime_show')
        g.custom_command('stop', 'runtime_stop')

    with self.command_group('logicapp run') as g:
        g.custom_command('start', 'run_start')
        g.custom_show_command('show', 'run_show')
        g.custom_command('list', 'run_list')
        g.custom_command('wait', 'run_wait', table_transformer=execution_table_format)
        g.custom_command('cancel', 'run_cancel', confirmation=False, table_transformer=execution_table_format)
        g.custom_command('resubmit', 'run_resubmit', confirmation=False, table_transformer=execution_table_format)

    with self.command_group('logicapp trigger history') as g:
        g.custom_command('resubmit', 'trigger_history_resubmit', confirmation=False, table_transformer=execution_table_format)

    with self.command_group('logicapp run action') as g:
        g.custom_command('list', 'run_action_list')
        g.custom_show_command('show', 'run_action_show')
        g.custom_command('show-content', 'run_action_show_content')

    with self.command_group('logicapp identity') as g:
        g.custom_command('assign', 'identity_assign')
        g.custom_show_command('show', 'identity_show')
        g.custom_command('remove', 'identity_remove')
