# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


class CostManagementQueryTest(ScenarioTest):
    """
    Those command results may be different every time after you run if running in live mode,
    because of the billing is changing as we are creating and deleting resources under this subscription.
    """

    @ResourceGroupPreparer(name_prefix='test_query_without_dataset_')
    def test_cm_query_in_subscription_scope(self, resource_group):

        usage_types = ['ActualCost', 'AmortizedCost', 'Usage']
        timeframes = ['BillingMonthToDate', 'MonthToDate', 'TheLastBillingMonth',
                      'TheLastMonth', 'WeekToDate']

        for usage_type in usage_types:
            for timeframe in timeframes:
                self.kwargs.update({
                    'usgae_type': usage_type,
                    'timeframe': timeframe,
                    'scope': '/subscriptions/{}'.format(self.get_subscription_id())
                })

                cost_data = self.cmd('costmanagement query --type {usgae_type} --timeframe {timeframe} --scope {scope}').get_output_in_json()

                self.assertEqual(cost_data['type'], 'Microsoft.CostManagement/query')

                # assert data columns, by default, there is no actual cost data but 2 columns "UsageDate" and "Currency"
                self.assertEqual(len(cost_data['columns']), 2)
                self.assertEqual(cost_data['columns'][0]['name'], 'UsageDate')
                self.assertEqual(cost_data['columns'][0]['type'], 'Number')
                self.assertEqual(cost_data['columns'][1]['name'], "Currency")
                self.assertEqual(cost_data['columns'][1]['type'], 'String')

    @ResourceGroupPreparer(name_prefix='test_data_aggregation_in_subscription_scope')
    def test_data_aggregation_in_subscription_scope(self, resource_group):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        usage_type = 'ActualCost'
        timeframe = 'TheLastMonth'
        aggregation_expression = '\'{"totalCost": {"name": "PreTaxCost", "function": "Sum"}}\''

        self.kwargs.update({
            'usage_type': usage_type,
            'timeframe': timeframe,
            'aggregation_expression': aggregation_expression
        })

        cost_data = self.cmd('costmanagement query '
                             '--type {usage_type} '
                             '--timeframe {timeframe} '
                             '--scope {scope} '
                             '--dataset-aggregation {aggregation_expression}').get_output_in_json()

        self.assertEqual(cost_data['type'], 'Microsoft.CostManagement/query')

        self.assertEqual(len(cost_data['columns']), 3)
        self.assertEqual(cost_data['columns'][0]['name'], 'PreTaxCost')
        self.assertEqual(cost_data['columns'][0]['type'], 'Number')

        self.assertEqual(len(cost_data['rows']), 30)

    @ResourceGroupPreparer(name_prefix='test_cm_query_in_subscription_scope_custome_timeframe')
    def test_data_aggregation_in_subscription_scope_custome_timeframe(self, resource_group):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        timeframe = 'Custom'
        aggregation_expression = '\'{"totalCost": {"name": "PreTaxCost", "function": "Sum"}}\''
        time_period = 'from=2020-03-01T00:00:00 to=2020-05-09T00:00:00 '

        self.kwargs.update({
            'usgae_type': 'ActualCost',
            'timeframe': timeframe,
            'time_period': time_period,
            'aggregation_expression': aggregation_expression
        })

        cost_data = self.cmd('costmanagement query '
                             '--type {usgae_type} '
                             '--timeframe {timeframe} '
                             '--time-period {time_period} '
                             '--scope {scope} '
                             '--dataset-aggregation {aggregation_expression}').get_output_in_json()

        self.assertEqual(cost_data['type'], 'Microsoft.CostManagement/query')

        self.assertEqual(len(cost_data['columns']), 3)
        self.assertEqual(cost_data['columns'][0]['name'], 'PreTaxCost')
        self.assertEqual(cost_data['columns'][0]['type'], 'Number')

        self.assertEqual(len(cost_data['rows']), 70)
        self.assertEqual(cost_data['rows'][0], [186.758302, 20200301, 'USD'])

    @ResourceGroupPreparer(name_prefix='test_data_filter_in_subscription_scopde')
    def test_data_grouping_in_subscription_scopde(self, resource_group):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        usage_type = 'ActualCost'
        timeframe = 'TheLastMonth'
        aggregation_expression = '\'{"totalCost": {"name": "PreTaxCost", "function": "Sum"}}\''
        dataset_grouping = 'name="ResourceGroup" type="Dimension"'

        self.kwargs.update({
            'usage_type': usage_type,
            'timeframe': timeframe,
            'aggregation_expression': aggregation_expression,
            'dataset_grouping': dataset_grouping
        })

        cost_data = self.cmd('costmanagement query '
                             '--type {usage_type} '
                             '--timeframe {timeframe} '
                             '--scope {scope} '
                             '--dataset-aggregation {aggregation_expression} '
                             '--dataset-grouping {dataset_grouping}').get_output_in_json()

        self.assertEqual(cost_data['type'], 'Microsoft.CostManagement/query')

        self.assertEqual(len(cost_data['columns']), 4)
        self.assertEqual(cost_data['columns'][0]['name'], 'PreTaxCost')
        self.assertEqual(cost_data['columns'][0]['type'], 'Number')
        self.assertEqual(cost_data['columns'][2]['name'], 'ResourceGroup')
        self.assertEqual(cost_data['columns'][2]['type'], 'String')

        self.assertEqual(len(cost_data['rows']), 1000)
