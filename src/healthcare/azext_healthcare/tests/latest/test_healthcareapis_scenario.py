# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ApimgmtScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_apimgmt')
    def test_apimgmt(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

# create_or_update -- create
        self.cmd('healthcare create  --resource-group "rg1" --name "service1" --kind "fhir" --location "westus"', checks=[
        ])

        self.cmd('healthcare create  --resource-group "rg1" --name "service1"', checks=[
        ])

        self.cmd('healthcare create  --resource-group "rg1" --name "service1"', checks=[
        ])

# create_or_update -- update
        self.cmd('healthcare update  --resource-group "rg1" --name "service1" --kind "fhir" --location "westus"', checks=[
        ])

        self.cmd('healthcare update  --resource-group "rg1" --name "service1"', checks=[
        ])

        self.cmd('healthcare update  --resource-group "rg1" --name "service1"', checks=[
        ])

# delete -- delete
        self.cmd('healthcare delete  --resource-group "rg1" --name "service1"', checks=[
        ])

        self.cmd('healthcare delete  --resource-group "rg1" --name "service1"', checks=[
        ])

        self.cmd('healthcare delete  --resource-group "rg1" --name "service1"', checks=[
        ])

# list_by_resource_group -- list
        self.cmd('healthcare list  --resource-group "rg1"', checks=[
        ])

        self.cmd('healthcare list  --resource-group "rg1"', checks=[
        ])

        self.cmd('healthcare list  --resource-group "rg1"', checks=[
        ])

# list -- list
        self.cmd('healthcare list  --resource-group "rg1"', checks=[
        ])

        self.cmd('healthcare list  --resource-group "rg1"', checks=[
        ])

        self.cmd('healthcare list  --resource-group "rg1"', checks=[
        ])

# get -- show
        self.cmd('healthcare show  --resource-group "rg1" --name "service1"', checks=[
        ])

        self.cmd('healthcare show  --resource-group "rg1" --name "service1"', checks=[
        ])

        self.cmd('healthcare show  --resource-group "rg1" --name "service1"', checks=[
        ])
