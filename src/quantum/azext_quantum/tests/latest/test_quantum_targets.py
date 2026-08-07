# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import pytest
import unittest

from azure.cli.testsdk.scenario_tests import live_only
from azure.cli.testsdk import (ScenarioTest)

from .utils import (get_test_resource_group, get_test_workspace, get_test_workspace_location, issue_cmd_with_param_missing,
                    get_test_workspace_random_name, get_test_workspace_storage, get_test_target_provider_sku_list,
                    get_test_target_provider, get_test_target_target)
from ...operations.target import get_provider

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumTargetsScenarioTest(ScenarioTest):

    @live_only()
    def test_targets(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()}')

        # clear current target
        self.cmd('az quantum target clear')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

        # set
        self.cmd('az quantum target set -t ionq.simulator -o json', checks=[
            self.check("targetId", "ionq.simulator")
        ])

        # show
        self.cmd('az quantum target show -o json', checks=[
            self.check("targetId", "ionq.simulator")
        ])

        # clear
        self.cmd('az quantum target clear')

        # show
        self.cmd('az quantum target show -t ionq.simulator -o json', checks=[
            self.check("targetId", "ionq.simulator")
        ])

    def test_target_errors(self):
        self.cmd('az quantum target clear')
        issue_cmd_with_param_missing(self, "az quantum target set", "az quantum target set -t target-id\nSelect a default when submitting jobs to Azure Quantum.")

    @live_only()
    def test_get_provider(self):
        test_resource_group = get_test_resource_group()
        test_location = get_test_workspace_location()
        test_storage = get_test_workspace_storage()
        test_target_provider_sku_list = get_test_target_provider_sku_list()
        test_workspace_temp = get_test_workspace_random_name()

        self.cmd(f'az quantum workspace create --auto-accept -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage} -r "{test_target_provider_sku_list}"')

        test_target = get_test_target_target()
        test_expected_provider = get_test_target_provider()
        test_returned_provider = get_provider(self, test_target, test_resource_group, test_workspace_temp)
        assert test_returned_provider == test_expected_provider

        test_target = "nonexistant.target"
        test_expected_provider = None
        test_returned_provider = get_provider(self, test_target, test_resource_group, test_workspace_temp)
        assert test_returned_provider == test_expected_provider

        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp}')


class QuantumTargetListProviderAccountTest(unittest.TestCase):
    """Unit tests (no Azure required) for the provider-account target listing support."""

    def test_transform_targets_provider_account_shape(self):
        from ...commands import transform_targets

        # Data-plane provider-account status uses the same shape as the workspace providers list.
        providers = [
            {
                'id': 'atom-boulder',
                'currentAvailability': 'Available',
                'targets': [
                    {'id': 'atom.qpu', 'currentAvailability': 'Available', 'averageQueueTime': 42}
                ]
            }
        ]
        rows = transform_targets(providers)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Provider'], 'atom-boulder')
        self.assertEqual(rows[0]['Target-id'], 'atom.qpu')
        self.assertEqual(rows[0]['Current Availability'], 'Available')
        self.assertEqual(rows[0]['Average Queue Time (seconds)'], 42)

    def test_target_list_provider_and_workspace_are_mutually_exclusive(self):
        from azure.cli.core.azclierror import MutuallyExclusiveArgumentError
        from ..._validators import validate_target_list_info

        cmd = self._fake_cmd(default_workspace=None)
        namespace = self._fake_namespace(provider_id='atom-boulder', workspace_name='MyWorkspace')
        with self.assertRaises(MutuallyExclusiveArgumentError):
            validate_target_list_info(cmd, namespace)

    def test_target_list_provider_ignores_configured_default_workspace(self):
        from ..._validators import validate_target_list_info

        # A saved default workspace must not conflict with an explicit --provider-id.
        cmd = self._fake_cmd(default_workspace='MyDefaultWorkspace')
        namespace = self._fake_namespace(provider_id='atom-boulder', workspace_name='MyDefaultWorkspace')
        # Should not raise.
        validate_target_list_info(cmd, namespace)

    @staticmethod
    def _fake_cmd(default_workspace):
        class _Config:
            defaults_section_name = 'defaults'

            def get(self, _section, _key, default=None):
                return default_workspace if default_workspace is not None else default

        class _Ctx:
            config = _Config()

        class _Cmd:
            cli_ctx = _Ctx()

        return _Cmd()

    @staticmethod
    def _fake_namespace(**kwargs):
        class _Namespace:
            pass

        namespace = _Namespace()
        for key, value in kwargs.items():
            setattr(namespace, key, value)
        return namespace


if __name__ == '__main__':
    unittest.main()
