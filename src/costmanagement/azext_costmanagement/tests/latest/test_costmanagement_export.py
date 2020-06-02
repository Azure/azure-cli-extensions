# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer, StorageAccountPreparer


class CostManagementExportTest(ScenarioTest):
    """
    Those command results may be different every time after you run if running in live mode,
    because of the cost is changing as we are creating and deleting resources under this subscription.
    """

    @ResourceGroupPreparer(name_prefix='test_export_create')
    @StorageAccountPreparer(name_prefix='test_export_create'.replace('_', ''))
    def test_export_create_in_subscription_scope(self, resource_group, storage_account):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        export_name = 'ep-01'
        storage_container = 'export'
        timeframe = 'TheLastMonth'
        storage_account_id = '/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account_name}'.format(
            sub=self.get_subscription_id(),
            rg=resource_group,
            account_name=storage_account
        )

        self.kwargs.update({
            'export_name': export_name,
            'storage_account_id': storage_account_id,
            'storage_container': storage_container,
            'timeframe': timeframe
        })

        creation_data = self.cmd('costmanagement export create '
                                 '--scope {scope} '
                                 '--name {export_name} '
                                 '--storage-account-id {storage_account_id} '
                                 '--storage-container {storage_container} '
                                 '--timeframe {timeframe} ').get_output_in_json()
        self._test_export_create_in_subscription_scope_assertions(creation_data,
                                                                  export_name,
                                                                  storage_container,
                                                                  storage_account_id,
                                                                  timeframe)

        # show an export
        show_data = self.cmd('costmanagement export show --scope {scope} --name {export_name}').get_output_in_json()
        self._test_export_create_in_subscription_scope_assertions(show_data,
                                                                  export_name,
                                                                  storage_container,
                                                                  storage_account_id,
                                                                  timeframe)

        # list exports
        list_data = self.cmd('costmanagement export list --scope {scope}').get_output_in_json()
        self.assertEqual(len(list_data), 1)
        self._test_export_create_in_subscription_scope_assertions(list_data[0],
                                                                  export_name,
                                                                  storage_container,
                                                                  storage_account_id,
                                                                  timeframe)

        self.cmd('costmanagement export delete -y --scope {scope} --name {export_name}')

        with self.assertRaisesRegex(SystemExit, '3'):
            self.cmd('costmanagement export show --scope {scope} --name {export_name}')

    def _test_export_create_in_subscription_scope_assertions(self, data, export_name, storage_container, storage_account_id, timeframe):
        self.assertEqual(data['name'], export_name)
        self.assertIsNone(data['aggregation'], None)
        self.assertIsNone(data['configuration'], None)
        self.assertDictEqual(data['destination'], {
            'container': storage_container,
            'resourceId': storage_account_id,
            'rootFolderPath': None
        })
        self.assertEqual(data['typePropertiesDefinitionType'], 'Usage')
        self.assertIsNone(data['recurrence'])
        self.assertIsNone(data['recurrencePeriod'])
        self.assertEqual(data['status'], 'Inactive')
        self.assertIsNone(data['timePeriod'])
        self.assertEqual(data['timeframe'], timeframe)

    @ResourceGroupPreparer(name_prefix='test_export_schedule')
    @StorageAccountPreparer(name_prefix='test_export_schedule'.replace('_', ''))
    def test_export_create_with_schedule_in_subscription_scope(self, resource_group, storage_account):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        export_name = 'ep-02'
        storage_container = 'export'
        timeframe = 'TheLastMonth'
        storage_account_id = '/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account_name}'.format(
            sub=self.get_subscription_id(),
            rg=resource_group,
            account_name=storage_account
        )

        self.kwargs.update({
            'export_name': export_name,
            'storage_account_id': storage_account_id,
            'storage_container': storage_container,
            'timeframe': timeframe
        })

        creation_data = self.cmd('costmanagement export create '
                                 '--scope {scope} '
                                 '--name {export_name} '
                                 '--storage-account-id {storage_account_id} '
                                 '--storage-container {storage_container} '
                                 '--timeframe {timeframe} '
                                 '--recurrence "Weekly" '
                                 '--recurrence-period from="2020-06-01T00:00:00Z" to="2020-10-31T00:00:00Z" '
                                 '--schedule-status Active').get_output_in_json()
        self._test_export_create_with_schedule_in_subscription_scope_assertions(creation_data,
                                                                                export_name,
                                                                                storage_container,
                                                                                storage_account_id,
                                                                                timeframe)

        # show an export
        show_data = self.cmd('costmanagement export show --scope {scope} --name {export_name}').get_output_in_json()
        self._test_export_create_with_schedule_in_subscription_scope_assertions(show_data,
                                                                                export_name,
                                                                                storage_container,
                                                                                storage_account_id,
                                                                                timeframe)

        # list exports
        list_data = self.cmd('costmanagement export list --scope {scope}').get_output_in_json()
        self.assertEqual(len(list_data), 1)
        self._test_export_create_with_schedule_in_subscription_scope_assertions(list_data[0],
                                                                                export_name,
                                                                                storage_container,
                                                                                storage_account_id,
                                                                                timeframe)

        self.cmd('costmanagement export delete -y --scope {scope} --name {export_name}')

        with self.assertRaisesRegex(SystemExit, '3'):
            self.cmd('costmanagement export show --scope {scope} --name {export_name}')

    def _test_export_create_with_schedule_in_subscription_scope_assertions(self, data, export_name, storage_container, storage_account_id, timeframe):
        self.assertEqual(data['name'], export_name)
        self.assertIsNone(data['aggregation'], None)
        self.assertIsNone(data['configuration'], None)
        self.assertDictEqual(data['destination'], {
            'container': storage_container,
            'resourceId': storage_account_id,
            'rootFolderPath': None
        })
        self.assertEqual(data['typePropertiesDefinitionType'], 'Usage')    # default is Usage
        self.assertEqual(data['recurrence'], 'Weekly')
        self.assertDictEqual(data['recurrencePeriod'], {
            "fromProperty": "2020-06-01T00:00:00+00:00",
            "to": "2020-10-31T00:00:00+00:00"
        })
        self.assertEqual(data['status'], 'Active')
        self.assertIsNone(data['timePeriod'])
        self.assertEqual(data['timeframe'], timeframe)

    @ResourceGroupPreparer(name_prefix='test_update_schedule')
    @StorageAccountPreparer(name_prefix='test_update_schedule'.replace('_', ''))
    def test_update_with_timeperiod_in_subscription_scope(self, resource_group, storage_account):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        export_name = 'ep-03'
        storage_container = 'export'
        timeframe = 'TheLastMonth'
        storage_account_id = '/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account_name}'.format(
            sub=self.get_subscription_id(),
            rg=resource_group,
            account_name=storage_account
        )

        self.kwargs.update({
            'export_name': export_name,
            'storage_account_id': storage_account_id,
            'storage_container': storage_container,
            'timeframe': timeframe,
            'time_period': 'from="2020-08-01T00:00:00Z" to="2020-10-31T00:00:00Z"'
        })

        creation_data = self.cmd('costmanagement export create '
                                 '--scope {scope} '
                                 '--name {export_name} '
                                 '--storage-account-id {storage_account_id} '
                                 '--storage-container {storage_container} '
                                 '--timeframe {timeframe} ').get_output_in_json()
        self._test_export_create_in_subscription_scope_assertions(creation_data,
                                                                  export_name,
                                                                  storage_container,
                                                                  storage_account_id,
                                                                  timeframe)

        timeframe = 'TheLastBillingMonth'
        self.kwargs.update({
            'timeframe': timeframe,
        })

        update_data = self.cmd('costmanagement export update '
                               '--scope {scope} '
                               '--name {export_name} '
                               '--recurrence-period {time_period} '
                               '--timeframe {timeframe} ').get_output_in_json()
        self.assertEqual(update_data['timeframe'], timeframe)
        self.assertDictEqual(update_data['recurrencePeriod'], {
            "fromProperty": "2020-08-01T00:00:00+00:00",
            "to": "2020-10-31T00:00:00+00:00"
        })

        self.cmd('costmanagement export delete -y --scope {scope} --name {export_name}')
