# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import unittest
from types import SimpleNamespace
from unittest import mock

from azext_cosmosdb_preview.tests.latest import (
    test_cosmosdb_sql_materializedview_scenario as materialized_view,
    test_cosmosdb_table_rbac_assignment_scenario as table_rbac,
)


class CosmosdbScenarioFixtureTest(unittest.TestCase):
    def test_materialized_view_uses_generated_account(self):
        scenario = SimpleNamespace(
            kwargs={'rg': 'test-resource-group'},
            create_random_name=mock.Mock(side_effect=['test-database', 'test-account']),
            cmd=mock.Mock(),
            check=mock.Mock(),
        )
        inspect.unwrap(materialized_view.Cosmosdb_previewMaterialiedviewScenarioTest.test_cosmosdb_materializedview)(
            scenario)

        self.assertEqual(scenario.kwargs['acc'], 'test-account')
        self.assertEqual(scenario.kwargs['db_name'], 'test-database')
        commands = [call.args[0].format(**scenario.kwargs) for call in scenario.cmd.call_args_list]
        self.assertIn('az cosmosdb create --disable-local-auth true -n test-account -g test-resource-group '
                      '--enable-materialized-views --backup-policy-type Continuous', commands)
        self.assertIn('az cosmosdb delete -n test-account -g test-resource-group --yes', commands)

    def test_table_rbac_uses_provisioned_identity_and_account_scope(self):
        scope = '/subscriptions/test-subscription/resourceGroups/test-group/providers/' \
                'Microsoft.DocumentDB/databaseAccounts/test-account'
        account = {'id': scope, 'identity': {'principalId': 'test-principal'}}
        assignments = iter([[], [{'name': 'test-assignment'}], []])
        commands = []
        scenario = SimpleNamespace(
            kwargs={'rg': 'test-group'},
            create_random_name=mock.Mock(side_effect=['test-account', 'test-table']),
            check=mock.Mock(),
        )

        def run_command(command, **kwargs):
            commands.append(command.format(**scenario.kwargs))
            if command.startswith('az cosmosdb create '):
                output = account
            elif command.startswith('az cosmosdb table role assignment list '):
                output = next(assignments)
            else:
                output = True
            return SimpleNamespace(get_output_in_json=lambda: output)

        scenario.cmd = mock.Mock(side_effect=run_command)
        inspect.unwrap(table_rbac.Cosmosdb_previewtableRbacAssignmentScenarioTest.test_cosmosdb_table_role_assignment)(
            scenario)

        self.assertIn('--assign-identity [system]', commands[0])
        self.assertEqual(scenario.kwargs['scope'], scope)
        self.assertEqual(scenario.kwargs['principal_id'], 'test-principal')
        for operation, role_suffix in (('create', '1'), ('update', '2')):
            command = next(command for command in commands
                           if command.startswith('az cosmosdb table role assignment ' + operation + ' '))
            self.assertIn('--scope ' + scope, command)
            self.assertIn('--principal-id test-principal', command)
            self.assertIn('--role-definition-id ' + scope +
                          '/tableRoleDefinitions/00000000-0000-0000-0000-00000000000' + role_suffix, command)
