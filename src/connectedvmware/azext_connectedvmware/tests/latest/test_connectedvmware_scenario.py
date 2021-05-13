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

        # count the list of vcenter resources in this resource group
        count = len(self.cmd('az connectedvmware vcenter list --resource-group ' + resource_group).get_output_in_json())
        # vcenter count list should report 1
        self.assertEqual(count, 1, 'cluster count expected to be 1')

    def test_connectedvmware_resourcePool(self):
        resource_group = "santosh-rg"

        # count the resource-pool resources in this resource group
        count = len(self.cmd('az connectedvmware resource-pool list --resource-group ' + resource_group).get_output_in_json())
        # resource-pool count should be greater than 1
        assert count >= 1

    def test_connectedvmware_virtualNetwork(self):
        resource_group = "santosh-rg"

        # count the virtual-network resources in this resource group
        count = len(self.cmd('az connectedvmware virtual-network list --resource-group ' + resource_group).get_output_in_json())
        # virtual-network count should be greater than or equal to 1
        assert count >= 1

    def test_connectedvmware_vm(self):
        resource_group = "santosh-rg"

        # count the list of vm resources in this resource group
        count = len(self.cmd('az connectedvmware vm list --resource-group ' + resource_group).get_output_in_json())
        # vm count should be greater than or equal 1
        assert count >= 1
