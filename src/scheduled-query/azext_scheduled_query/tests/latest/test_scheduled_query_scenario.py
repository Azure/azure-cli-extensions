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

    @ResourceGroupPreparer(name_prefix='cli_test_scheduled_query')
    def test_scheduled_query(self, resource_group):

        self.kwargs.update({
            'name': 'test1'
        })

        self.cmd('scheduled_query create -g {rg} -n {name} --tags foo=doo', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('scheduled_query update -g {rg} -n {name} --tags foo=boo', checks=[
            self.check('tags.foo', 'boo')
        ])
        count = len(self.cmd('scheduled_query list').get_output_in_json())
        self.cmd('scheduled_query show - {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'boo')
        ])
        self.cmd('scheduled_query delete -g {rg} -n {name}')
        final_count = len(self.cmd('scheduled_query list').get_output_in_json())
        self.assertTrue(final_count, count - 1)

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