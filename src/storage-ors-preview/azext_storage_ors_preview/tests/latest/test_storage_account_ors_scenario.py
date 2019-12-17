# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, api_version_constraint)
from ...profiles import CUSTOM_MGMT_STORAGE


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageAccountORSScenarioTest(ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE, min_api='2019-04-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_account_ors', location='eastus2euap')
    @StorageAccountPreparer(parameter_name='source_account', name_Prefix='cli_test_storage_ors', kind='StorageV2')
    @StorageAccountPreparer(parameter_name='destination_account', name_Prefix='cli_test_storage_ors', kind='StorageV2')
    def test_storage_account_ors(self, resource_group, source_account, destination_account):
        src_account_info = self.get_account_info(resource_group, source_account)
        src_container = self.create_container(src_account_info)
        dest_account_info = self.get_account_info(resource_group, destination_account)
        dest_container = self.create_container(dest_account_info)
        self.kwargs.update({
            'rg': resource_group,
            'src_sc': source_account,
            'dest_sc': destination_account
        })

        #TODO: Enable ChangeFeed for Storage Account

        # Create ORS policy on destination account
        res = self.storage_cmd('storage account ors-policy create --properties @ors_policy.json', dest_account_info) \
            .get_output_in_json()
        self.kwargs.update({
            'policy_id': res["policyId"],
            'rule_id': res["rules"]["ruleId"]
        })

        self.storage_cmd('storage account ors-policy create --policy-id default --source-account {stc_sc} --destination-account {dest_sc} --rules {}', dest_account_info)
        # Get ORS policy from destination account
        self.storage_cmd('storage account ors-policy show --policy-id {policy_id}', dest_account_info)

        # Create ORS policy on source account
        self.storage_cmd('storage account ors-policy create ', src_account_info)

        # Get Policy from source account
        self.storage_cmd('storage account ors-policy list ')
        self.storage_cmd('storage account ors-policy show ')

        # Update ORS policy
        self.storage_cmd('storage account ors-policy update ')

        # Add rules
        self.storage_cmd('storage account ors-policy rule list ')
        self.storage_cmd('storage account ors-policy rule add ')
        self.storage_cmd('storage account ors-policy rule list ')
        self.storage_cmd('storage account ors-policy show')

        # Update rules
        self.storage_cmd('storage account ors-policy rule show')
        self.storage_cmd('storage account ors-policy rule update')
        self.storage_cmd('storage account ors-policy rule show')
        self.storage_cmd('storage account ors-policy show')

        # Remove rules
        self.storage_cmd('storage account ors-policy rule list ')
        self.storage_cmd('storage account ors-policy rule remove')
        self.storage_cmd('storage account ors-policy rule list ')
        self.storage_cmd('storage account ors-policy show')

        # Remove policy from destination and source account
        self.storage_cmd('storage account ors-policy list ')
        self.storage_cmd('storage account ors-policy delete ')
        self.storage_cmd('storage account ors-policy list ')
