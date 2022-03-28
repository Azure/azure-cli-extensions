# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AgsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_amg')
    def test_amg_e2e(self, resource_group):

        self.kwargs.update({
            'name': 'clitestamg',
            'location': 'westeurope'
        })

        self.cmd('grafana create -g {rg} -n {name} -l {location} --tags foo=doo --skip-role-assignments', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('grafana list -g {rg}')
        count = len(self.cmd('grafana list').get_output_in_json())
        self.cmd('grafana show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'doo')
        ])

        self.cmd('grafana delete -g {rg} -n {name} --yes')
        final_count = len(self.cmd('grafana list').get_output_in_json())
        self.assertTrue(final_count, count - 1)