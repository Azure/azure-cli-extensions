# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk import ResourceGroupPreparer


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
            'Dataset1': self.create_random_name(prefix='cli_test_synchronization_settings'[:9], length=24),
            'SynchronizationSettings_2': self.create_random_name(prefix='cli_test_synchronization_settings'[:9], length=24),
            'Trigger1': self.create_random_name(prefix='cli_test_triggers'[:9], length=24),
        })

        self.cmd('az datashare account create '
                 '--identity type=SystemAssigned '
                 '--location "West US 2" '
                 '--tags tag1=Red tag2=White '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az datashare share create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--properties-description "share description" '
                 '--properties-share-kind "CopyBased" '
                 '--properties-terms "Confidential" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDWTable" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDBTable" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--kind "KustoDatabase" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--kind "KustoCluster" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare data-set create '
                 '--account-name "{Account1}" '
                 '--kind "Blob" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share-subscription create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--properties-invitation-id "12345678-1234-1234-12345678abd" '
                 '--properties-source-share-location "eastus2" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare invitation create '
                 '--account-name "{Account1}" '
                 '--properties-target-email "receiver@microsoft.com" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare trigger create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--kind "ScheduleBased" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting create '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--kind "ScheduleBased" '
                 '--synchronization-setting-name "{Dataset1}"',
                 checks=[])

        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDWTable" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "AdlsGen2File" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "SqlDBTable" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare data-set-mapping create '
                 '--account-name "{Account1}" '
                 '--kind "Blob" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare data-set-mapping show '
                 '--account-name "{Account1}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare provider-share-subscription show '
                 '--account-name "{Account1}" '
                 '--provider-share-subscription-id "d5496da4-9c52-402f-b067-83cc9ddea888" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-setting-name "{SynchronizationSettings_2}"',
                 checks=[])

        self.cmd('az datashare trigger show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

        self.cmd('az datashare invitation show '
                 '--account-name "{Account1}" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share-subscription show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare data-set show '
                 '--account-name "{Account1}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare account show '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az datashare consumer-invitation show '
                 '--invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
                 '--location "East US 2"',
                 checks=[])

        self.cmd('az datashare consumer-source-data-set list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscriptions_2}"',
                 checks=[])

        self.cmd('az datashare data-set-mapping list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare trigger list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare provider-share-subscription list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare invitation list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare data-set list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share-subscription list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az datashare share list '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az datashare account list '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az datashare account list',
                 checks=[])

        self.cmd('az datashare consumer-invitation list',
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

        self.cmd('az datashare share list-synchronization-detail '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-id "7d0536a6-3fa5-43de-b152-3d07c4f6b2bb"',
                 checks=[])

        self.cmd('az datashare share list-synchronization '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare account update '
                 '--account-name "{Account1}" '
                 '--tags tag1=Red tag2=White '
                 '--resource-group "{rg}"',
                 checks=[])

        self.cmd('az datashare consumer-invitation reject-invitation '
                 '--properties-invitation-id "dfbbc788-19eb-4607-a5a1-c74181bfff03" '
                 '--location "East US 2"',
                 checks=[])

        self.cmd('az datashare data-set-mapping delete '
                 '--account-name "{Account1}" '
                 '--data-set-mapping-name "{DatasetMapping1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare synchronization-setting delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}" '
                 '--synchronization-setting-name "{SynchronizationSettings_2}"',
                 checks=[])

        self.cmd('az datashare trigger delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}" '
                 '--trigger-name "{Trigger1}"',
                 checks=[])

        self.cmd('az datashare invitation delete '
                 '--account-name "{Account1}" '
                 '--invitation-name "{Invitation1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share-subscription delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-subscription-name "{ShareSubscription1}"',
                 checks=[])

        self.cmd('az datashare data-set delete '
                 '--account-name "{Account1}" '
                 '--data-set-name "{Dataset1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare share delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}" '
                 '--share-name "{Share1}"',
                 checks=[])

        self.cmd('az datashare account delete '
                 '--account-name "{Account1}" '
                 '--resource-group "{rg}"',
                 checks=[])
