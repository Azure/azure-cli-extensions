# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from collections import OrderedDict


class TestProject(unittest.TestCase):
    """Tests for the _project helper."""

    def test_project_returns_ordered_dict(self):
        from azext_chaos._table_format import _project
        result = {'name': 'test', 'location': 'westus2'}
        projected = _project(result, '{Name: name, Location: location}')
        self.assertIsInstance(projected, OrderedDict)
        self.assertEqual(projected['Name'], 'test')
        self.assertEqual(projected['Location'], 'westus2')

    def test_project_missing_keys_return_none(self):
        from azext_chaos._table_format import _project
        result = {'name': 'test'}
        projected = _project(result, '{Name: name, Missing: missing_key}')
        self.assertEqual(projected['Name'], 'test')
        self.assertIsNone(projected['Missing'])


class TestWorkspaceTableFormat(unittest.TestCase):

    def test_workspace_show_table_format(self):
        from azext_chaos._table_format import workspace_show_table_format
        result = {
            'id': '/subscriptions/00000000-0000-0000-0000-000000000000'
                  '/resourceGroups/MyRG/providers/Microsoft.Chaos'
                  '/workspaces/MyWorkspace',
            'name': 'MyWorkspace',
            'location': 'westus2',
            'properties': {'provisioningState': 'Succeeded'},
            'identity': {'type': 'SystemAssigned'},
        }
        table = workspace_show_table_format(result)
        self.assertEqual(table['Name'], 'MyWorkspace')
        self.assertEqual(table['ResourceGroup'], 'MyRG')
        self.assertEqual(table['Location'], 'westus2')
        self.assertEqual(table['ProvisioningState'], 'Succeeded')
        self.assertEqual(table['IdentityType'], 'SystemAssigned')

    def test_workspace_show_table_format_no_id(self):
        from azext_chaos._table_format import workspace_show_table_format
        result = {
            'name': 'MyWorkspace',
            'location': 'westus2',
            'properties': {'provisioningState': 'Succeeded'},
        }
        table = workspace_show_table_format(result)
        self.assertEqual(table['ResourceGroup'], '')

    def test_workspace_list_table_format(self):
        from azext_chaos._table_format import workspace_list_table_format
        results = [
            {
                'id': '/subscriptions/sub1/resourceGroups/RG1'
                      '/providers/Microsoft.Chaos/workspaces/ws1',
                'name': 'ws1',
                'location': 'westus2',
                'properties': {'provisioningState': 'Succeeded'},
                'identity': {'type': 'SystemAssigned'},
            },
            {
                'id': '/subscriptions/sub1/resourceGroups/RG2'
                      '/providers/Microsoft.Chaos/workspaces/ws2',
                'name': 'ws2',
                'location': 'eastus',
                'properties': {'provisioningState': 'Creating'},
                'identity': {'type': 'UserAssigned'},
            },
        ]
        tables = workspace_list_table_format(results)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]['Name'], 'ws1')
        self.assertEqual(tables[1]['ResourceGroup'], 'RG2')

    def test_workspace_show_table_format_no_mutation(self):
        """workspace_show_table_format must not inject keys into the input dict."""
        from azext_chaos._table_format import workspace_show_table_format
        result = {
            'id': '/subscriptions/00000000-0000-0000-0000-000000000000'
                  '/resourceGroups/MyRG/providers/Microsoft.Chaos'
                  '/workspaces/MyWorkspace',
            'name': 'MyWorkspace',
            'location': 'westus2',
            'properties': {'provisioningState': 'Succeeded'},
            'identity': {'type': 'SystemAssigned'},
        }
        original_keys = set(result.keys())
        workspace_show_table_format(result)
        self.assertEqual(set(result.keys()), original_keys)


class TestScenarioTableFormat(unittest.TestCase):

    def test_scenario_show_table_format(self):
        from azext_chaos._table_format import scenario_show_table_format
        result = {
            'name': 'ZoneDown-1.0',
            'properties': {
                'version': '1.0',
                'description': 'Zone failure simulation',
                'recommendation': {
                    'recommendationStatus': 'Recommended',
                },
            },
        }
        table = scenario_show_table_format(result)
        self.assertEqual(table['Name'], 'ZoneDown-1.0')
        self.assertEqual(table['Version'], '1.0')
        self.assertEqual(table['Description'], 'Zone failure simulation')
        self.assertEqual(table['Recommendation'], 'Recommended')

    def test_scenario_list_table_format(self):
        from azext_chaos._table_format import scenario_list_table_format
        results = [
            {'name': 's1', 'properties': {
                'version': '1.0', 'description': 'd1',
                'recommendation': {'recommendationStatus': 'R'},
            }},
        ]
        tables = scenario_list_table_format(results)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]['Name'], 's1')


