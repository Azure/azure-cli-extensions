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
    @StorageAccountPreparer(name_prefix='test_export_create'.replace('_', ''), location='westus2')
    def test_export_create_in_subscription_scope(self, resource_group, storage_account):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        export_name = self.create_random_name('ep', 15)
        type = 'Usage'  # 'Usage' is the default export type
        storage_container = 'export'
        timeframe = 'TheLastMonth'
        schedule_status = 'Inactive'  # 'Inactive' is the default schedule status
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
                                                                  timeframe,
                                                                  type,
                                                                  schedule_status)

        # show an export
        show_data = self.cmd('costmanagement export show --scope {scope} --name {export_name}').get_output_in_json()
        self._test_export_create_in_subscription_scope_assertions(show_data,
                                                                  export_name,
                                                                  storage_container,
                                                                  storage_account_id,
                                                                  timeframe,
                                                                  type,
                                                                  schedule_status)

        # list exports
        self.cmd('costmanagement export list --scope {scope}').get_output_in_json()

        self.cmd('costmanagement export delete -y --scope {scope} --name {export_name}')

        with self.assertRaisesRegex(SystemExit, '3'):
            self.cmd('costmanagement export show --scope {scope} --name {export_name}')

    def _test_export_create_in_subscription_scope_assertions(self, data, export_name, storage_container, storage_account_id, timeframe, type, schedule_status):
        self.assertEqual(data['name'], export_name)
        self.assertIsNone(data['definition']['dataSet']['configuration'], None)
        self.assertDictEqual(data['deliveryInfo']['destination'], {
            'container': storage_container,
            'resourceId': storage_account_id,
            'rootFolderPath': None
        })
        self.assertEqual(data['definition']['type'], type)
        self.assertIsNone(data['schedule']['recurrence'])
        self.assertIsNone(data['schedule']['recurrencePeriod'])
        self.assertEqual(data['schedule']['status'] , schedule_status)
        self.assertIsNone(data['definition']['timePeriod'])
        self.assertEqual(data['definition']['timeframe'], timeframe)

    @ResourceGroupPreparer(name_prefix='test_export_schedule')
    @StorageAccountPreparer(name_prefix='test_export_schedule'.replace('_', ''), location='westus2')
    def test_export_create_with_schedule_in_subscription_scope(self, resource_group, storage_account):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        export_name = self.create_random_name('ep', 15)
        type = 'Usage'  # 'Usage' is the default export type
        storage_container = 'export'
        timeframe = 'TheLastMonth'
        recurrence = 'Weekly'
        schedule_status = 'Active'
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
            'schedule_status': schedule_status,
            'recurrence': recurrence,
            'recurrence_period': 'from="2022-04-01T00:00:00Z" to="2022-04-30T00:00:00Z"'
        })

        recurrence_period_dict = {
            "fromProperty": "2022-04-01T00:00:00+00:00",
            "to": "2022-04-30T00:00:00+00:00"
        }

        creation_data = self.cmd('costmanagement export create '
                                 '--scope {scope} '
                                 '--name {export_name} '
                                 '--storage-account-id {storage_account_id} '
                                 '--storage-container {storage_container} '
                                 '--timeframe {timeframe} '
                                 '--recurrence {recurrence} '
                                 '--recurrence-period {recurrence_period} '
                                 '--schedule-status {schedule_status}').get_output_in_json()
        self._test_export_create_with_schedule_in_subscription_scope_assertions(creation_data,
                                                                                export_name,
                                                                                storage_container,
                                                                                storage_account_id,
                                                                                timeframe,
                                                                                type,
                                                                                schedule_status,
                                                                                recurrence,
                                                                                recurrence_period_dict)

        # show an export
        show_data = self.cmd('costmanagement export show --scope {scope} --name {export_name}').get_output_in_json()
        self._test_export_create_with_schedule_in_subscription_scope_assertions(show_data,
                                                                                export_name,
                                                                                storage_container,
                                                                                storage_account_id,
                                                                                timeframe,
                                                                                type,
                                                                                schedule_status,
                                                                                recurrence,
                                                                                recurrence_period_dict)

        # list exports
        self.cmd('costmanagement export list --scope {scope}').get_output_in_json()

        self.cmd('costmanagement export delete -y --scope {scope} --name {export_name}')

        with self.assertRaisesRegex(SystemExit, '3'):
            self.cmd('costmanagement export show --scope {scope} --name {export_name}')

    def _test_export_create_with_schedule_in_subscription_scope_assertions(self, data, export_name, storage_container, storage_account_id, timeframe, type, schedule_status, recurrence, recurrence_period):
        self.assertEqual(data['name'], export_name)
        self.assertIsNone(data['definition']['dataSet']['configuration'], None)
        self.assertDictEqual(data['deliveryInfo']['destination'], {
            'container': storage_container,
            'resourceId': storage_account_id,
            'rootFolderPath': None
        })
        self.assertEqual(data['definition']['type'], type)
        self.assertEqual(data['schedule']['recurrence'], recurrence)
        self.assertDictEqual(data['schedule']['recurrencePeriod'], recurrence_period)

        self.assertEqual(data['schedule']['status'], schedule_status)
        self.assertIsNone(data['definition']['timePeriod'])
        self.assertEqual(data['definition']['timeframe'], timeframe)

    @ResourceGroupPreparer(name_prefix='test_update_schedule')
    @StorageAccountPreparer(name_prefix='test_update_schedule'.replace('_', ''), location='westus2')
    def test_update_with_timeperiod_in_subscription_scope(self, resource_group, storage_account):
        self.kwargs.update({
            'scope': '/subscriptions/{}'.format(self.get_subscription_id()),
        })

        export_name = self.create_random_name('ep', 15)
        storage_container = 'export'
        timeframe = 'TheLastMonth'
        type = 'ActualCost'
        schedule_status = 'Inactive'  # 'Inactive' is the default schedule status
        storage_account_id = '/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{account_name}'.format(
            sub=self.get_subscription_id(),
            rg=resource_group,
            account_name=storage_account
        )

        self.kwargs.update({
            'export_name': export_name,
            'type': type,
            'storage_account_id': storage_account_id,
            'storage_container': storage_container,
            'timeframe': timeframe
        })

        creation_data = self.cmd('costmanagement export create '
                                 '--scope {scope} '
                                 '--name {export_name} '
                                 '--type {type} '
                                 '--storage-account-id {storage_account_id} '
                                 '--storage-container {storage_container} '
                                 '--timeframe {timeframe} ').get_output_in_json()
        self._test_export_create_in_subscription_scope_assertions(creation_data,
                                                                  export_name,
                                                                  storage_container,
                                                                  storage_account_id,
                                                                  timeframe,
                                                                  type,
                                                                  schedule_status)

        timeframe = 'TheLastBillingMonth'
        self.kwargs.update({
            'timeframe': timeframe,
            'time_period': 'from="2022-04-01T00:00:00Z" to="2022-04-30T00:00:00Z"'
        })

        update_data = self.cmd('costmanagement export update '
                               '--scope {scope} '
                               '--name {export_name} '
                               '--recurrence-period {time_period} '
                               '--timeframe {timeframe} ').get_output_in_json()
        self.assertEqual(update_data['definition']['timeframe'], timeframe)
        self.assertDictEqual(update_data['schedule']['recurrencePeriod'], {
            "fromProperty": "2022-04-01T00:00:00+00:00",
            "to": "2022-04-30T00:00:00+00:00"
        })

        self.cmd('costmanagement export delete -y --scope {scope} --name {export_name}')
