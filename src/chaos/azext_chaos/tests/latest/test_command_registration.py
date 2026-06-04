# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import MagicMock, patch

from azext_chaos._help import helps


class TestHelpEntries(unittest.TestCase):
    """Tests for help entries defined in _help.py."""

    def test_chaos_group_help_exists(self):
        self.assertIn('chaos', helps)

    def test_chaos_workspace_group_help_exists(self):
        self.assertIn('chaos workspace', helps)

    def test_chaos_scenario_group_help_exists(self):
        self.assertIn('chaos scenario', helps)

    def test_chaos_scenario_config_group_help_exists(self):
        self.assertIn('chaos scenario config', helps)

    def test_chaos_scenario_run_group_help_exists(self):
        self.assertIn('chaos scenario run', helps)

    def test_chaos_discovered_resource_group_help_exists(self):
        self.assertIn('chaos discovered-resource', helps)

    def test_alias_help_exists(self):
        self.assertIn('chaos workspace evaluate-scenarios', helps)

    def test_alias_help_mentions_canonical_name(self):
        alias_help = helps['chaos workspace evaluate-scenarios']
        self.assertIn(
            'Alias of `az chaos workspace refresh-recommendation`',
            alias_help
        )


class TestCommandRegistration(unittest.TestCase):
    """Tests for command registration in commands.py."""

    def test_load_command_table_callable(self):
        from azext_chaos.commands import load_command_table
        # Create a mock loader with an empty command_table dict
        mock_loader = MagicMock()
        mock_loader.command_table = {}
        with patch('azext_chaos.commands._register_aaz_subclass_overrides'):
            # Should not raise
            load_command_table(mock_loader, None)

    def test_alias_registered_via_subclass(self):
        """Both ``chaos workspace refresh-recommendation`` and
        ``chaos workspace evaluate-scenarios`` are registered via
        ``_register_aaz_subclass_overrides`` (NOT via ``g.custom_command``).
        Patch out the AAZCommand subclass constructors so the test doesn't
        depend on real loader infrastructure (convention #2 caveat:
        AAZCommand requires a real AzCommandsLoader, not a MagicMock).
        """
        from azext_chaos.commands import _register_aaz_subclass_overrides
        mock_loader = MagicMock()
        mock_loader.command_table = {}
        with patch('azext_chaos.custom.ScenarioConfigCreate') as mock_scc, \
                patch('azext_chaos.custom.WorkspaceRefreshRecommendation') as mock_wrr, \
                patch('azext_chaos.custom.WorkspaceEvaluateScenarios') as mock_wes, \
                patch('azext_chaos.custom_wait.ScenarioRunWait') as mock_srw:
            mock_scc.return_value = 'scc-instance'
            mock_wrr.return_value = 'wrr-instance'
            mock_wes.return_value = 'wes-instance'
            mock_srw.return_value = 'srw-instance'
            _register_aaz_subclass_overrides(mock_loader)
        self.assertEqual(
            mock_loader.command_table.get('chaos workspace refresh-recommendation'),
            'wrr-instance',
        )
        self.assertEqual(
            mock_loader.command_table.get('chaos workspace evaluate-scenarios'),
            'wes-instance',
        )
        self.assertEqual(
            mock_loader.command_table.get('chaos scenario config create'),
            'scc-instance',
        )
        self.assertEqual(
            mock_loader.command_table.get('chaos scenario run wait'),
            'srw-instance',
        )


class TestParamsLoadable(unittest.TestCase):
    """Tests for _params.py load_arguments function."""

    def test_load_arguments_callable(self):
        from azext_chaos._params import load_arguments
        mock_loader = MagicMock()
        # Should not raise
        load_arguments(mock_loader, None)


class TestInitModule(unittest.TestCase):
    """Tests for __init__.py ChaosCommandsLoader."""

    def test_command_loader_cls_exists(self):
        from azext_chaos import COMMAND_LOADER_CLS
        self.assertIsNotNone(COMMAND_LOADER_CLS)

    def test_command_loader_cls_is_az_loader(self):
        from azext_chaos import COMMAND_LOADER_CLS
        from azure.cli.core import AzCommandsLoader
        self.assertTrue(issubclass(COMMAND_LOADER_CLS, AzCommandsLoader))


