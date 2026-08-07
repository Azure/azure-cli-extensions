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


class QuantumSuiteOffersTargetListTest(unittest.TestCase):
    """Unit tests (no Azure required) for the suite offer target listing support."""

    def test_transform_targets_suite_offer_shape(self):
        from ...commands import transform_targets

        # Data-plane suite offer status uses the same shape as the workspace providers list.
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

    def test_list_targets_normalizes_value_wrapper(self):
        from unittest import mock
        from ...operations import suiteoffers

        status = {'value': [{'id': 'atom-boulder', 'currentAvailability': 'Available', 'targets': []}]}
        with mock.patch.object(suiteoffers, 'cf_suite_offer_status', return_value=status), \
                mock.patch.object(suiteoffers, '_get_suite_offer_location', return_value='westus'), \
                mock.patch('azure.cli.core.commands.client_factory.get_subscription_id', return_value='sub'):
            result = suiteoffers.list_targets(self._fake_cmd(), provider_id='atom-boulder')
        self.assertEqual(result, status['value'])

    def test_list_targets_wraps_single_object(self):
        from unittest import mock
        from ...operations import suiteoffers

        status = {'id': 'atom-boulder', 'currentAvailability': 'Available', 'targets': []}
        with mock.patch.object(suiteoffers, 'cf_suite_offer_status', return_value=status), \
                mock.patch.object(suiteoffers, '_get_suite_offer_location', return_value='westus'), \
                mock.patch('azure.cli.core.commands.client_factory.get_subscription_id', return_value='sub'):
            result = suiteoffers.list_targets(self._fake_cmd(), provider_id='atom-boulder')
        self.assertEqual(result, [status])

    @staticmethod
    def _fake_cmd():
        class _Ctx:
            pass

        class _Cmd:
            cli_ctx = _Ctx()

        return _Cmd()


if __name__ == '__main__':
    unittest.main()
