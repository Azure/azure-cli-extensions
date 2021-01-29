# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import is_private_preview_subscription, TEST_WORKSPACE, TEST_RG, TEST_WORKSPACE_LOCATION, TEST_SUBS

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumTargetsScenarioTest(ScenarioTest):

    def test_targets(self):
        # Since azure quantum is still in private preview, we require
        # these tests to run in a specific subscription (AzureQuantum-test)
        # if running somewhere else, just skip
        if not is_private_preview_subscription(self):
            self.skipTest(f"Need to run azure quantum tests in subscription {TEST_SUBS}")

        # Because we are in private preview, we need to set the subscription again so it gets
        # reflected in the recordings. Once this is not dependent on a particular subscription
        # this can be removed.
        self.cmd(f"az account set -s {TEST_SUBS}")

        # set current workspace:
        self.cmd(f'az quantum workspace set -g {TEST_RG} -w validator-qio-parallel-tempering-cpu-eastus2euap -l eastus2euap')

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
