# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse, live_only
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

from .utils import get_test_resource_group, get_test_workspace, get_test_workspace_location, get_test_workspace_storage, get_test_workspace_random_name
from ..._version_check_helper import check_version
from datetime import datetime
from ...__init__ import CLI_REPORTED_VERSION 

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class QuantumWorkspacesScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_workspace(self):
        # clear
        self.cmd(f'az quantum workspace clear')

        # initialize values
        test_location = get_test_workspace_location()
        test_workspace = get_test_workspace()
        test_resource_group = get_test_resource_group()

        # list
        workspaces = self.cmd(f'az quantum workspace list -l {test_location} -o json').get_output_in_json()
        assert len(workspaces) > 0
        self.cmd('az quantum workspace list -o json', checks=[
            self.check(f"[?name=='{test_workspace}'].resourceGroup | [0]", test_resource_group)
        ])

        # set
        self.cmd(f'az quantum workspace set -g {test_resource_group} -w {test_workspace} -l {test_location} -o json', checks=[
            self.check("name", test_workspace)
        ])

        # show
        self.cmd(f'az quantum workspace show -o json', checks=[
            self.check("name", test_workspace)
        ])

        # clear
        self.cmd(f'az quantum workspace clear')

    @live_only()
    def test_workspace_create_destroy(self):
        # initialize values
        test_location = get_test_workspace_location()
        test_resource_group = get_test_resource_group()
        test_workspace_temp = get_test_workspace_random_name()
        test_storage_account = get_test_workspace_storage()

        # create
        self.cmd(f'az quantum workspace create -g {test_resource_group} -w {test_workspace_temp} -l {test_location} -a {test_storage_account} -r "Microsoft/Basic" -o json --skip-role-assignment', checks=[
           self.check("name", test_workspace_temp),
           self.check("provisioningState", "Accepted")  # Status is accepted since we're not linking the storage account.
        ])

        # delete
        self.cmd(f'az quantum workspace delete -g {test_resource_group} -w {test_workspace_temp} -o json', checks=[
           self.check("name", test_workspace_temp),
           self.check("provisioningState", "Deleting")
        ])

    @live_only()
    def test_version_check(self):
        # initialize values
        test_old_date = "2021-04-01"
        test_today = str(datetime.today()).split(' ')[0] 
        test_old_reported_version = "0.1.0"
        test_current_reported_version = CLI_REPORTED_VERSION
        test_none_version = None
        test_config = None

        message = check_version(test_config, test_current_reported_version, test_old_date)
        assert test_current_reported_version in message

        message = check_version(test_config, test_old_reported_version, test_old_date)
        assert test_old_reported_version in message

        message = check_version(test_config, test_none_version, test_today)
        assert message is None  # Note: list_versions("quantum") fails during these tests
     