# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

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
            'testDashboard': self.create_random_name(prefix='cli-test-dashboards'[:9], length=24),
            'inputPath': os.path.join(TEST_DIR, 'properties.json')
        })

        self.cmd('az portal dashboard create '
                 '--location "eastus" '
                 '--input-path "{inputPath}" '
                 '--tags aKey=aValue anotherKey=anotherValue '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheck('name', self.kwargs.get('testDashboard', ''))])

        self.cmd('az portal dashboard show '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[
                     JMESPathCheck('name', self.kwargs.get('testDashboard', '')),
                     JMESPathCheck('resourceGroup', self.kwargs.get('rg', '')),
                     JMESPathCheck('tags', '{\'aKey\': \'aValue\', \'anotherKey\': \'anotherValue\'}'),
                     JMESPathCheck('properties.lenses[0]',
                                   '{\'order\': 0, \'parts\': [{\'metadata\': {\'inputs\': [], \'settings\': {}, '
                                   '\'type\': \'Extension/HubsExtension/PartType/MarkdownPart\'}, '
                                   '\'position\': {\'colSpan\': 5, \'rowSpan\': 3, \'x\': 0, \'y\': 0}}]}'),
                     JMESPathCheck('properties.metadata',
                                   '{\'model\': {\'timeRange\': {\'type\': \'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange\', '
                                   '\'value\': {\'relative\': {\'duration\': 24, \'timeUnit\': 1}}}}}')])

        self.cmd('az portal dashboard list '
                 '--resource-group "{rg}"',
                 checks=[JMESPathCheckExists('[?name==\'{}\']'.format(self.kwargs.get('testDashboard', '')))])

        self.kwargs.update({
            'inputPath': os.path.join(TEST_DIR, 'properties-update.json')
        })

        self.cmd('az portal dashboard update '
                 '--input-path "{inputPath}" '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[
                     JMESPathCheck('name', self.kwargs.get(
                         'testDashboard', '')),
                     JMESPathCheck('resourceGroup', self.kwargs.get('rg', '')),
                     JMESPathCheck(
                         'tags', '{\'aKey\': \'aValue\', \'anotherKey\': \'anotherValue\'}'),
                     JMESPathCheck('properties.lenses[0]',
                                   '{\'order\': 0, \'parts\': [{\'metadata\': {\'inputs\': [], \'settings\': {}, '
                                   '\'type\': \'Extension/HubsExtension/PartType/MarkdownPart\'}, '
                                   '\'position\': {\'colSpan\': 5, \'rowSpan\': 5, \'x\': 0, \'y\': 0}}]}'),
                     JMESPathCheck('properties.metadata',
                                   '{\'model\': {\'timeRange\': {\'type\': \'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange\', '
                                   '\'value\': {\'relative\': {\'duration\': 12, \'timeUnit\': 1}}}}}')])

        self.cmd('az portal dashboard delete '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}" '
                 '--y',
                 checks=[])

        self.cmd('az portal dashboard list '
                 '--resource-group "{rg}"',
                 checks=[NoneCheck()])

        self.kwargs.update({
            'inputPath': os.path.join(TEST_DIR, 'dashboard.json')
        })

        self.cmd('az portal dashboard import '
                 '--input-path "{inputPath}" '
                 '--name "{testDashboard}" '
                 '--resource-group "{rg}"',
                 checks=[
                     JMESPathCheck('name', self.kwargs.get('testDashboard', '')),
                     JMESPathCheck('resourceGroup', self.kwargs.get('rg', '')),
                     JMESPathCheck('properties.lenses[0]',
                                   '{\'order\': 0, \'parts\': [{\'metadata\': {\'inputs\': [], \'settings\': {}, '
                                   '\'type\': \'Extension/HubsExtension/PartType/MarkdownPart\'}, '
                                   '\'position\': {\'colSpan\': 5, \'rowSpan\': 3, \'x\': 0, \'y\': 0}}]}'),
                     JMESPathCheck('properties.metadata',
                                   '{\'model\': {\'timeRange\': {\'type\': \'MsPortalFx.Composition.Configuration.ValueTypes.TimeRange\', '
                                   '\'value\': {\'relative\': {\'duration\': 24, \'timeUnit\': 1}}}}}')])
