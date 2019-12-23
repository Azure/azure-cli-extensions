# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, api_version_constraint)
from ...profiles import CUSTOM_MGMT_STORAGE_ORS


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageAccountORSScenarioTest(ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE_ORS, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_account_ors', location='eastus2euap')
    @StorageAccountPreparer(parameter_name='source_account', location='eastus2euap', kind='StorageV2')
    @StorageAccountPreparer(parameter_name='destination_account', location='eastus2euap', kind='StorageV2')
    def test_storage_account_ors(self, resource_group, source_account, destination_account):
        src_account_info = self.get_account_info(resource_group, source_account)
        src_container = self.create_container(src_account_info)
        dest_account_info = self.get_account_info(resource_group, destination_account)
        dest_container = self.create_container(dest_account_info)
        self.kwargs.update({
            'rg': resource_group,
            'src_sc': source_account,
            'dest_sc': destination_account,
            'scont': src_container,
            'dcont': dest_container
        })

        # Enable ChangeFeed for Storage Accounts
        self.storage_cmd('storage account blob-service-properties update --enable-change-feed', src_account_info) \
            .assert_with_checks(JMESPathCheck('changeFeed', True))
        self.storage_cmd('storage account blob-service-properties update --enable-change-feed', dest_account_info) \
            .assert_with_checks(JMESPathCheck('changeFeed', True))

        # Create ORS policy on destination account
        result = self.storage_cmd('storage account ors-policy create -s {src_sc} -d {dest_sc} --destination-container {dcont} --source-container {scont}',
                                  dest_account_info).get_output_in_json()
        self.assertIn('policyId', result)
        self.assertIn('ruleId', result['rules'][0])

        self.kwargs.update({
            'policy_id': result["policyId"],
            'rule_id': result["rules"]["ruleId"]
        })

        # Get policy properties from destination account
        self.storage_cmd('storage account ors-policy show --policy-id {policy_id}', dest_account_info) \
            .assert_with_checks(JMESPathCheck('type', "Microsoft.Storage/storageAccounts/objectReplicationPolicies")) \
            .assert_with_checks(JMESPathCheck('sourceAccount', source_account)) \
            .assert_with_checks(JMESPathCheck('destinationAccount', destination_account)) \
            .assert_with_checks(JMESPathCheck('rules[0].sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].destinationContainer', dest_container))

        # Add rules
        self.storage_cmd('storage account ors-policy rule list --policy-id {policy_id}', dest_account_info)\
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.storage_cmd('storage account ors-policy show --rule-id {rule_id} --policy-id {policy_id}',
                         dest_account_info)\
            .assert_with_checks(JMESPathCheck('ruleId', result["rules"]["ruleId"])) \
            .assert_with_checks(JMESPathCheck('sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('destinationContainer', dest_container))
        result = self.storage_cmd('storage account ors-policy rule add --policy-id {policy_id} -d {} -s {}',
                                  destination_account).get_output_in_json()
        self.storage_cmd('storage account ors-policy rule list --policy-id {policy_id}', dest_account_info)\
            .assert_with_checks(JMESPathCheck('length(@)', 2))

        # Update rules
        new_destination_container = "new_dcont"
        self.storage_cmd('storage account ors-policy rule update --policy-id {} --rule-id {} -d {}'.format(
            result['policyId'], result['rules']['ruleId'], new_destination_container
        ))
        self.storage_cmd('storage account ors-policy rule show --policy-id {} --rule-id {}'.format(
            result['policyId'], result['rules']['ruleId'])) \
            .assert_with_checks(JMESPathCheck('destinationContainer', new_destination_container))

        # Remove rules
        self.storage_cmd('storage account ors-policy rule remove --policy-id {} --rule-id {}'.format(
            result['policyId'], result['rules']['ruleId']))
        self.storage_cmd('storage account ors-policy rule list --policy-id {policy_id}', dest_account_info) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        # Create ORS policy on source account
        self.storage_cmd('storage account ors-policy create -p result', src_account_info)

        # Get Policy from source account
        self.storage_cmd('storage account ors-policy list', src_account_info) \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        self.storage_cmd('storage account ors-policy show --policy-id {policy_id}', src_account_info) \
            .assert_with_checks(JMESPathCheck('type', "Microsoft.Storage/storageAccounts/objectReplicationPolicies")) \
            .assert_with_checks(JMESPathCheck('sourceAccount', source_account)) \
            .assert_with_checks(JMESPathCheck('destinationAccount', destination_account)) \
            .assert_with_checks(JMESPathCheck('rules[0].sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].destinationContainer', dest_container))

        # Update ORS policy
        new_source_account = 'new_source_account'
        self.storage_cmd('storage account ors-policy update --policy-id {policy-id} --source-account {}'.format(
            new_source_account), dest_account_info) \
            .assert_with_checks(JMESPathCheck('sourceAccount', new_source_account))

        # Remove policy from destination and source account
        self.storage_cmd('storage account ors-policy remove --policy-id {policy_id}', dest_account_info)

        self.storage_cmd('storage account ors-policy list ') \
            .assert_with_checks(JMESPathCheck('length(@)', 0))
