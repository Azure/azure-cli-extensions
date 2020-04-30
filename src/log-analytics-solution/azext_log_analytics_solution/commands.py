# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
from azure.cli.core.commands import CliCommandType
from ._client_factory import cf_solutions


def load_command_table(self, _):

    log_analytics_solution_solutions = CliCommandType(
        operations_tmpl='azext_log_analytics_solution.vendored_sdks.operationsmanagement.operations._solutions_operations#SolutionsOperations.{}',
        client_factory=cf_solutions)

    with self.command_group('monitor log-analytics solution', log_analytics_solution_solutions,
                            client_factory=cf_solutions, is_experimental=True) as g:
        g.custom_command('create', 'create_monitor_log_analytics_solution', supports_no_wait=True)
        g.custom_command('update', 'update_monitor_log_analytics_solution', supports_no_wait=True)
        g.custom_command('delete', 'delete_monitor_log_analytics_solution', supports_no_wait=True, confirmation=True)
        g.custom_show_command('show', 'get_monitor_log_analytics_solution')
        g.custom_command('list', 'list_monitor_log_analytics_solution')
