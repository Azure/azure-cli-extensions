# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class PortalScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_portal_testRG'[:9], key='rg')
    def test_portal(self, resource_group):

        self.kwargs.update({
            'testDashboard': self.create_random_name(prefix='cli_test_dashboards'[:9], length=24),
        })

        self.cmd('az portal dashboard create '
                 '--location "eastus" '
                 '--properties-lenses "{{\\"aLens\\":{{\\"order\\":1,\\"parts\\":{{\\"aPart\\":{{\\"position\\":{{\\"colSpan\\":3,\\"rowSpan\\":4,\\"x\\":1,\\"y\\":2}}}},\\"bPart\\":{{\\"position\\":{{\\"colSpan\\":6,\\"rowSpan\\":6,\\"x\\":5,\\"y\\":5}}}}}}}},\\"bLens\\":{{\\"order\\":2,\\"parts\\":{{}}}}}}" '
                 '--properties-metadata metadata=[object Object]=undefined '
                 '--tags aKey=aValue anotherKey=anotherValue '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az portal dashboard show '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az portal dashboard list '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az portal dashboard list',
                 checks=[])

        self.cmd('az portal dashboard update '
                 '--tags aKey=bValue anotherKey=anotherValue2 '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az portal dashboard delete '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[])
