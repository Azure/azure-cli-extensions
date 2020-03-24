# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    from azext_operationsmanagement.generated._client_factory import cf_solution
    operationsmanagement_solution = CliCommandType(
        operations_tmpl='azext_operationsmanagement.vendored_sdks.operationsmanagement.operations._solution_operations#'
        'SolutionOperations.{}')
    with self.command_group('operationsmanagement solution', operationsmanagement_solution) as g:
        g.custom_command('list', 'operationsmanagement_solution_list')
        g.custom_show_command('show', 'operationsmanagement_solution_show')
        g.custom_command('create', 'operationsmanagement_solution_create', supports_no_wait=True)
        g.custom_command('update', 'operationsmanagement_solution_update', supports_no_wait=True)
        g.custom_command('delete', 'operationsmanagement_solution_delete', supports_no_wait=True)
        g.wait_command('wait')

    from azext_operationsmanagement.generated._client_factory import cf_management_association
    operationsmanagement_management_association = CliCommandType(
        operations_tmpl='azext_operationsmanagement.vendored_sdks.operationsmanagement.operations._management_associati'
        'on_operations#ManagementAssociationOperations.{}')
    with self.command_group('operationsmanagement management-association', operationsmanagement_management_association) as g:
        g.custom_command('list', 'operationsmanagement_management_association_list')
        g.custom_show_command('show', 'operationsmanagement_management_association_show')
        g.custom_command('create', 'operationsmanagement_management_association_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'operationsmanagement_management_association_delete')

    from azext_operationsmanagement.generated._client_factory import cf_management_configuration
    operationsmanagement_management_configuration = CliCommandType(
        operations_tmpl='azext_operationsmanagement.vendored_sdks.operationsmanagement.operations._management_configura'
        'tion_operations#ManagementConfigurationOperations.{}')
    with self.command_group('operationsmanagement management-configuration',
                            operationsmanagement_management_configuration) as g:
        g.custom_command('list', 'operationsmanagement_management_configuration_list')
        g.custom_show_command('show', 'operationsmanagement_management_configuration_show')
        g.custom_command('create', 'operationsmanagement_management_configuration_create')
        g.generic_update_command('update')
        g.custom_command('delete', 'operationsmanagement_management_configuration_delete')
