# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import is_private_preview_subscription, TEST_WORKSPACE, TEST_RG, TEST_SUBS

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumScenarioTest(ScenarioTest):

    def test_targets(self):
        # Since azure quantum is still in private preview, we require
        # these tests to run in a specific subscription (AzureQuantum-test)
        # if running somewhere else, just skip
        if not is_private_preview_subscription(self):
            self.skipTest(f"Need to run azure quantum tests in subscription {TEST_SUBS}")

        # set current workspace:
        self.cmd(f'az quantum workspace set -g {TEST_RG} -w {TEST_WORKSPACE}')

        # clear current target
        self.cmd(f'az quantum target clear')

        # list
        targets = self.cmd('az quantum target list -o json').get_output_in_json()
        assert len(targets) > 0
        self.cmd('az quantum target list -o json', checks=[
            self.check(f"[?id=='Microsoft'].targets | [0] | [?id=='microsoft.paralleltempering.cpu'].id | [0]", 'microsoft.paralleltempering.cpu')
        ])

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
