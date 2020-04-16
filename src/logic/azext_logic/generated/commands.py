# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType


def load_command_table(self, _):

    with self.command_group('logic', is_experimental=True):
        pass

    from azext_logic.generated._client_factory import cf_workflow
    logic_workflow = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._workflow_operations#WorkflowOperations.{}',
        client_factory=cf_workflow)
    with self.command_group('logic workflow', logic_workflow, client_factory=cf_workflow) as g:
        g.custom_command('list', 'logic_workflow_list')
        g.custom_show_command('show', 'logic_workflow_show')
        g.custom_command('create', 'logic_workflow_create')
        g.custom_command('update', 'logic_workflow_update')
        g.custom_command('delete', 'logic_workflow_delete', confirmation=True)

    from azext_logic.generated._client_factory import cf_integration_account
    logic_integration_account = CliCommandType(
        operations_tmpl='azext_logic.vendored_sdks.logic.operations._integration_account_operations#IntegrationAccountO'
        'perations.{}',
        client_factory=cf_integration_account)
    with self.command_group('logic integration-account', logic_integration_account,
                            client_factory=cf_integration_account) as g:
        g.custom_command('list', 'logic_integration_account_list')
        g.custom_show_command('show', 'logic_integration_account_show')
        g.custom_command('create', 'logic_integration_account_create')
        g.custom_command('update', 'logic_integration_account_update')
        g.custom_command(
            'delete', 'logic_integration_account_delete', confirmation=True)
        g.custom_command('import', 'logic_integration_account_import')
