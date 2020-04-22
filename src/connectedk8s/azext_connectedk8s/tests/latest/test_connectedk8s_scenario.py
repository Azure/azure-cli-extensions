# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)  # pylint: disable=import-error
from azure_devtools.scenario_tests import AllowLargeResponse  # pylint: disable=import-error


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Connectedk8sScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_connectedk8s')
    def test_connectedk8s(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('connectedk8s connect -g {rg} -n {name} -l eastus2euap --tags foo=doo', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        count = len(self.cmd('connectedk8s list').get_output_in_json())
        self.cmd('connectedk8s show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'boo')
        ])
        self.cmd('connectedk8s delete -g {rg} -n {name} -y')
        final_count = len(self.cmd('connectedk8s list').get_output_in_json())
        self.assertTrue(final_count, count - 1)