class TestScenarioConfigTableFormat(unittest.TestCase):

    def test_scenario_config_show_extracts_scenario_name(self):
        """Scenario config table must show short scenario name, not full ARM ID."""
        from azext_chaos._table_format import scenario_config_show_table_format
        result = {
            'name': 'zone1',
            'properties': {
                'scenarioId': (
                    '/subscriptions/00000000-0000-0000-0000-000000000000'
                    '/resourceGroups/MyRG/providers/Microsoft.Chaos'
                    '/workspaces/MyWorkspace/scenarios/ZoneDown-1.0'
                ),
                'provisioningState': 'Succeeded',
            },
        }
        table = scenario_config_show_table_format(result)
        self.assertEqual(table['Name'], 'zone1')
        self.assertEqual(table['Scenario'], 'ZoneDown-1.0')
        self.assertEqual(table['ProvisioningState'], 'Succeeded')

    def test_scenario_config_show_empty_scenario_id(self):
        from azext_chaos._table_format import scenario_config_show_table_format
        result = {
            'name': 'zone1',
            'properties': {
                'scenarioId': '',
                'provisioningState': 'Creating',
            },
        }
        table = scenario_config_show_table_format(result)
        self.assertEqual(table['Scenario'], '')

    def test_scenario_config_show_missing_properties(self):
        from azext_chaos._table_format import scenario_config_show_table_format
        result = {'name': 'zone1'}
        table = scenario_config_show_table_format(result)
        self.assertEqual(table['Scenario'], '')

    def test_scenario_config_show_no_mutation(self):
        """scenario_config_show_table_format must not inject keys into the input dict."""
        from azext_chaos._table_format import scenario_config_show_table_format
        result = {
            'name': 'zone1',
            'properties': {
                'scenarioId': (
                    '/subscriptions/00000000-0000-0000-0000-000000000000'
                    '/resourceGroups/MyRG/providers/Microsoft.Chaos'
                    '/workspaces/MyWorkspace/scenarios/ZoneDown-1.0'
                ),
                'provisioningState': 'Succeeded',
            },
        }
        original_keys = set(result.keys())
        scenario_config_show_table_format(result)
        self.assertEqual(set(result.keys()), original_keys)

    def test_scenario_config_list_table_format(self):
        from azext_chaos._table_format import scenario_config_list_table_format
        results = [
            {
                'name': 'cfg1',
                'properties': {
                    'scenarioId': '/subscriptions/sub/resourceGroups/rg'
                                  '/providers/Microsoft.Chaos'
                                  '/workspaces/ws/scenarios/S1',
                    'provisioningState': 'Succeeded',
                },
            },
            {
                'name': 'cfg2',
                'properties': {
                    'scenarioId': '/subscriptions/sub/resourceGroups/rg'
                                  '/providers/Microsoft.Chaos'
                                  '/workspaces/ws/scenarios/S2',
                    'provisioningState': 'Failed',
                },
            },
        ]
        tables = scenario_config_list_table_format(results)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]['Scenario'], 'S1')
        self.assertEqual(tables[1]['Scenario'], 'S2')


class TestScenarioRunTableFormat(unittest.TestCase):

    def test_run_show_table_format(self):
        from azext_chaos._table_format import scenario_run_show_table_format
        result = {
            'name': '12345678-1234-1234-1234-123456789012',
            'properties': {
                'status': 'Running',
                'startTime': '2026-01-01T00:00:00Z',
                'endTime': None,
            },
        }
        table = scenario_run_show_table_format(result)
        self.assertEqual(table['RunId'],
                         '12345678-1234-1234-1234-123456789012')
        self.assertEqual(table['Status'], 'Running')
        self.assertEqual(table['StartTime'], '2026-01-01T00:00:00Z')
        self.assertIsNone(table['EndTime'])

    def test_run_list_table_format(self):
        from azext_chaos._table_format import scenario_run_list_table_format
        results = [
            {'name': 'run1', 'properties': {
                'status': 'Succeeded',
                'startTime': 't1', 'endTime': 't2',
            }},
        ]
        tables = scenario_run_list_table_format(results)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]['RunId'], 'run1')


