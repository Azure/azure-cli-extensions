# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType

from azext_dms._client_factory import (dms_client_factory,
                                       dms_cf_projects,
                                       dms_cf_tasks,
                                       dms_cf_service_tasks)


def load_command_table(self, _):
    dms_projects_sdk = CliCommandType(
        operations_tmpl='azext_dms.vendored_sdks.datamigration.operations._projects_operations#ProjectsOperations.{}',
        client_factory=dms_client_factory
    )

    dms_tasks_sdk = CliCommandType(
        operations_tmpl='azext_dms.vendored_sdks.datamigration.operations._tasks_operations#TasksOperations.{}',
        client_factory=dms_client_factory
    )

    dms_service_tasks_sdk = CliCommandType(
        operations_tmpl='azext_dms.vendored_sdks.datamigration.operations._service_tasks_operations#ServiceTasksOperations.{}',  # pylint: disable=line-too-long
        client_factory=dms_client_factory
    )

    with self.command_group('dms project', dms_projects_sdk, client_factory=dms_cf_projects) as g:
        g.custom_command('create', 'create_or_update_project')

    with self.command_group('dms project task', dms_tasks_sdk, client_factory=dms_cf_tasks) as g:
        g.custom_command('cancel', 'stop_task')
        g.custom_command('create', 'create_task')
        g.custom_command('cutover', 'cutover_sync_task')
        g.custom_command('restart', 'restart_task')
        g.custom_command('stop', 'stop_task')

    with self.command_group('dms task', dms_service_tasks_sdk, client_factory=dms_cf_service_tasks) as g:
        g.custom_command('create', 'create_service_task')
        g.command('delete', 'delete', confirmation=True)
        g.command('list', 'list')
        g.show_command('show', 'get')
        g.command('cancel', 'cancel')
