# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Connectedk8sScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_connectedk8s')
    def test_connectedk8s(self, resource_group):

        self.kwargs.update({
            'name': 'test1',
            'rg': resource_group
        })

        self.cmd('connectedk8s connect -g akkeshar3 -n {name}', checks=[
            self.check('name', '{name}')
        ])
        #self.cmd('connectedk8s update -g {rg} -n {name}', checks=[
        #])
        count = len(self.cmd('connectedk8s list').get_output_in_json())
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}')
        ])
        self.cmd('connectedk8s delete -g {rg} -n {name} --yes')
        final_count = len(self.cmd('connectedk8s list').get_output_in_json())
        self.assertTrue(final_count, count - 1)