class TestValidationTableFormat(unittest.TestCase):

    def test_validation_show_table_format_succeeded(self):
        from azext_chaos._table_format import validation_show_table_format
        result = {
            'name': 'latest',
            'properties': {
                'status': 'Succeeded',
                'startTime': '2026-01-01T00:00:00Z',
                'endTime': '2026-01-01T00:01:00Z',
                'errors': [],
                'validationErrors': {'errors': []},
            },
        }
        table = validation_show_table_format(result)
        self.assertEqual(table['Status'], 'Succeeded')
        self.assertEqual(table['Errors'], '')

    def test_validation_show_table_format_with_errors(self):
        from azext_chaos._table_format import validation_show_table_format
        result = {
            'name': 'latest',
            'properties': {
                'status': 'Failed',
                'startTime': '2026-01-01T00:00:00Z',
                'endTime': '2026-01-01T00:01:00Z',
                'errors': [{'message': 'system error'}],
                'validationErrors': {
                    'errors': [{'message': 'e1'}, {'message': 'e2'}],
                },
            },
        }
        table = validation_show_table_format(result)
        self.assertEqual(table['Errors'], '1 system, 2 validation')

    def test_validation_show_table_format_no_mutation(self):
        """validation_show_table_format must not inject keys into the input dict."""
        from azext_chaos._table_format import validation_show_table_format
        result = {
            'name': 'latest',
            'properties': {
                'status': 'Succeeded',
                'startTime': '2026-01-01T00:00:00Z',
                'endTime': '2026-01-01T00:01:00Z',
                'errors': [],
                'validationErrors': {'errors': []},
            },
        }
        original_keys = set(result.keys())
        validation_show_table_format(result)
        self.assertEqual(set(result.keys()), original_keys)


class TestPermissionFixTableFormat(unittest.TestCase):

    def test_permission_fix_show_table_format(self):
        from azext_chaos._table_format import permission_fix_show_table_format
        result = {
            'name': 'latest',
            'properties': {
                'state': 'Succeeded',
                'summary': '3 roles assigned',
                'whatIfMode': False,
            },
        }
        table = permission_fix_show_table_format(result)
        self.assertEqual(table['State'], 'Succeeded')
        self.assertEqual(table['Summary'], '3 roles assigned')
        self.assertFalse(table['WhatIfMode'])

    def test_permission_fix_show_what_if_mode(self):
        from azext_chaos._table_format import permission_fix_show_table_format
        result = {
            'name': 'latest',
            'properties': {
                'state': 'Succeeded',
                'summary': '3 roles would be assigned',
                'whatIfMode': True,
            },
        }
        table = permission_fix_show_table_format(result)
        self.assertTrue(table['WhatIfMode'])


class TestDiscoveredResourceTableFormat(unittest.TestCase):

    def test_discovered_resource_show_table_format(self):
        from azext_chaos._table_format import (
            discovered_resource_show_table_format,
        )
        result = {
            'name': 'myvm',
            'properties': {
                'namespace': 'Microsoft.Compute',
                'resourceName': 'myvm',
                'resourceType': 'virtualMachines',
                'fullyQualifiedIdentifier': '/subscriptions/sub/rg/vm',
                'discoveredAt': '2026-01-01T00:00:00Z',
                'scope': '/subscriptions/sub/resourceGroups/rg',
            },
        }
        table = discovered_resource_show_table_format(result)
        # F10e: leads with human-meaningful columns; the opaque GUID is now 'Id'.
        self.assertEqual(table['Id'], 'myvm')
        self.assertEqual(table['ResourceName'], 'myvm')
        self.assertEqual(table['ResourceType'], 'virtualMachines')
        self.assertEqual(table['Namespace'], 'Microsoft.Compute')
        self.assertEqual(table['DiscoveredAt'], '2026-01-01T00:00:00Z')
        # ResourceName must precede Id so the table does not lead with the GUID.
        keys = list(table.keys())
        self.assertLess(keys.index('ResourceName'), keys.index('Id'))

    def test_discovered_resource_list_table_format(self):
        from azext_chaos._table_format import (
            discovered_resource_list_table_format,
        )
        results = [
            {'name': 'r1', 'properties': {
                'namespace': 'ns1', 'resourceName': 'r1',
                'resourceType': 'rt1',
                'fullyQualifiedIdentifier': 'fqi1',
                'discoveredAt': 't1', 'scope': 's1',
            }},
            {'name': 'r2', 'properties': {
                'namespace': 'ns2', 'resourceName': 'r2',
                'resourceType': 'rt2',
                'fullyQualifiedIdentifier': 'fqi2',
                'discoveredAt': 't2', 'scope': 's2',
            }},
        ]
        tables = discovered_resource_list_table_format(results)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]['Id'], 'r1')
        self.assertEqual(tables[0]['ResourceName'], 'r1')
        self.assertEqual(tables[1]['Namespace'], 'ns2')


