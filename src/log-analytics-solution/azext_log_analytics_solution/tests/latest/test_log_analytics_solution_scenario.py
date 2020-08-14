# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from knack.util import CLIError


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class OperationsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(parameter_name='resource_group_1')
    @ResourceGroupPreparer(parameter_name='resource_group_2')
    @ResourceGroupPreparer(parameter_name_for_location='location')
    def test_log_analytics_solution(self, resource_group_1, resource_group_2, location):

        self.kwargs.update({
            'loc': location,
            'workspace_name': self.create_random_name('workspace', 20),
            'rg': resource_group_1,
            'rg2': resource_group_2,
            'sub': self.get_subscription_id(),
            'la_prop_path': os.path.join(TEST_DIR, 'log_analytics.json')
        })
        self.kwargs['solution_type'] = 'Containers'
        self.kwargs['solution_name'] = self.kwargs['solution_type'] + '(' + self.kwargs['workspace_name'] + ')'

        workspace = self.cmd('resource create -g {rg} -n {workspace_name} -l {loc} --resource-type '
                             'Microsoft.OperationalInsights/workspaces -p @"{la_prop_path}"').get_output_in_json()
        self.kwargs.update({
            'workspace_resource_id': workspace['id'],
            'wrong_workspace_resource_id': workspace['id'][1:]
        })

        with self.assertRaises(CLIError) as err:
            self.cmd('az monitor log-analytics solution create '
                     '--resource-group {rg} '
                     '--solution-type {solution_type} '
                     '--workspace "{wrong_workspace_resource_id}" ')
            self.assertTrue("usage error: --workspace is invalid" == err.exception)

        with self.assertRaises(CLIError) as err:
            self.cmd('az monitor log-analytics solution create '
                     '--resource-group {rg2} '
                     '--solution-type {solution_type} '
                     '--workspace "{workspace_resource_id}" ')
            self.assertTrue("usage error: workspace and solution must be under the same resource group" == err.exception)

        self.cmd('az monitor log-analytics solution create '
                 '--resource-group {rg} '
                 '--solution-type {solution_type} '
                 '--workspace "{workspace_resource_id}" '
                 '--tags key1=value1',
                 checks=[self.check('name', '{solution_name}')])

        self.cmd('az monitor log-analytics solution show --resource-group {rg} --name {solution_name}',
                 checks=[self.check('name', '{solution_name}'),
                         self.check('plan.publisher', 'Microsoft'),
                         self.check('plan.product', 'OMSGallery/Containers'),
                         self.check('tags', {'key1': 'value1'})])

        self.cmd('az monitor log-analytics solution update --resource-group {rg} --name {solution_name} '
                 '--tags key2=value2',
                 checks=[self.check('name', '{solution_name}'),
                         self.check('tags', {'key2': 'value2'})])

        self.cmd('az monitor log-analytics solution show --resource-group {rg} --name {solution_name}',
                 checks=[self.check('name', '{solution_name}'),
                         self.check('plan.publisher', 'Microsoft'),
                         self.check('plan.product', 'OMSGallery/Containers'),
                         self.check('tags', {'key2': 'value2'})])

        self.kwargs['workspace_name2'] = self.create_random_name('workspace', 20)
        self.cmd('resource create -g {rg2} -n {workspace_name2} -l {loc} --resource-type '
                 'Microsoft.OperationalInsights/workspaces -p @"{la_prop_path}"').get_output_in_json()
        self.kwargs['solution_name2'] = 'Containers(' + self.kwargs['workspace_name2'] + ')'

        self.cmd('az monitor log-analytics solution create '
                 '--resource-group {rg2} '
                 '-t {solution_type} '
                 '--workspace "{workspace_name2}" '
                 '--tags key3=value3',
                 checks=[self.check('name', '{solution_name2}')])

        self.cmd('az monitor log-analytics solution list --query "value[?name==\'{solution_name}\']"',
                 checks=[self.check('length([])', 1)])

        self.cmd('az monitor log-analytics solution list --resource-group {rg2} '
                 '--query "value[?name==\'{solution_name2}\']" ',
                 checks=[self.check('length([])', 1)])

        self.cmd('az monitor log-analytics solution delete --resource-group {rg} --name {solution_name} -y',
                 checks=[])

        self.cmd('az monitor log-analytics solution delete --resource-group {rg2} --name {solution_name2} -y',
                 checks=[])

        self.cmd('az resource delete -g {rg} -n {workspace_name} --resource-type '
                 'Microsoft.OperationalInsights/workspaces', checks=[])

        self.cmd('az resource delete -g {rg2} -n {workspace_name2} --resource-type '
                 'Microsoft.OperationalInsights/workspaces', checks=[])

        self.cmd('az monitor log-analytics solution list --query "value[?name==\'{solution_name}\']"',
                 checks=[self.check('length([])', 0)])

        self.cmd('az monitor log-analytics solution list --resource-group {rg2} '
                 '--query "value[?name==\'{solution_name2}\']" ',
                 checks=[self.check('length([])', 0)])
