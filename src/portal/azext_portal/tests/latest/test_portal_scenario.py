# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import JMESPathCheck
from azure.cli.testsdk import JMESPathCheckExists
from azure.cli.testsdk import NoneCheck
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
                 checks=[
                     JMESPathCheck('name', self.kwargs.get(
                         'testDashboard', '')),
                     JMESPathCheck('resourceGroup', self.kwargs.get('rg', '')),
                     JMESPathCheck(
                         'tags', '{\'aKey\': \'aValue\', \'anotherKey\': \'anotherValue\'}'),
                     JMESPathCheck('lenses', '{\'0\': {\'metadata\': None, \'order\': 0, \'parts\': '
                                   '{\'0\': {\'metadata\': {\'inputs\': [], \'settings\': {}, \'type\': '
                                   '\'Extension/HubsExtension/PartType/ClockPart\'}, \'position\': {\'colSpan\': 2, '
                                   '\'metadata\': None, \'rowSpan\': 2, \'x\': 6, \'y\': 2}}}}}'),
                     JMESPathCheck('metadata', '{\'model\': {\'timeRange\': {\'type\': '
                                   '\'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange\', \'value\': '
                                   '{\'relative\': {\'duration\': 24, \'timeUnit\': 1}}}}}')])

        self.cmd('az portal dashboard list '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheckExists('[?name==\'{}\']'.format(self.kwargs.get('testDashboard', '')))])

        self.cmd('az portal dashboard list '
                 '--resource-group=',
                 checks=[JMESPathCheckExists('[?name==\'{}\']'.format(self.kwargs.get('testDashboard', '')))])

        self.cmd('az portal dashboard update '
                 '--input-path "src/portal/azext_portal/tests/latest/properties-update.json" '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[
                     JMESPathCheck('name', self.kwargs.get(
                         'testDashboard', '')),
                     JMESPathCheck('resourceGroup', self.kwargs.get('rg', '')),
                     JMESPathCheck(
                         'tags', '{\'aKey\': \'aValue\', \'anotherKey\': \'anotherValue\'}'),
                     JMESPathCheck('lenses', '{\'0\': {\'metadata\': None, \'order\': 0, \'parts\': '
                                   '{\'0\': {\'metadata\': {\'inputs\': [], \'settings\': {}, \'type\': '
                                   '\'Extension/HubsExtension/PartType/ClockPart\'}, \'position\': {\'colSpan\': 2, '
                                   '\'metadata\': None, \'rowSpan\': 2, \'x\': 6, \'y\': 2}}}}}'),
                     JMESPathCheck('metadata', '{\'model\': {\'timeRange\': {\'type\': '
                                   '\'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange\', \'value\': '
                                   '{\'relative\': {\'duration\': 12, \'timeUnit\': 1}}}}}')])

        self.cmd('az portal dashboard delete '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}" '
                 '--y',
                 checks=[])

        self.cmd('az portal dashboard list '
                 '--resource-group "{rg}"',
                 checks=[NoneCheck()])

        self.cmd('az portal dashboard import '
                 '--input-path "src/portal/azext_portal/tests/latest/dashboard.json" '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[
                     JMESPathCheck(
                         'name', '7c0464ec-b1cd-4a98-a4a5-1ebe2d980260'),
                     JMESPathCheck('resourceGroup', self.kwargs.get('rg', '')),
                     JMESPathCheck('location', 'eastus'),
                     JMESPathCheck('type', 'Microsoft.Portal/dashboards'),
                     JMESPathCheck(
                         'tags', '{\'hidden-title\': \'test dashboard\'}'),
                     JMESPathCheck('lenses', '{\'0\': {\'metadata\': None, \'order\': 0, \'parts\': '
                                   '{\'0\': {\'metadata\': {\'inputs\': [{\'isOptional\': True, \'name\': '
                                   '\'resourceType\', \'value\': \'Microsoft.Resources/subscriptions/resourcegroups\'},'
                                   ' {\'isOptional\': True, \'name\': \'filter\'}, {\'isOptional\': True, \'name\':'
                                   ' \'scope\'}, {\'isOptional\': True, \'name\': \'kind\'}], \'type\': '
                                   '\'Extension/HubsExtension/PartType/BrowseResourceGroupPinnedPart\'}, \'position\': '
                                   '{\'colSpan\': 6, \'metadata\': None, \'rowSpan\': 4, \'x\': 0, \'y\': 0}}}}}'),
                     JMESPathCheck('metadata', '{\'model\': {\'timeRange\': {\'type\': '
                                   '\'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange\', \'value\': '
                                   '{\'relative\': {\'duration\': 24, \'timeUnit\': 1}}}}}')])