class TestScenarioRunErrorSurfacing(unittest.TestCase):
    """F4: a failed run's error detail is surfaced in --output table."""

    def test_surfaces_errors_list(self):
        from azext_chaos._table_format import scenario_run_show_table_format
        result = {
            'name': 'run-1',
            'properties': {
                'status': 'Failed',
                'startTime': 't0',
                'endTime': 't1',
                'errors': [
                    {'errorCode': 'AuthorizationFailed',
                     'errorMessage': "Action 'shutdown' failed."},
                ],
            },
        }
        table = scenario_run_show_table_format(result)
        self.assertEqual(table['Status'], 'Failed')
        self.assertIn('AuthorizationFailed', table['Error'])
        self.assertIn("Action 'shutdown' failed.", table['Error'])

    def test_surfaces_execution_errors(self):
        from azext_chaos._table_format import scenario_run_show_table_format
        result = {
            'name': 'run-2',
            'properties': {
                'status': 'Failed',
                'executionErrors': {
                    'errorCode': 'ProviderError',
                    'errorMessage': 'provider rejected the action',
                },
            },
        }
        table = scenario_run_show_table_format(result)
        self.assertIn('ProviderError', table['Error'])

    def test_no_error_on_success(self):
        from azext_chaos._table_format import scenario_run_show_table_format
        result = {'name': 'run-3', 'properties': {'status': 'Succeeded'}}
        table = scenario_run_show_table_format(result)
        self.assertEqual(table['Error'], '')


class TestWorkspaceDiscoveryEvaluationTableFormat(unittest.TestCase):

    def test_workspace_discovery_show(self):
        from azext_chaos._table_format import (
            workspace_discovery_show_table_format,
        )
        result = {
            'name': 'latest',
            'properties': {
                'status': 'Succeeded',
                'startTime': '2026-01-01T00:00:00Z',
                'endTime': '2026-01-01T00:05:00Z',
            },
        }
        table = workspace_discovery_show_table_format(result)
        self.assertEqual(table['Status'], 'Succeeded')
        self.assertEqual(table['StartTime'], '2026-01-01T00:00:00Z')
        self.assertEqual(table['EndTime'], '2026-01-01T00:05:00Z')

    def test_workspace_evaluation_show(self):
        from azext_chaos._table_format import (
            workspace_evaluation_show_table_format,
        )
        result = {
            'name': 'latest',
            'properties': {
                'status': 'InProgress',
                'startTime': '2026-01-01T00:00:00Z',
                'endTime': None,
            },
        }
        table = workspace_evaluation_show_table_format(result)
        self.assertEqual(table['Status'], 'InProgress')
        self.assertIsNone(table['EndTime'])


