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

    def test_workspace(self):
        # Since azure quantum is still in private preview, we require
        # these tests to run in a specific subscription (AzureQuantum-test)
        # if running somewhere else, just skip
        if not is_private_preview_subscription(self):
            self.skipTest(f"Need to run azure quantum tests in subscription {TEST_SUBS}")

        # clear
        self.cmd(f'az quantum workspace clear')

        # list
        workspaces = self.cmd('az quantum workspace list -o json').get_output_in_json()
        assert len(workspaces) > 0
        self.cmd('az quantum workspace list -o json', checks=[
            self.check(f"[?name=='{TEST_WORKSPACE}'].resourceGroup | [0]", TEST_RG)
        ])

        # set
        self.cmd(f'az quantum workspace set -g {TEST_RG} -w {TEST_WORKSPACE} -o json', checks=[
            self.check("name", TEST_WORKSPACE)
        ])

        # show
        self.cmd(f'az quantum workspace show -o json', checks=[
            self.check("name", TEST_WORKSPACE)
        ])

        # clear
        self.cmd(f'az quantum workspace clear')
