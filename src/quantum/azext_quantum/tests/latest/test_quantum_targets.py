# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import pytest
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, issue_cmd_with_param_missing

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumTargetsScenarioTest(ScenarioTest):

    def test_targets(self):
        # set current workspace:
        self.cmd(f'az quantum workspace set -g {get_test_resource_group()} -w {get_test_workspace()} -l {get_test_workspace_location()}')

        # clear current target
        self.cmd(f'az quantum target clear')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0

        # set
        self.cmd(f'az quantum target set -t microsoft.paralleltempering.cpu -o json', checks=[
            self.check("targetId", "microsoft.paralleltempering.cpu")
        ])

        # show
        self.cmd(f'az quantum target show -o json', checks=[
            self.check("targetId", "microsoft.paralleltempering.cpu")
        ])
        self.cmd(f'az quantum target show -t microsoft.simulatedannealing.cpu -o json', checks=[
            self.check("targetId", "microsoft.simulatedannealing.cpu")
        ])

        # clear
        self.cmd(f'az quantum target clear')

    # @pytest.fixture(autouse=True)
    # def _pass_fixtures(self, capsys):
    #     self.capsys = capsys
    # # See "TODO" in issue_cmd_with_param_missing un utils.py

    def test_target_errors(self):
        self.cmd(f'az quantum target clear')
        issue_cmd_with_param_missing(self, "az quantum target set", "az quantum target set -t target-id\nSelect a default when submitting jobs to Azure Quantum.")
