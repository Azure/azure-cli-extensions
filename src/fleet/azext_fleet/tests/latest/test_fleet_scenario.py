# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class FleetScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_fleet')
    def test_fleet(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('fleet create -g {rg} -n {name} --tags foo=doo', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('fleet update -g {rg} -n {name} --tags foo=boo', checks=[
            self.check('tags.foo', 'boo')
        ])
        count = len(self.cmd('fleet list').get_output_in_json())
        self.cmd('fleet show - {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'boo')
        ])
        self.cmd('fleet delete -g {rg} -n {name}')
        final_count = len(self.cmd('fleet list').get_output_in_json())
        self.assertTrue(final_count, count - 1)