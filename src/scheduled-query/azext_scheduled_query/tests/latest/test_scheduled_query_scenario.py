# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class Scheduled_queryScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_scheduled_query', location='eastus')
    def test_scheduled_query(self, resource_group):
        from azure.mgmt.core.tools import resource_id
        import time
        import mock
        self.kwargs.update({
            'name1': 'sq01',
            'name2': 'sq02',
            'rg': resource_group,
            'vm': 'myvm1',
            'ws': self.create_random_name('clitest', 20)
        })
        with mock.patch('azure.cli.command_modules.vm.custom._gen_guid', side_effect=self.create_guid):
            vm = self.cmd('vm create -n {vm} -g {rg} --image UbuntuLTS --nsg-rule None --workspace {ws} --generate-ssh-keys').get_output_in_json()
        self.kwargs.update({
            'vm_id': vm['id'],
            'rg_id': resource_id(subscription=self.get_subscription_id(),
                                 resource_group=resource_group),
            'sub_id': resource_id(subscription=self.get_subscription_id(),
                                  resource_group=resource_group),
        })
        time.sleep(180)
        self.cmd('monitor scheduled-query create -g {rg} -n {name1} --scopes {vm_id} --condition "count \'union Event, Syslog | where TimeGenerated > ago(1h)\' > 360" --description "Test rule" --target-resource-type Microsoft.Compute/virtualMachines',
                 checks=[
                     self.check('name', '{name1}'),
                     self.check('scopes[0]', '{vm_id}'),
                     self.check('severity', 2),
                     self.check('criteria.allOf[0].query', 'union Event, Syslog | where TimeGenerated > ago(1h)'),
                     self.check('criteria.allOf[0].threshold', 360),
                     self.check('criteria.allOf[0].timeAggregation', 'Count'),
                     self.check('criteria.allOf[0].operator', 'GreaterThan'),
                     self.check('criteria.allOf[0].failingPeriods.minFailingPeriodsToAlert', 1),
                     self.check('criteria.allOf[0].failingPeriods.numberOfEvaluationPeriods', 1)
                 ])
        self.cmd('monitor scheduled-query create -g {rg} -n {name2} --scopes {rg_id} --condition "count \'union Event, Syslog | where TimeGenerated > ago(1h)\' > 360" --description "Test rule" --target-resource-type Microsoft.Compute/virtualMachines',
                 checks=[
                     self.check('name', '{name2}'),
                     self.check('scopes[0]', '{rg_id}'),
                     self.check('severity', 2)
                 ])
        self.cmd('monitor scheduled-query update -g {rg} -n {name1} --condition "count \'union Event | where TimeGenerated > ago(2h)\' < 260 at least 2 out of 3" --description "Test rule 2" --severity 4 --disabled --evaluation-frequency 10m --window-size 10m',
                 checks=[
                     self.check('name', '{name1}'),
                     self.check('scopes[0]', '{vm_id}'),
                     self.check('severity', 4),
                     self.check('windowSize', '0:10:00'),
                     self.check('evaluationFrequency', '0:10:00'),
                     self.check('criteria.allOf[0].query', 'union Event | where TimeGenerated > ago(2h)'),
                     self.check('criteria.allOf[0].threshold', 260),
                     self.check('criteria.allOf[0].timeAggregation', 'Count'),
                     self.check('criteria.allOf[0].operator', 'LessThan'),
                     self.check('criteria.allOf[0].failingPeriods.minFailingPeriodsToAlert', 2),
                     self.check('criteria.allOf[0].failingPeriods.numberOfEvaluationPeriods', 3)
                 ])
        self.cmd('monitor scheduled-query show -g {rg} -n {name1}',
                 checks=[
                     self.check('name', '{name1}')
                 ])
        self.cmd('monitor scheduled-query list -g {rg}',
                 checks=[
                     self.check('length(@)', 2)
                 ])
        self.cmd('monitor scheduled-query list',
                 checks=[
                 ])
        self.cmd('monitor scheduled-query delete -g {rg} -n {name1} -y')
        with self.assertRaisesRegexp(SystemExit, '3'):
            self.cmd('monitor scheduled-query show -g {rg} -n {name1}')