class TestHelpEntries(unittest.TestCase):
    """Verify every command group and command has a help entry."""

    _REQUIRED_GROUPS = [
        'chaos',
        'chaos workspace',
        'chaos scenario',
        'chaos scenario config',
        'chaos scenario run',
        'chaos discovered-resource',
    ]

    _REQUIRED_COMMANDS = [
        'chaos workspace create',
        'chaos workspace show',
        'chaos workspace list',
        'chaos workspace delete',
        'chaos workspace update',
        'chaos workspace refresh-recommendation',
        'chaos workspace evaluate-scenarios',
        'chaos workspace show-discovery',
        'chaos workspace show-evaluation',
        'chaos scenario create',
        'chaos scenario show',
        'chaos scenario list',
        'chaos scenario delete',
        'chaos scenario config create',
        'chaos scenario config show',
        'chaos scenario config list',
        'chaos scenario config delete',
        'chaos scenario config validate',
        'chaos scenario config show-validation',
        'chaos scenario config fix-permissions',
        'chaos scenario config show-permission-fix',
        'chaos scenario run start',
        'chaos scenario run list',
        'chaos scenario run show',
        'chaos scenario run cancel',
        'chaos discovered-resource list',
        'chaos discovered-resource show',
    ]

    def test_all_groups_have_help(self):
        from azext_chaos._help import helps
        for group in self._REQUIRED_GROUPS:
            with self.subTest(group=group):
                self.assertIn(group, helps)

    def test_all_commands_have_help(self):
        from azext_chaos._help import helps
        for cmd in self._REQUIRED_COMMANDS:
            with self.subTest(cmd=cmd):
                self.assertIn(cmd, helps)

    def test_all_commands_have_at_least_two_examples(self):
        from azext_chaos._help import helps
        for cmd in self._REQUIRED_COMMANDS:
            with self.subTest(cmd=cmd):
                help_text = helps[cmd]
                if 'type: group' in help_text:
                    continue
                count = help_text.count('- name:')
                self.assertGreaterEqual(
                    count, 2,
                    f"Command '{cmd}' has {count} examples, expected >= 2"
                )

    def test_alias_begins_with_alias_of(self):
        from azext_chaos._help import helps
        alias_help = helps['chaos workspace evaluate-scenarios']
        self.assertTrue(
            'Alias of `az chaos workspace refresh-recommendation`'
            in alias_help
        )

    def test_config_create_has_zones_example(self):
        from azext_chaos._help import helps
        help_text = helps['chaos scenario config create']
        self.assertIn("zones=", help_text)

    def test_config_create_has_physical_zones_example(self):
        from azext_chaos._help import helps
        help_text = helps['chaos scenario config create']
        self.assertIn("physical-zones", help_text)

    def test_config_create_notes_mutual_exclusion(self):
        from azext_chaos._help import helps
        help_text = helps['chaos scenario config create']
        self.assertIn('mutually exclusive', help_text)

    def test_run_start_has_all_four_pairings(self):
        from azext_chaos._help import helps
        help_text = helps['chaos scenario run start']
        self.assertIn('--skip-validation --no-wait', help_text)
        skip_count = help_text.count('--skip-validation')
        no_wait_count = help_text.count('--no-wait')
        self.assertGreaterEqual(skip_count, 3)
        self.assertGreaterEqual(no_wait_count, 3)


class TestCommandsWiring(unittest.TestCase):
    """Verify table_transformer is wired for custom commands."""

    def test_validate_has_table_transformer(self):
        from unittest.mock import MagicMock, patch
        from azext_chaos.commands import load_command_table
        mock_loader = MagicMock()
        mock_loader.command_table = {}
        with patch('azext_chaos.commands._register_aaz_subclass_overrides'):
            load_command_table(mock_loader, None)
        ctx = mock_loader.command_group.return_value.__enter__.return_value
        validate_call = next(
            (c for c in ctx.custom_command.call_args_list
             if c.args[0] == 'validate'),
            None
        )
        self.assertIsNotNone(validate_call, "'validate' command not registered")
        self.assertIn('table_transformer', validate_call.kwargs)

    def test_start_has_table_transformer(self):
        from unittest.mock import MagicMock, patch
        from azext_chaos.commands import load_command_table
        mock_loader = MagicMock()
        mock_loader.command_table = {}
        with patch('azext_chaos.commands._register_aaz_subclass_overrides'):
            load_command_table(mock_loader, None)
        ctx = mock_loader.command_group.return_value.__enter__.return_value
        start_call = next(
            (c for c in ctx.custom_command.call_args_list
             if c.args[0] == 'start'),
            None
        )
        self.assertIsNotNone(start_call, "'start' command not registered")
        self.assertIn('table_transformer', start_call.kwargs)


class TestSetupTableFormat(unittest.TestCase):
    """Tests for setup_table_format."""

    def test_projects_discovered_scenarios(self):
        from azext_chaos._table_format import setup_table_format
        result = {
            "workspace": {"name": "ws"},
            "scenarios": [
                {"name": "ZoneDown-1.0",
                 "properties": {"version": "1.0",
                                "recommendation": {
                                    "recommendationStatus": "Recommended"}}},
            ],
        }
        rows = setup_table_format(result)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Name'], 'ZoneDown-1.0')
        self.assertEqual(rows[0]['Recommendation'], 'Recommended')

    def test_empty_when_no_scenarios(self):
        from azext_chaos._table_format import setup_table_format
        self.assertEqual(setup_table_format({"scenarios": []}), [])
        self.assertEqual(setup_table_format({}), [])


if __name__ == '__main__':
    unittest.main()
