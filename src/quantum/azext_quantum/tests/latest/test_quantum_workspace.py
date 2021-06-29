# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import TEST_WORKSPACE_RM, TEST_RG_RM, TEST_SUBS, TEST_WORKSPACE_CREATE_DELETE, TEST_WORKSPACE_LOCATION, TEST_WORKSPACE_SA

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class QuantumWorkspacesScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_workspace(self):
        # clear
        self.cmd(f'az quantum workspace clear')

        # list
        workspaces = self.cmd(f'az quantum workspace list -l {TEST_WORKSPACE_LOCATION} -o json').get_output_in_json()
        assert len(workspaces) > 0
        self.cmd('az quantum workspace list -o json', checks=[
            self.check(f"[?name=='{TEST_WORKSPACE_RM}'].resourceGroup | [0]", TEST_RG_RM)
        ])

        # set
        self.cmd(f'az quantum workspace set -g {TEST_RG_RM} -w {TEST_WORKSPACE_RM} -l {TEST_WORKSPACE_LOCATION} -o json', checks=[
            self.check("name", TEST_WORKSPACE_RM)
        ])

        # show
        self.cmd(f'az quantum workspace show -o json', checks=[
            self.check("name", TEST_WORKSPACE_RM)
        ])

        # clear
        self.cmd(f'az quantum workspace clear')

        # Currently disabled for required role assignment permissions on test subscription

        # create
        # self.cmd(f'az quantum workspace create -g {TEST_RG} -w {TEST_WORKSPACE_CREATE_DELETE} -l {TEST_WORKSPACE_LOCATION} -a {TEST_WORKSPACE_SA} -r "Microsoft/Basic" -o json --skip-role-assignment', checks=[
        #    self.check("name", TEST_WORKSPACE_CREATE_DELETE),
        #    self.check("provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
        # ])

        # delete
        # self.cmd(f'az quantum workspace delete -g {TEST_RG} -w {TEST_WORKSPACE_CREATE_DELETE} -o json', checks=[
        #    self.check("name", TEST_WORKSPACE_CREATE_DELETE),
        #    self.check("provisioningState", "Deleting")
        # ])
