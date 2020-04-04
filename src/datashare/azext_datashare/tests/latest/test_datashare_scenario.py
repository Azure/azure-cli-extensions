# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class DataShareManagementClientScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='cli_test_datashare_SampleResourceGroup'[:9], key='rg')
    def test_datashare(self, resource_group):

        self.kwargs.update({
            'Account1': self.create_random_name(prefix='cli_test_accounts'[:9], length=24),
            'Dataset1': self.create_random_name(prefix='cli_test_data_sets'[:9], length=24),
            'DatasetMapping1': self.create_random_name(prefix='cli_test_data_set_mappings'[:9], length=24),
            'Invitation1': self.create_random_name(prefix='cli_test_invitations'[:9], length=24),
            'Share1': self.create_random_name(prefix='cli_test_shares'[:9], length=24),
            'ShareSubscription1': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'ShareSubscriptions_2': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'ShareSubscriptions_3': self.create_random_name(prefix='cli_test_share_subscriptions'[:9], length=24),
            'SynchronizationSettings_2': self.create_random_name(prefix='cli_test_synchronization_settings'[:9], length=24),
            'Trigger1': self.create_random_name(prefix='cli_test_triggers'[:9], length=24),
        })

        datashareAccount = self.cmd('az datashare account create '
                                    '--identity type=SystemAssigned '
                                    '--location "West US 2" '
                                    '--tags tag1=Red tag2=White '
                                    '--name "{Account1}" '
                                    '--resource-group "{rg}"',
                                    checks=[self.check('name', self.kwargs.get('Account1', '')),
                                            self.check('location', 'westus2'),
                                            self.check('resourceGroup', self.kwargs.get('rg', '')),
                                            self.check('tags', '{\'tag1\': \'Red\', \'tag2\': \'White\'}'),
                                            ]).get_output_in_json()
        
        self.cmd('az datashare account wait '
                 '--name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--created',
                 checks=[])

        accountId = datashareAccount['id']
        self.cmd('az datashare account show '
                 '-n "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[self.check('name', self.kwargs.get('Account1', '')),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', self.kwargs.get('rg', '')),
                         self.check('tags', '{\'tag1\': \'Red\', \'tag2\': \'White\'}'),
                         ])

        self.cmd('az datashare account show '
                 '--ids {}'.format(accountId),
                 checks=[self.check('name', self.kwargs.get('Account1', '')),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', self.kwargs.get('rg', '')),
                         self.check('tags', '{\'tag1\': \'Red\', \'tag2\': \'White\'}'),
                         ])

        self.cmd('az datashare account list '
                 '--resource-group "{rg}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(accountId), self.kwargs.get('Account1', '')),
                         self.check("[?id=='{}'].location | [0]".format(accountId), 'westus2'),
                         self.check("[?id=='{}'].resourceGroup | [0]".format(accountId), self.kwargs.get('rg', '')),
                         self.check("[?id=='{}'].tags | [0]".format(accountId), '{\'tag1\': \'Red\', \'tag2\': \'White\'}'),
                         ])

        self.cmd('az datashare account list'
                 '--resource-group=',
                 checks=[self.check("[?id=='{}'].name | [0]".format(accountId), self.kwargs.get('Account1', '')),
                         self.check("[?id=='{}'].location | [0]".format(accountId), 'westus2'),
                         self.check("[?id=='{}'].resourceGroup | [0]".format(accountId), self.kwargs.get('rg', '')),
                         self.check("[?id=='{}'].tags | [0]".format(accountId), '{\'tag1\': \'Red\', \'tag2\': \'White\'}'),
                         ])

        self.cmd('az datashare account update '
                 '--name "{Account1}" '
                 '--tags tag1=Green'
                 '--resource-group "{rg}"',
                 checks=[self.check('name', self.kwargs.get('Account1', '')),
                         self.check('location', 'westus2'),
                         self.check('provisioningState', 'Succeeded'),
                         self.check('resourceGroup', self.kwargs.get('rg', '')),
                         self.check('tags', '{\'tag1\': \'Green\'}')])

        datashare = self.cmd('az datashare create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--description "share description" '
                 '--share-kind "CopyBased" '
                 '--terms "Confidential" '
                 '--name "{Share1}"',
                 checks=[self.check('name', self.kwargs.get('Share1', '')),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')
                 ]).get_output_in_json()

        datashareId = datashare['id']
        self.cmd('az datashare show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--name "{Share1}"',
                 checks=[self.check('name', self.kwargs.get('Share1', '')),
                         self.check('description', 'share description'),
                         self.check('shareKind', 'CopyBased'),
                         self.check('terms', 'Confidential')])
        
        self.cmd('az datashare list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[self.check("[?id=='{}'].name | [0]".format(datashareId), self.kwargs.get('Share1', '')),
                         self.check("[?id=='{}'].description | [0]".format(datashareId), 'share description'),
                         self.check("[?id=='{}'].shareKind | [0]".format(datashareId), 'CopyBased'),
                         self.check("[?id=='{}'].terms | [0]".format(datashareId), 'Confidential'])


        self.cmd('az datashare dataset create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDWTable" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare dataset create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDBTable" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare dataset create '
                 '--account-name "{Account1}" '
                 '--kind "KustoDatabase" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare dataset create '
                 '--account-name "{Account1}" '
                 '--kind "KustoCluster" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare dataset create '
                 '--account-name "{Account1}" '
                 '--kind "Blob" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])
        
        self.cmd('az datashare dataset show '
                 '--account-name "{Account1}" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])
        
        self.cmd('az datashare dataset list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--kind "ScheduleBased" '
                 '--name "{SynchronizationSettings_2}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--name "{SynchronizationSettings_2}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare list-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare list-synchronization-detail '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        self.cmd('az datashare invitation create '
                 '--account-name "{Account1}" '
                 '--target-email "receiver@microsoft.com" '
                 '--name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare invitation show '
                 '--account-name "{Account1}" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])
        
        self.cmd('az datashare invitation list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share-subscription create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--invitation-id "12345678-1234-1234-12345678abd" '
                 '--source-share-location "eastus2" '
                 '--name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare share-subscription show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare share-subscription list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])
        
        self.cmd('az datashare share-subscription list-source-share-synchronization-setting '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_3}"',
                 checks=[])

        self.cmd('az datashare share-subscription list-synchronization-detail '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_3}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        self.cmd('az datashare share-subscription cancel-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        self.cmd('az datashare share-subscription list-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_3}"',
                 checks=[])

        self.cmd('az datashare share-subscription synchronize '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--synchronization-mode "Incremental"',
                 checks=[])

        self.cmd('az datashare trigger create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--kind "ScheduleBased" '
                 '--name "{Trigger1}"',
                 checks=[])

        self.cmd('az datashare dataset-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDWTable" '
                 '--name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare dataset-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "AdlsGen2File" '
                 '--name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare dataset-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDBTable" '
                 '--mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare dataset-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "Blob" '
                 '--mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare dataset-mapping show '
                 '--account-name "{Account1}" '
                 '--mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare dataset-mapping list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])
        
        self.cmd('az datashare provider-share-subscription show '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])
        self.cmd('az datashare provider-share-subscription list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])
        self.cmd('az datashare provider-share-subscription reinstate '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare provider-share-subscription revoke '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare trigger show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

    
        self.cmd('az datashare consumer-invitation show '
                 '--invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
                 '--location "East US 2"',
                 checks=[])

        self.cmd('az datashare consumer-source-dataset list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_2}"',
                 checks=[])

        

        self.cmd('az datashare trigger list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        

        


        self.cmd('az datashare consumer-invitation list',
                 checks=[])

        


        self.cmd('az datashare consumer-invitation reject-invitation '
                 '--invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
                 '--location "East US 2"',
                 checks=[])

        self.cmd('az datashare dataset-mapping delete '
                 '--account-name "{Account1}" '
                 '--name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '-name "{SynchronizationSettings_2}"',
                 checks=[])

        self.cmd('az datashare trigger delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--name "{Trigger1}"',
                 checks=[])

        self.cmd('az datashare invitation delete '
                 '--account-name "{Account1}" '
                 '--name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share-subscription delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare dataset delete '
                 '--account-name "{Account1}" '
                 '--name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--name "{Share1}"',
                 checks=[])

        self.cmd('az datashare account delete '
                 '--name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--no-wait',
                 checks=[])

        self.cmd('az datashare account wait '
                 '--name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--deleted',
                 checks=[])
