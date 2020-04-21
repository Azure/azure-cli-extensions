# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, JMESPathCheck)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DataBoxScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_databox')
    @StorageAccountPreparer(parameter_name='storage_account_1')
    @StorageAccountPreparer(parameter_name='storage_account_2')
    def test_databox(self, storage_account_1, storage_account_2):
        job_name = self.create_random_name('job', 24)
        self.kwargs.update({
            'job_name': job_name,
            'storage_account_1': storage_account_1,
            'storage_account_2': storage_account_2
        })

        # Create a databox job with sku 'DataBox'.
        self.cmd('databox job create '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--location westus '
                 '--sku DataBox '
                 '--contact-name "Public SDK Test" '
                 '--phone 14258828080 '
                 '--email-list testing@microsoft.com '
                 '--street-address1 "1 MICROSOFT WAY" '
                 '--city Redmond '
                 '--state-or-province WA '
                 '--country US '
                 '--postal-code 98052 '
                 '--company-name Microsoft '
                 '--storage-account {storage_account_1} {storage_account_2} '
                 '--staging-storage-account {storage_account_1} '
                 '--resource-group-for-managed-disk rg-for-managed-disk',
                 checks=[JMESPathCheck('status', 'DeviceOrdered')])

        self.cmd('databox job update '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--contact-name "Public SDK Test 1" '
                 '--email-list testing1@microsoft.com',
                 checks=[])

        self.cmd('databox job show '
                 '--resource-group {rg} '
                 '--name {job_name}',
                 checks=[
                     JMESPathCheck('name', job_name),
                     JMESPathCheck('isCancellable', True),
                     JMESPathCheck('isDeletable', False),
                     JMESPathCheck('details.contactDetails.contactName', 'Public SDK Test 1'),
                     JMESPathCheck('details.contactDetails.emailList[0]', 'testing1@microsoft.com')])

        self.cmd('databox job list '
                 '--resource-group {rg}',
                 checks=[JMESPathCheck('length(@)', 1)])

        self.cmd('databox job cancel '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--reason "CancelTest" '
                 '-y',
                 checks=[])

        self.cmd('databox job show '
                 '--resource-group {rg} '
                 '--name {job_name}',
                 checks=[
                     JMESPathCheck('name', job_name),
                     JMESPathCheck('isCancellable', False),
                     JMESPathCheck('isDeletable', True)])

        self.cmd('databox job delete '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '-y',
                 checks=[])

        self.cmd('databox job show '
                 '--resource-group {rg} '
                 '--name {job_name}',
                 expect_failure=True)

        # Create another databox job with sku 'DataBoxDisk'.
        self.cmd('databox job create '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--location westus '
                 '--sku DataBoxDisk '
                 '--expected-data-size 1 '
                 '--contact-name "Public SDK Test" '
                 '--phone 14258828080 '
                 '--email-list testing@microsoft.com '
                 '--street-address1 "1 MICROSOFT WAY" '
                 '--city Redmond '
                 '--state-or-province WA '
                 '--country US '
                 '--postal-code 98052 '
                 '--company-name Microsoft '
                 '--storage-account {storage_account_1}',
                 checks=[JMESPathCheck('status', 'DeviceOrdered')])

        self.cmd('databox job cancel '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '--reason "CancelTest" '
                 '-y',
                 checks=[])

        self.cmd('databox job delete '
                 '--resource-group {rg} '
                 '--name {job_name} '
                 '-y',
                 checks=[])

        self.cmd('databox job show '
                 '--resource-group {rg} '
                 '--name {job_name}',
                 expect_failure=True)

        # DataBox service will create a lock 'DATABOX_SERVICE' on the storage account under the resource group when creating a job. In order to clean up the resource group, we need delete the lock first.
        self.cmd('lock delete '
                 '--name DATABOX_SERVICE '
                 '-g {rg} '
                 '--resource-name {storage_account_1} '
                 '--resource-type Microsoft.Storage/storageAccounts')

        self.cmd('lock delete '
                 '--name DATABOX_SERVICE '
                 '-g {rg} '
                 '--resource-name {storage_account_2} '
                 '--resource-type Microsoft.Storage/storageAccounts')
