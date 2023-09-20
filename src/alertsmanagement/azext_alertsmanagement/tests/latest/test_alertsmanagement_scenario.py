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
            'rg_id': rg_id,
            'subs_id': subs_id
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
                 '--action-groups "/subscriptions/{subs_id}/resourcegroups/amp-common/providers/microsoft.insights/actiongroups/application insights smart detection" '
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

        self.cmd('az monitor alert-processing-rule delete -g {rg} -n test1 --yes')
        self.cmd('az monitor alert-processing-rule delete -g {rg} -n test2 --yes')


class PrometheusRuleGroup(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_alertsmanagement_prometheus_rule_group_', location='eastus')
    def test_alertsmanagement_prometheus_rule_group(self, resource_group):
        subs_id = self.get_subscription_id()
        rg_id = '/subscriptions/{}/resourceGroups/{}'.format(subs_id, resource_group)
        self.kwargs.update({
            'rg_id': rg_id,
            'subs_id': subs_id,
            'loc': 'eastus2euap',
            'name': self.create_random_name('prometheus-rule-group', 28),
            'action_group_name1': self.create_random_name('action-group-name', 24),
            'action_group_name2': self.create_random_name('action-group-name', 24),
            'account_name': self.create_random_name('account-name', 24),
            'description': 'This is the description of the following rule group',
            'interval': 'PT10M',
            'expression': "histogram_quantile(0.99, sum(rate(jobs_duration_seconds_bucket{service=\"billing-processing\"}[5m])) by (job_type))",
            'body': '{\\"location\\":\\"eastus2euap\\"}',
        })
        actionGroup1 = self.cmd('az monitor action-group create -n {action_group_name1} -g {rg}').get_output_in_json()
        actionGroup2 = self.cmd('az monitor action-group create -n {action_group_name2} -g {rg}').get_output_in_json()
        macAccount = self.cmd('az rest --method "PUT" \
                        --url "https://management.azure.com/subscriptions/{subs_id}/resourcegroups/{rg}/providers/Microsoft.Monitor/accounts/{account_name}?api-version=2021-06-03-preview" \
                        --body "{body}"').get_output_in_json()
        self.kwargs['account_id'] = macAccount['id']
        self.kwargs['action_group_id01'] = actionGroup1['id']
        self.kwargs['action_group_id02'] = actionGroup2['id']
        self.cmd('az alerts-management prometheus-rule-group create -n {name} -g {rg} -l {loc} --enabled '
                 '--description test '
                 '--interval {interval} '
                 '--scopes {account_id} '
                 '--rules [{{"record":"test","expression":"test","labels":{{"team":"prod"}}}},'
                 '{{"alert":"Billing_Processing_Very_Slow","expression":"test","enabled":"true","severity":2,'
                 '"for":"PT5M","labels":{{"team":"prod"}},"annotations":{{"annotationName1":"annotationValue1"}},'
                 '"resolveConfiguration":{{"autoResolved":"true","timeToResolve":"PT10M"}},'
                 '"actions":[{{"actionGroupId":{action_group_id01},"actionProperties":{{"key11":"value11","key12":"value12"}}}},'
                 '{{"actionGroupId":{action_group_id02},"actionProperties":{{"key21":"value21","key22":"value22"}}}}]}}]',
                 checks=self.check('name', '{name}'))

        self.cmd('az alerts-management prometheus-rule-group update -n {name} -g {rg} --tags key=value',
                 checks=[
                     self.check('name', '{name}'),
                     self.check('tags.key', 'value')
                 ])

        self.cmd('az alerts-management prometheus-rule-group list -g {rg}',
                 checks=self.check('length(@)', 1))

        self.cmd('az alerts-management prometheus-rule-group show -n {name} -g {rg}',
                 checks=self.check('name', '{name}'))

        self.cmd('az alerts-management prometheus-rule-group delete -n {name} -g {rg}')
