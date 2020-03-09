# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class AlertsScenarioTest(ScenarioTest):

    @unittest.skip('Smart detector not ready')
    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_alert_rule_')
    def test_alertsmanagement_alert_rule(self, resource_group):
        subscription_id = self.get_subscription_id()

        ag1_id = self.cmd('monitor action-group create -g {rg} -n ag1').get_output_in_json()['id']

        self.kwargs.update({
            'ag1_id': ag1_id,
            'scope': '/subscriptions/{}/resourceGroups/{}'.format(subscription_id, resource_group),
            'detector_id': 'asdf'
        })

        self.cmd('az alertsmanagement smart-detector-alert-rule create '
                 '--resource-group {rg} '
                 '--name "MyAlertRule" '
                 '--description "Sample smart detector alert rule description" '
                 '--state "Enabled" '
                 '--severity "Sev3" '
                 '--frequency "PT5M" '
                 '--detector {detector_id} '
                 '--scope {scope} '
                 '--action-groups {ag1_id}',
                 checks=[])

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_action_rule_')
    def test_alertsmanagement_action_rule(self, resource_group):
        subs_id = self.get_subscription_id()
        rg_id = '/subscriptions/{}/resourceGroups/{}'.format(subs_id, resource_group)
        self.kwargs.update({
            'rg_id': rg_id
        })
        self.cmd('az alertsmanagement action-rule create '
                 '--resource-group {rg} '
                 '--name rule1 '
                 '--location Global '
                 '--status Enabled '
                 '--rule-type Suppression '
                 '--scope-type ResourceGroup '
                 '--scope {rg_id} '
                 '--severity Equals Sev0 Sev2 '
                 '--monitor-service Equals Platform "Application Insights" '
                 '--monitor-condition Equals Fired '
                 '--target-resource-type NotEquals Microsoft.Compute/VirtualMachines '
                 '--recurrence-type Daily '
                 '--start-date 12/09/2018 '
                 '--end-date 12/18/2018 '
                 '--start-time 06:00:00 '
                 '--end-time 14:00:00',
                 checks=[])

        self.cmd('az alertsmanagement action-rule show '
                 '--resource-group {rg} '
                 '--name "rule1"',
                 checks=[
                     self.check('name', 'rule1'),
                     self.check('location', 'Global'),
                     self.check('properties.status', 'Enabled'),
                     self.check('properties.type', 'Suppression'),
                     self.check('properties.conditions.monitorCondition.operator', 'Equals'),
                     self.check('properties.conditions.monitorCondition.values[0]', 'Fired'),
                     self.check('properties.conditions.severity.operator', 'Equals'),
                     self.check('properties.conditions.severity.values[0]', 'Sev0'),
                     self.check('properties.conditions.severity.values[1]', 'Sev2'),
                     self.check('properties.conditions.targetResourceType.operator', 'NotEquals'),
                     self.check('properties.conditions.targetResourceType.values[0]',
                                'Microsoft.Compute/VirtualMachines'),
                     self.check('properties.suppressionConfig.recurrenceType', 'Daily'),
                     self.check('properties.suppressionConfig.schedule.endDate', '12/18/2018'),
                     self.check('properties.suppressionConfig.schedule.endTime', '14:00:00'),
                     self.check('properties.suppressionConfig.schedule.startDate', '12/09/2018'),
                     self.check('properties.suppressionConfig.schedule.startTime', '06:00:00'),
                 ])

        self.cmd('az alertsmanagement action-rule update '
                 '--resource-group {rg} '
                 '--name "rule1" '
                 '--status Disabled',
                 checks=[
                     self.check('properties.status', 'Disabled')
                 ])

        self.cmd('az alertsmanagement action-rule list')

        self.cmd('az alertsmanagement action-rule list -g {rg}')

        self.cmd('az alertsmanagement action-rule delete -g {rg} -n rule1')

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_smart_group_')
    def test_alertsmanagement_smart_group(self, resource_group):
        self.cmd('az alertsmanagement smart-group get-all',
                 checks=[])
        # self.cmd('az alertsmanagement smart-group get-by-id '
        #          '--smart-group-id "603675da-9851-4b26-854a-49fc53d32715"',
        #          checks=[])
        # self.cmd('az alertsmanagement smart-group change-state '
        #          '--smart-group-id "a808445e-bb38-4751-85c2-1b109ccc1059" '
        #          '--new-state "Acknowledged"',
        #          checks=[])
        # self.cmd('az alertsmanagement smart-group get-history '
        #          '--smart-group-id "603675da-9851-4b26-854a-49fc53d32715"',
        #          checks=[])

    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_alert_')
    def test_alertsmanagement_alert(self, resource_group):
        subscription_id = self.get_subscription_id()
        self.kwargs.update({
            'alert_id': '1dde5384-3a40-4616-8a5d-be8e2453595d',
            'alert_full_id': '/subscriptions/{}/providers/Microsoft.AlertsManagement/alerts/1dde5384-3a40-4616-8a5d-be8e2453595d'.format(subscription_id)
        })

        self.cmd('az alertsmanagement alert get-history '
                 '--alert-id {alert_id}',
                 checks=[self.check('properties.alertId', '{alert_id}')])
        self.cmd('az alertsmanagement alert get-by-id '
                 '--alert-id {alert_id}',
                 checks=[self.check('id', '{alert_full_id}')])
        self.cmd('az alertsmanagement alert get-summary --groupby "severity,alertstate"',
                 checks=[])
        self.cmd('az alertsmanagement alert get-all',
                 checks=[])

    # @ResourceGroupPreparer()
    # def test_alertsmanagement(self, resource_group):
    #     self.cmd('az alertsmanagement action-rule create '
    #              '--resource-group {rg} '
    #              '--name "DailySuppression" '
    #              '--location "Global" '
    #              '--status "Enabled"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-detector-alert-rule show '
    #              '--resource-group {rg} '
    #              '--name "MyAlertRule"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement action-rule show '
    #              '--resource-group {rg} '
    #              '--name "DailySuppression"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-detector-alert-rule list '
    #              '--resource-group {rg}',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement action-rule list '
    #              '--resource-group {rg}',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert get-history '
    #              '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-group get-by-id '
    #              '--smart-group-id "603675da-9851-4b26-854a-49fc53d32715"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert get-history '
    #              '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-detector-alert-rule list '
    #              '--resource-group {rg}',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert get-by-id '
    #              '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert get-summary',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-group get-all',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement action-rule list',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert get-all',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert meta-data',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-detector-alert-rule update '
    #              '--resource-group {rg} '
    #              '--name "MyAlertRule" '
    #              '--description "New description for patching" '
    #              '--frequency "PT1M"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement action-rule update '
    #              '--resource-group {rg} '
    #              '--name "WeeklySuppression" '
    #              '--status "Disabled"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-group change-state '
    #              '--smart-group-id "a808445e-bb38-4751-85c2-1b109ccc1059" '
    #              '--new-state "Acknowledged"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement alert get-history '
    #              '--alert-id "66114d64-d9d9-478b-95c9-b789d6502100"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement smart-detector-alert-rule delete '
    #              '--resource-group {rg} '
    #              '--name "MyAlertRule"',
    #              checks=[])
    #
    #     self.cmd('az alertsmanagement action-rule delete '
    #              '--resource-group {rg} '
    #              '--name "DailySuppression"',
    #              checks=[])
