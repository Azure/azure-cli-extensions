# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer,
                               JMESPathCheck, api_version_constraint)
from ..storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_STORAGE_ORS


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class StorageAccountORSScenarioTest(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_STORAGE_ORS, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_account_ors', location='eastus2euap')
    @StorageAccountPreparer(parameter_name='source_account', location='eastus2euap', kind='StorageV2')
    @StorageAccountPreparer(parameter_name='destination_account', location='eastus2euap', kind='StorageV2')
    @StorageAccountPreparer(parameter_name='new_account', location='eastus2euap', kind='StorageV2')
    def test_storage_account_ors(self, resource_group, source_account, destination_account, new_account):
        src_account_info = self.get_account_info(resource_group, source_account)
        src_container = self.create_container(src_account_info)
        dest_account_info = self.get_account_info(resource_group, destination_account)
        dest_container = self.create_container(dest_account_info)
        self.kwargs.update({
            'rg': resource_group,
            'src_sc': source_account,
            'dest_sc': destination_account,
            'new_sc': new_account,
            'scont': src_container,
            'dcont': dest_container,
        })

        # Enable ChangeFeed for Source Storage Accounts
        self.cmd('storage account blob-service-properties update -n {src_sc} -g {rg} --enable-change-feed', checks=[
                 JMESPathCheck('changeFeed.enabled', True)])

        # Enable Versioning for two Storage Accounts
        self.cmd('storage account blob-service-properties update -n {src_sc} -g {rg} --enable-versioning', checks=[
                 JMESPathCheck('isVersioningEnabled', True)])

        self.cmd('storage account blob-service-properties update -n {dest_sc} -g {rg} --enable-versioning', checks=[
                 JMESPathCheck('isVersioningEnabled', True)])

        # Create ORS policy on destination account
        result = self.cmd('storage account or-policy create -g {rg} -n {dest_sc} -s {src_sc} --destination-container {dcont} --source-container {scont} -t "2020-02-19T16:05:00Z"')\
            .get_output_in_json()
        self.assertIn('policyId', result)
        self.assertIn('ruleId', result['rules'][0])
        self.assertEqual(result["rules"][0]["filters"]["minCreationTime"], "2020-02-19T16:05:00Z")

        self.kwargs.update({
            'policy_id': result["policyId"],
            'rule_id': result["rules"][0]["ruleId"]
        })

        # Get policy properties from destination account
        self.cmd('storage account or-policy show -g {rg} -n {dest_sc} --policy-id {policy_id}') \
            .assert_with_checks(JMESPathCheck('type', "Microsoft.Storage/storageAccounts/objectReplicationPolicies")) \
            .assert_with_checks(JMESPathCheck('sourceAccount', source_account)) \
            .assert_with_checks(JMESPathCheck('destinationAccount', destination_account)) \
            .assert_with_checks(JMESPathCheck('rules[0].sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].destinationContainer', dest_container))

        # Add rules
        src_container1 = self.create_container(src_account_info)
        dest_container1 = self.create_container(dest_account_info)
        self.cmd('storage account or-policy rule list -g {rg} -n {dest_sc} --policy-id {policy_id}')\
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.cmd('storage account or-policy rule show -g {rg} -n {dest_sc} --rule-id {rule_id} --policy-id {policy_id}')\
            .assert_with_checks(JMESPathCheck('ruleId', result["rules"][0]["ruleId"])) \
            .assert_with_checks(JMESPathCheck('sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('destinationContainer', dest_container))

        result = self.cmd('storage account or-policy rule add -g {} -n {} --policy-id {} -d {} -s {} -t "2020-02-19T16:05:00Z"'.format(
            resource_group, destination_account, self.kwargs["policy_id"], dest_container1, src_container1)).get_output_in_json()
        self.assertEqual(result["rules"][0]["filters"]["minCreationTime"], "2020-02-19T16:05:00Z")

        self.cmd('storage account or-policy rule list -g {rg} -n {dest_sc} --policy-id {policy_id}')\
            .assert_with_checks(JMESPathCheck('length(@)', 2))

        # Update rules
        self.cmd('storage account or-policy rule update -g {} -n {} --policy-id {} --rule-id {} --prefix-match blobA blobB -t "2020-02-20T16:05:00Z"'.format(
            resource_group, destination_account, result['policyId'], result['rules'][1]['ruleId'])) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[0]', 'blobA')) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[1]', 'blobB')) \
            .assert_with_checks(JMESPathCheck('filters.minCreationTime', '2020-02-20T16:05:00Z'))

        self.cmd('storage account or-policy rule show -g {} -n {} --policy-id {} --rule-id {}'.format(
            resource_group, destination_account, result['policyId'], result['rules'][1]['ruleId'])) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[0]', 'blobA')) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[1]', 'blobB')) \
            .assert_with_checks(JMESPathCheck('filters.minCreationTime', '2020-02-20T16:05:00Z'))

        # Remove rules
        self.cmd('storage account or-policy rule remove -g {} -n {} --policy-id {} --rule-id {}'.format(
            resource_group, destination_account, result['policyId'], result['rules'][1]['ruleId']))
        self.cmd('storage account or-policy rule list -g {rg} -n {dest_sc} --policy-id {policy_id}') \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        # Set ORS policy to source account
        import json
        temp_dir = self.create_temp_dir()
        policy_file = os.path.join(temp_dir, "policy.json")
        with open(policy_file, "w") as f:
            policy = self.cmd('storage account or-policy show -g {rg} -n {dest_sc} --policy-id {policy_id}')\
                .get_output_in_json()
            json.dump(policy, f)
        self.kwargs['policy'] = policy_file
        self.cmd('storage account or-policy create -g {rg} -n {src_sc} -p @"{policy}"')\
            .assert_with_checks(JMESPathCheck('type', "Microsoft.Storage/storageAccounts/objectReplicationPolicies")) \
            .assert_with_checks(JMESPathCheck('sourceAccount', source_account)) \
            .assert_with_checks(JMESPathCheck('destinationAccount', destination_account)) \
            .assert_with_checks(JMESPathCheck('rules[0].sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].destinationContainer', dest_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].filters.minCreationTime', '2020-02-19T16:05:00Z'))

        # Update ORS policy
        self.cmd('storage account or-policy update -g {} -n {} --policy-id {} --source-account {}'.format(
            resource_group, destination_account, self.kwargs["policy_id"], new_account)) \
            .assert_with_checks(JMESPathCheck('sourceAccount', new_account))

        # Delete policy from destination and source account
        self.cmd('storage account or-policy delete -g {rg} -n {src_sc} --policy-id {policy_id}')
        self.cmd('storage account or-policy list -g {rg} -n {src_sc}') \
            .assert_with_checks(JMESPathCheck('length(@)', 0))

        self.cmd('storage account or-policy delete -g {rg} -n {dest_sc} --policy-id {policy_id}')
        self.cmd('storage account or-policy list -g {rg} -n {dest_sc}') \
            .assert_with_checks(JMESPathCheck('length(@)', 0))
