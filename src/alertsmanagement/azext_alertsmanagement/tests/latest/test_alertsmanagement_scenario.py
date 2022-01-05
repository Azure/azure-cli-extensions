# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AlertsScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_processing_rule_')
    def test_alertsmanagement_processing_rule(self, resource_group):
        subs_id = self.get_subscription_id()
        rg_id = '/subscriptions/{}/resourceGroups/{}'.format(subs_id, resource_group)
        self.kwargs.update({
            'rg_id': rg_id
        })
        self.cmd('az monitor alert-processing-rule create '
                 '--resource-group {rg} '
                 '--name test1 '
                 '--rule-type RemoveAllActionGroups '
                 '--scopes {rg_id} '
                 '--filter-severity Equals Sev0 Sev2 '
                 '--filter-monitor-service Equals Platform "Application Insights" '
                 '--filter-monitor-condition Equals Fired '
                 '--filter-resource-type NotEquals Microsoft.Compute/VirtualMachines '
                 '--schedule-recurrence-type Daily '
                 '--schedule-start-datetime \'2018-12-09 06:00:00\' '
                 '--schedule-end-datetime \'2018-12-18 14:00:00\' '
                 '--schedule-recurrence-start-time \'06:00:00\' '
                 '--schedule-recurrence-end-time \'14:00:00\' ',
                 checks=[
                     self.check('name', 'test1')
                 ])

        self.cmd('az monitor alert-processing-rule show '
                 '--resource-group {rg} '
                 '--name "test1"',
                 checks=[
                     self.check('name', 'test1'),
                     self.check('properties.actions[0].actionType', 'RemoveAllActionGroups'),
                     self.check('properties.conditions[3].field','TargetResourceType'),
                     self.check('properties.conditions[3].operator','NotEquals'),
                     self.check('properties.conditions[3].values[0]','Microsoft.Compute/VirtualMachines')
                 ])

        self.cmd('az monitor alert-processing-rule create '
                 '--resource-group {rg} '
                 '--name test2 '
                 '--scopes {rg_id} '
                 '--rule-type AddActionGroups '
                 '--action-groups "/subscriptions/dd91de05-d791-4ceb-b6dc-988682dc7d72/resourcegroups/amp-common/providers/microsoft.insights/actiongroups/application insights smart detection" '
                 '--schedule-recurrence-type Weekly '
                 '--schedule-recurrence Sunday Saturday '
                 '--schedule-start-datetime \'2018-12-09 06:00:00\' '
                 '--schedule-end-datetime \'2018-12-18 14:00:00\' ',
                 checks=[
                     self.check('name', 'test2'),
                     self.check('properties.schedule.recurrences[0].daysOfWeek[0]', 'Sunday'),
                     self.check('properties.schedule.recurrences[0].daysOfWeek[1]', 'Saturday')
                 ])

        self.cmd('az monitor alert-processing-rule show '
                 '--resource-group {rg} '
                 '--name "test2"',
                 checks=[
                     self.check('name', 'test2'),
                     self.check('properties.enabled', True),
                     self.check('properties.actions[0].actionType', 'AddActionGroups'),
                     self.check('properties.schedule.effectiveFrom', '2018-12-09T06:00:00'),
                     self.check('properties.schedule.effectiveUntil', '2018-12-18T14:00:00')
                 ])

        self.cmd('az monitor alert-processing-rule update '
                 '--resource-group {rg} '
                 '--name test1 '
                 '--enabled False '
                 '--tags isUpdated=YES secondTag=justATag',
                 checks=[
                     self.check('properties.enabled', False),
                     self.check('tags.isUpdated', 'YES')
                 ])

        self.cmd('az monitor alert-processing-rule list -g {rg}',
                 checks=self.check('[0].name', 'test1'))

        self.cmd('az monitor alert-processing-rule delete -g {rg} -n test1')
        self.cmd('az monitor alert-processing-rule delete -g {rg} -n test2')