class TestHelpTextExamples(unittest.TestCase):
    """Tests for EPIC-004: help-text examples use correct arg names and friendly placeholders."""

    def test_workspace_create_example_uses_mi_user_assigned(self):
        """E4-T1: workspace create example uses --mi-user-assigned, not --type/--user-assigned-identities."""
        from azext_chaos.aaz.latest.chaos.workspace._create import Create
        docstring = Create.__doc__
        self.assertIn('--mi-user-assigned', docstring)
        self.assertNotIn('--type UserAssigned', docstring)
        self.assertNotIn('--user-assigned-identities', docstring)

    def test_workspace_list_example_no_continuation_token(self):
        """E4-T2: workspace list example has no --continuation-token."""
        from azext_chaos.aaz.latest.chaos.workspace._list import List
        docstring = List.__doc__
        self.assertNotIn('--continuation-token', docstring)

    def test_scenario_config_create_example_uses_friendly_names(self):
        """E4-T3: scenario config create uses ZoneDown-1.0, not UUID."""
        from azext_chaos.aaz.latest.chaos.scenario.config._create import Create
        docstring = Create.__doc__
        self.assertIn('ZoneDown-1.0', docstring)
        self.assertNotIn('12345678-1234-1234-1234-123456789012', docstring)

    def test_scenario_config_create_example_no_scenario_id(self):
        """E4-T3: scenario config create example does not include --scenario-id."""
        from azext_chaos.aaz.latest.chaos.scenario.config._create import Create
        docstring = Create.__doc__
        self.assertNotIn('--scenario-id', docstring)

    def test_scenario_config_list_example_uses_friendly_name(self):
        """E4-T5: scenario config list uses ZoneDown-1.0, not UUID."""
        from azext_chaos.aaz.latest.chaos.scenario.config._list import List
        docstring = List.__doc__
        self.assertIn('ZoneDown-1.0', docstring)
        self.assertNotIn('12345678-1234-1234-1234-123456789012', docstring)

    def test_scenario_config_show_example_uses_friendly_name(self):
        """E4-T6: scenario config show uses ZoneDown-1.0, not UUID."""
        from azext_chaos.aaz.latest.chaos.scenario.config._show import Show
        docstring = Show.__doc__
        self.assertIn('ZoneDown-1.0', docstring)
        self.assertNotIn('12345678-1234-1234-1234-123456789012', docstring)

    def test_fix_permissions_example_uses_correct_command_name(self):
        """E4-T7: fix-permissions example uses fix-permissions, not fix-resource-permission."""
        from azext_chaos.aaz.latest.chaos.scenario.config._fix_permissions import FixPermissions
        docstring = FixPermissions.__doc__
        self.assertIn('fix-permissions', docstring)
        self.assertNotIn('fix-resource-permission', docstring)
        self.assertIn('ZoneDown-1.0', docstring)

    def test_scenario_run_show_example_uses_friendly_name(self):
        """E4-T8: scenario run show uses ZoneDown-1.0, not UUID."""
        from azext_chaos.aaz.latest.chaos.scenario.run._show import Show
        docstring = Show.__doc__
        self.assertIn('ZoneDown-1.0', docstring)
        self.assertNotIn('12345678-1234-1234-1234-123456789012', docstring)

    def test_scenario_run_list_example_uses_friendly_name(self):
        """E4-T9: scenario run list uses ZoneDown-1.0, not UUID."""
        from azext_chaos.aaz.latest.chaos.scenario.run._list import List
        docstring = List.__doc__
        self.assertIn('ZoneDown-1.0', docstring)
        self.assertNotIn('12345678-1234-1234-1234-123456789012', docstring)


class TestScenarioIdAutoDerivation(unittest.TestCase):
    """Tests for E4-T4: --scenario-id auto-derivation via custom subclass.

    The auto-derivation runs in :class:`azext_chaos.custom.ScenarioConfigCreate`
    (an :class:`AAZCommand` subclass registered in commands.py) so that the
    generated ``aaz/latest/.../config/_create.py`` module stays pristine.
    """

    def _make_create_cmd(self, scenario_id, resource_group, workspace_name, scenario_name, subscription_id):
        """Create a minimally-initialized ScenarioConfigCreate instance for testing pre_operations."""
        from azext_chaos.custom import ScenarioConfigCreate
        from azure.cli.core.aaz._arg import AAZUndefined
        cmd = ScenarioConfigCreate.__new__(ScenarioConfigCreate)
        cmd.ctx = MagicMock()
        cmd.ctx.subscription_id = subscription_id
        args = MagicMock()
        # AAZ uses AAZUndefined for unset args, not None
        args.scenario_id = scenario_id if scenario_id is not None else AAZUndefined
        args.resource_group = resource_group
        args.workspace_name = workspace_name
        args.scenario_name = scenario_name
        cmd.ctx.args = args
        return cmd, args

    def test_pre_operations_synthesizes_scenario_id_when_not_provided(self):
        """pre_operations sets scenario_id from other args when not explicitly provided."""
        cmd, args = self._make_create_cmd(
            scenario_id=None,  # Will be set to AAZUndefined
            resource_group='myRG',
            workspace_name='myWorkspace',
            scenario_name='ZoneDown-1.0',
            subscription_id='11111111-2222-3333-4444-555555555555',
        )

        cmd.pre_operations()

        expected_id = (
            '/subscriptions/11111111-2222-3333-4444-555555555555'
            '/resourceGroups/myRG/providers/Microsoft.Chaos'
            '/workspaces/myWorkspace/scenarios/ZoneDown-1.0'
        )
        self.assertEqual(args.scenario_id, expected_id)

    def test_pre_operations_preserves_explicit_scenario_id(self):
        """pre_operations does not overwrite an explicitly provided scenario_id."""
        explicit_id = '/subscriptions/aaaa/resourceGroups/rg/providers/Microsoft.Chaos/workspaces/ws/scenarios/sc'
        cmd, args = self._make_create_cmd(
            scenario_id=explicit_id,
            resource_group='myRG',
            workspace_name='myWorkspace',
            scenario_name='ZoneDown-1.0',
            subscription_id='11111111-2222-3333-4444-555555555555',
        )

        cmd.pre_operations()

        self.assertEqual(args.scenario_id, explicit_id)

    def test_aaz_create_pre_operations_is_pristine(self):
        """The AAZ-generated Create.pre_operations must be a no-op (pristine).

        Auto-derivation lives in the ScenarioConfigCreate subclass; the
        generated module must contain no hand-edits.
        """
        from azext_chaos.aaz.latest.chaos.scenario.config._create import Create
        from azure.cli.core.aaz._arg import AAZUndefined
        cmd = Create.__new__(Create)
        cmd.callbacks = {}
        cmd.ctx = MagicMock()
        cmd.ctx.subscription_id = 'unused'
        args = MagicMock()
        args.scenario_id = AAZUndefined
        args.resource_group = 'rg'
        args.workspace_name = 'ws'
        args.scenario_name = 'sn'
        cmd.ctx.args = args

        cmd.pre_operations()

        # Pristine pre_operations must not mutate args.scenario_id.
        self.assertEqual(args.scenario_id, AAZUndefined)


if __name__ == '__main__':
    unittest.main()
