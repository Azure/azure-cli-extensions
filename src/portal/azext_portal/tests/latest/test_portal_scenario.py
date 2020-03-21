# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import JMESPathCheck
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class PortalScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_portal_testRG'[:9], key='rg')
    def test_portal(self, resource_group):

        self.kwargs.update({
            'testDashboard': self.create_random_name(prefix='cli_test_dashboards'[:9], length=24)
        })

        self.cmd('az portal dashboard create '
                 '--location "eastus" '
                 '--input- "src/portal/azext_portal/tests/latest/properties.json" '
                 '--tags aKey=aValue anotherKey=anotherValue '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('name', self.kwargs.get('testDashboard', ''))])
        
        self.cmd('az portal dashboard show '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('name', self.kwargs.get('testDashboard', ''))])
        
        self.cmd('az portal dashboard list '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('[0].name', self.kwargs.get('testDashboard', ''))])

        self.cmd('az portal dashboard list',
                 checks=[JMESPathCheck('[0].name', self.kwargs.get('testDashboard', ''))])

        self.cmd('az portal dashboard update '
                 '--input-path "src/portal/azext_portal/tests/latest/properties-update.json" '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('metadata.model.timeRange.value.relative.duration', 12)])

        self.cmd('az portal dashboard delete '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az portal dashboard import '
                 '--input-path "src/portal/azext_portal/tests/latest/dashboard.json" '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('name', 'testdashboard')])
