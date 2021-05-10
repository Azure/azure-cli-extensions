# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from knack.util import CLIError
from azure.cli.testsdk import ScenarioTest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ConnectedvmwareScenarioTest(ScenarioTest):
    
    def test_connectedvmware_vcenter(self):  
        resource_group = "santosh-rg" 
        location = ""
        custom_loc = ""

        # count the list of vcenter resources in this resource group
        count = len(self.cmd('az connectedvmware vcenter list --resource-group santosh-rg').get_output_in_json())
        # vcenter count list should report 1
        self.assertEqual(count, 1, 'cluster count expected to be 1')
