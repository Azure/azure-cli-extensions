# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class IpGroupScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_ip_group')
    def test_ip_group(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd(
            'network ip-group create -g {rg} -n {name} --tags foo=doo '
            '--ip-addresses 10.0.0.1 10.0.0.2 --location "westus"',
            checks=[self.check('tags.foo', 'doo'), self.check('name', '{name}')]
        )
        self.cmd('network ip-group update -g {rg} -n {name} --tags foo=boo --ip-addresses 10.0.1.0', checks=[
            self.check('tags.foo', 'boo'),
            self.check('ipAddresses', "['10.0.1.0']")
        ])
        count = len(self.cmd('network ip-group list').get_output_in_json())
        self.cmd('network ip-group show -g {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'boo')
        ])
        self.cmd('network ip-group delete -g {rg} -n {name}')
        final_count = len(self.cmd('network ip-group list').get_output_in_json())
        self.assertTrue(final_count, count - 1)
