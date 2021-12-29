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

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_action_rule_')
    def test_alertsmanagement_action_rule(self, resource_group):
        subs_id = self.get_subscription_id()
        rg_id = '/subscriptions/{}/resourceGroups/{}'.format(subs_id, resource_group)
        self.kwargs.update({
            'rg_id': rg_id
        })
        # self.cmd('az monitor action-rule create '
        #          '--resource-group {rg} '
        #          '--name rule1 '
        #          '--location Global '
        #          '--status Enabled '
        #          '--rule-type Suppression '
        #          '--scope-type ResourceGroup '
        #          '--scope {rg_id} '
        #          '--severity Equals Sev0 Sev2 '
        #          '--monitor-service Equals Platform "Application Insights" '
        #          '--monitor-condition Equals Fired '
        #          '--target-resource-type NotEquals Microsoft.Compute/VirtualMachines '
        #          '--suppression-recurrence-type Daily '
        #          '--suppression-start-date 12/09/2018 '
        #          '--suppression-end-date 12/18/2018 '
        #          '--suppression-start-time 06:00:00 '
        #          '--suppression-end-time 14:00:00',
        #          checks=[])

        self.cmd('az monitor action-rule show '
                 '--resource-group {rg} '
                 '--name "test1"',
                 checks=[
                     self.check('name', 'test1'),
                     self.check('location', 'Global')
                 ])

        # self.cmd('az monitor action-rule create '
        #          '--resource-group {rg} '
        #          '--name rule2 '
        #          '--location Global '
        #          '--status Enabled '
        #          '--rule-type Suppression '
        #          '--scope-type ResourceGroup '
        #          '--scope {rg_id} '
        #          '--severity Equals Sev0 Sev2 '
        #          '--monitor-service Equals Platform "Application Insights" '
        #          '--monitor-condition Equals Fired '
        #          '--target-resource-type NotEquals Microsoft.Compute/VirtualMachines '
        #          '--suppression-recurrence-type Once '
        #          '--suppression-start-date 08/25/2021 '
        #          '--suppression-end-date 08/26/2021 '
        #          '--suppression-start-time 06:00:00 '
        #          '--suppression-end-time 14:00:00',
        #          checks=[])

        # self.cmd('az monitor action-rule show '
        #          '--resource-group {rg} '
        #          '--name "rule2"',
        #          checks=[
        #              self.check('name', 'rule2'),
        #              self.check('location', 'Global'),
        #              self.check('properties.status', 'Enabled'),
        #              self.check('properties.type', 'Suppression'),
        #              self.check('properties.conditions.monitorCondition.operator', 'Equals'),
        #              self.check('properties.conditions.monitorCondition.values[0]', 'Fired'),
        #              self.check('properties.conditions.severity.operator', 'Equals'),
        #              self.check('properties.conditions.severity.values[0]', 'Sev0'),
        #              self.check('properties.conditions.severity.values[1]', 'Sev2'),
        #              self.check('properties.conditions.targetResourceType.operator', 'NotEquals'),
        #              self.check('properties.conditions.targetResourceType.values[0]',
        #                         'Microsoft.Compute/VirtualMachines'),
        #              self.check('properties.suppressionConfig.recurrenceType', 'Once'),
        #              self.check('properties.suppressionConfig.schedule.endDate', '08/26/2021'),
        #              self.check('properties.suppressionConfig.schedule.endTime', '14:00:00'),
        #              self.check('properties.suppressionConfig.schedule.startDate', '08/25/2021'),
        #              self.check('properties.suppressionConfig.schedule.startTime', '06:00:00'),
        #          ])

        # self.cmd('az monitor action-rule update '
        #          '--resource-group {rg} '
        #          '--name "rule1" '
        #          '--status Disabled',
        #          checks=[
        #              self.check('properties.status', 'Disabled')
        #          ])

        # self.cmd('az monitor action-rule list',
        #          checks=self.check('[0].name', 'rule1'))

        # self.cmd('az monitor action-rule list -g {rg}',
        #          checks=self.check('[0].name', 'rule1'))

        # self.cmd('az monitor action-rule delete -g {rg} -n rule1')
        # self.cmd('az monitor action-rule delete -g {rg} -n rule2')
