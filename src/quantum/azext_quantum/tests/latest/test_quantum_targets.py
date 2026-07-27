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
from ...commands import transform_targets

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

    @live_only()
    def test_target_list_provider_status(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()}')

        # The JSON output that feeds the table should expose the provider account's
        # current availability, which is the source of the "Provider Status" column.
        providers = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(providers) > 0
        for provider in providers:
            assert "currentAvailability" in provider

        # The table view should surface the provider status as a dedicated column.
        table_output = self.cmd('az quantum target list -o table').output
        assert "Provider Status" in table_output

    def test_target_errors(self):
        self.cmd('az quantum target clear')
        issue_cmd_with_param_missing(self, "az quantum target set", "az quantum target set -t target-id\nSelect a default when submitting jobs to Azure Quantum.")

    def test_transform_targets(self):
        providers = [
            {
                "id": "atom-dev",
                "currentAvailability": "Available",
                "targets": [
                    {
                        "id": "atom.qpu.vb-dev.physical",
                        "currentAvailability": "Degraded",
                        "averageQueueTime": 7
                    }
                ]
            }
        ]

        table = transform_targets(providers)
        self.assertEqual(len(table), 1)
        row = table[0]
        self.assertEqual(row['Provider'], "atom-dev")
        self.assertEqual(row['Provider Status'], "Available")
        self.assertEqual(row['Target-id'], "atom.qpu.vb-dev.physical")
        self.assertEqual(row['Current Availability'], "Degraded")
        self.assertEqual(row['Average Queue Time (seconds)'], 7)

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