class ScheduledQueryCondtionTest(unittest.TestCase):

    def _build_namespace(self, name_or_id=None, resource_group=None, provider_namespace=None, parent=None,
                         resource_type=None):
        from argparse import Namespace
        return Namespace()

    def call_condition(self, ns, value):
        from azext_scheduled_query._actions import ScheduleQueryConditionAction
        ScheduleQueryConditionAction('--condition', 'condition').__call__(None, ns, value.split(), '--condition')

    def check_condition(self, ns, time_aggregation, query, operator, threshold, metric_measure_column=None, resource_id_column=None):
        prop = ns.condition[0]
        self.assertEqual(prop.time_aggregation, time_aggregation)
        self.assertEqual(prop.query, query)
        self.assertEqual(prop.operator, operator)
        self.assertEqual(prop.threshold, threshold)
        if metric_measure_column:
            self.assertEqual(prop.metric_measure_column, metric_measure_column)
        if resource_id_column:
            self.assertEqual(prop.resource_id_column, resource_id_column)

    def check_dimension(self, ns, index, name, operator, values):
        dim = ns.condition[0].dimensions[index]
        self.assertEqual(dim.name, name)
        self.assertEqual(dim.operator, operator)
        self.assertEqual(dim.values, values)

    def check_falling_period(self, ns, min_failing_periods_to_alert, number_of_evaluation_periods):
        falling_period = ns.condition[0].failing_periods
        self.assertEqual(falling_period.min_failing_periods_to_alert, min_failing_periods_to_alert)
        self.assertEqual(falling_period.number_of_evaluation_periods, number_of_evaluation_periods)

    def test_monitor_scheduled_query_condition_action(self):

        from knack.util import CLIError

        ns = self._build_namespace()
        self.call_condition(ns, 'avg "Perf" > 90')
        self.check_condition(ns, 'Average', 'Perf', 'GreaterThan', '90')

        ns = self._build_namespace()
        self.call_condition(ns, 'avg "% Processor Time" from "Perf | where ObjectName == \\\"Processor\\\"" > 70 resource id resourceId')
        self.check_condition(ns, 'Average', 'Perf | where ObjectName == \\\"Processor\\\"', 'GreaterThan', '70', '% Processor Time', 'resourceId')

        ns = self._build_namespace()
        self.call_condition(ns, 'avg "% Processor Time" from "Perf | where ObjectName == \\\"Processor\\\" and C>=D && E<<F" > 70 resource id resourceId where ApiName includes GetBlob or PutBlob and DpiName excludes CCC at least 1.1 out of 10.1')
        self.check_condition(ns, 'Average', 'Perf | where ObjectName == \\\"Processor\\\" and C>=D && E<<F', 'GreaterThan', '70', '% Processor Time', 'resourceId')
        self.check_dimension(ns, 0, 'ApiName', 'Include', ['GetBlob', 'PutBlob'])
        self.check_dimension(ns, 1, 'DpiName', 'Exclude', ['CCC'])
        self.check_falling_period(ns, 1.1, 10.1)

        ns = self._build_namespace()
        self.call_condition(ns, 'avg "% Processor Time" from "Perf and C>=D && E<<F" > 70 resource id resourceId where ApiName includes GetBlob or PutBlob and DpiName excludes CCC at least 1.1 out of 10.1')
        self.check_condition(ns, 'Average', 'Perf and C>=D && E<<F', 'GreaterThan', '70', '% Processor Time', 'resourceId')
        self.check_dimension(ns, 0, 'ApiName', 'Include', ['GetBlob', 'PutBlob'])
        self.check_dimension(ns, 1, 'DpiName', 'Exclude', ['CCC'])
        self.check_falling_period(ns, 1.1, 10.1)
