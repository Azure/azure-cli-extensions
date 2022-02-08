# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class DataShareManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datashare_provider_rg'[:12], location='eastus', key='ProviderResourceGroup')
    @StorageAccountPreparer(name_prefix='clitestdatashareprovidersa'[:12], location='eastus', key='ProviderStorageAccount')
    @AllowLargeResponse()
    def test_datashare(self, resource_group, storage_account):

        self.kwargs.update({
            'ConsumerSubscription': '00000000-0000-0000-0000-000000000000',  # change this value in live test
            'ConsumerResourceGroup': 'datashare_consumer_rg',  # this is a pre-existing reosurce group in consumer subscription
            'ConsumerStorageAccount': 'datashareconsumersa',  # this is a pre-existing storage account in consumer subscription
            'ProviderEmail': 'provider@microsoft.com',  # change this value in live test
            'ConsumerEmail': 'consumer@microsoft.com',  # change this value in live test
            'ProviderAccount': 'cli_test_account',
            'ConsumerAccount': 'cli_test_consumer_account',
            'ProviderDataset': 'cli_test_data_set',
            'ConsumerDatasetMapping': 'cli_test_data_set_mapping',
            'ProviderInvitation': 'cli_test_invitation',
            'ProviderShare': 'cli_test_share',
            'ConsumerShareSubscription': 'cli_test_share_subscription',
            'ProviderSynchronizationSetting': 'cli_test_synchronization_setting',
            'ConsumerTrigger': 'cli_test_trigger',
            'ProviderContainer': 'clitestcontainer',
            'ConsumerContainer': 'clitestconsumercontainer',
        })

        # Provider commands
        datashareAccount = self.cmd('az datashare account create '
                                    '--location "East US" '
                                    '--tags tag1=Red tag2=White '
                                    '--name "{ProviderAccount}" '
                                    '--resource-group "{ProviderResourceGroup}"',
                                    checks=[self.check('name', '{ProviderAccount}'),
                                            self.check('location', 'eastus'),
                                            self.check('resourceGroup', '{ProviderResourceGroup}'),
                                            self.check('tags.tag1', 'Red'),
                                            self.check('tags.tag2', 'White')
                                            ]).get_output_in_json()

        self.cmd('az datashare account wait '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--created',
                 checks=[])

        accountId = datashareAccount['id']
        self.cmd('az datashare account show '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}"',
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'eastus'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])
        self.cmd('az datashare account show '
                 '--ids {}'.format(accountId),
                 checks=[self.check('name', '{ProviderAccount}'),
                         self.check('location', 'eastus'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', '{ProviderResourceGroup}'),
                         self.check('tags.tag1', 'Red'),
                         self.check('tags.tag2', 'White')
                         ])

         # Provider Clean up
        self.cmd('az datashare account delete '
                 '--name "{ProviderAccount}" '
                 '--resource-group "{ProviderResourceGroup}" '
                 '--no-wait '
                 '--yes',
                 checks=[])