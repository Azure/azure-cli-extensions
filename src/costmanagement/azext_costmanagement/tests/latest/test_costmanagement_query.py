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
