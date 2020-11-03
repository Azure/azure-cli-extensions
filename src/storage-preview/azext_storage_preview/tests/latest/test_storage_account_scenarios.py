# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.cli.testsdk import (ScenarioTest, JMESPathCheck, ResourceGroupPreparer, StorageAccountPreparer,
                               api_version_constraint)
from .storage_test_util import StorageScenarioMixin
from ...profiles import CUSTOM_MGMT_PREVIEW_STORAGE
from azure_devtools.scenario_tests import AllowLargeResponse


@api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2016-12-01')
class StorageAccountNetworkRuleTests(StorageScenarioMixin, ScenarioTest):
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2017-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_network_rules(self, resource_group):
        kwargs = {
            'rg': resource_group,
            'acc': self.create_random_name(prefix='cli', length=24),
            'vnet': 'vnet1',
            'subnet': 'subnet1'
        }
        self.cmd('storage account create -g {rg} -n {acc} --bypass Metrics --default-action Deny --https-only'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Metrics'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])
        self.cmd('storage account update -g {rg} -n {acc} --bypass Logging --default-action Allow'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Allow')])
        self.cmd('storage account update -g {rg} -n {acc} --set networkRuleSet.default_action=deny'.format(**kwargs),
                 checks=[
                     JMESPathCheck('networkRuleSet.bypass', 'Logging'),
                     JMESPathCheck('networkRuleSet.defaultAction', 'Deny')])

        self.cmd('network vnet create -g {rg} -n {vnet} --subnet-name {subnet}'.format(**kwargs))
        self.cmd(
            'network vnet subnet update -g {rg} --vnet-name {vnet} -n {subnet} --service-endpoints Microsoft.Storage'.format(
                **kwargs))

        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        # test network-rule add idempotent
        self.cmd('storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --ip-address 25.2.0.0/24'.format(**kwargs))
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 2),
            JMESPathCheck('length(virtualNetworkRules)', 1)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --ip-address 25.1.2.3'.format(**kwargs))
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {acc} --vnet-name {vnet} --subnet {subnet}'.format(
                **kwargs))
        self.cmd('storage account network-rule list -g {rg} --account-name {acc}'.format(**kwargs), checks=[
            JMESPathCheck('length(ipRules)', 1),
            JMESPathCheck('length(virtualNetworkRules)', 0)
        ])

    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2020-08-01-preview')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_service_endpoints')
    @StorageAccountPreparer()
    def test_storage_account_resource_access_rules(self, resource_group, storage_account):
        self.kwargs = {
            'rg': resource_group,
            'sa': storage_account,
            'rid1': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace1",
            'rid2': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace2",
            'rid3': "/subscriptions/a7e99807-abbf-4642-bdec-2c809a96a8bc/resourceGroups/res9407/providers/Microsoft.Synapse/workspaces/testworkspace3",
            'tid1': "72f988bf-86f1-41af-91ab-2d7cd011db47",
            'tid2': "72f988bf-86f1-41af-91ab-2d7cd011db47"
        }

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add idempotent
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])

        # test network-rule add more
        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])

        self.cmd(
            'storage account network-rule add -g {rg} --account-name {sa} --resource-id {rid3} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 3)
        ])

        # remove network-rule
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid1} --tenant-id {tid1}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 2)
        ])
        self.cmd(
            'storage account network-rule remove -g {rg} --account-name {sa} --resource-id {rid2} --tenant-id {tid2}')
        self.cmd('storage account network-rule list -g {rg} --account-name {sa}', checks=[
            JMESPathCheck('length(resourceAccessRules)', 1)
        ])


class StorageAccountBlobInventoryScenarioTest(StorageScenarioMixin, ScenarioTest):
    @AllowLargeResponse()
    @api_version_constraint(CUSTOM_MGMT_PREVIEW_STORAGE, min_api='2019-06-01')
    @ResourceGroupPreparer(name_prefix='cli_test_storage_account_ors', location='eastus2')
    @StorageAccountPreparer(parameter_name='source_account', location='eastus2', kind='StorageV2')
    @StorageAccountPreparer(parameter_name='destination_account', location='eastus2', kind='StorageV2')
    @StorageAccountPreparer(parameter_name='new_account', location='eastus2', kind='StorageV2')
    def test_storage_account_blob_inventory_policy(self, resource_group, source_account, destination_account, new_account):
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
        result = self.cmd('storage account blob-inventory-policy create -n {dest_sc} -s {src_sc} --dcont {dcont} '
                          '--scont {scont} -t "2020-02-19T16:05:00Z"').get_output_in_json()
        self.assertIn('policyId', result)
        self.assertIn('ruleId', result['rules'][0])
        self.assertEqual(result["rules"][0]["filters"]["minCreationTime"], "2020-02-19T16:05:00Z")

        self.kwargs.update({
            'policy_id': result["policyId"],
            'rule_id': result["rules"][0]["ruleId"]
        })

        # Get policy properties from destination account
        self.cmd('storage account blob-inventory-policy show -g {rg} -n {dest_sc} --policy-id {policy_id}') \
            .assert_with_checks(JMESPathCheck('type', "Microsoft.Storage/storageAccounts/objectReplicationPolicies")) \
            .assert_with_checks(JMESPathCheck('sourceAccount', source_account)) \
            .assert_with_checks(JMESPathCheck('destinationAccount', destination_account)) \
            .assert_with_checks(JMESPathCheck('rules[0].sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].destinationContainer', dest_container))

        # Add rules
        src_container1 = self.create_container(src_account_info)
        dest_container1 = self.create_container(dest_account_info)
        self.cmd('storage account blob-inventory-policy rule list -g {rg} -n {dest_sc} --policy-id {policy_id}')\
            .assert_with_checks(JMESPathCheck('length(@)', 1))
        self.cmd('storage account blob-inventory-policy rule show -g {rg} -n {dest_sc} --rule-id {rule_id} --policy-id {policy_id}')\
            .assert_with_checks(JMESPathCheck('ruleId', result["rules"][0]["ruleId"])) \
            .assert_with_checks(JMESPathCheck('sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('destinationContainer', dest_container))

        result = self.cmd('storage account blob-inventory-policy rule add -g {} -n {} --policy-id {} -d {} -s {} -t "2020-02-19T16:05:00Z"'.format(
            resource_group, destination_account, self.kwargs["policy_id"], dest_container1, src_container1)).get_output_in_json()
        self.assertEqual(result["rules"][0]["filters"]["minCreationTime"], "2020-02-19T16:05:00Z")

        self.cmd('storage account blob-inventory-policy rule list -g {rg} -n {dest_sc} --policy-id {policy_id}')\
            .assert_with_checks(JMESPathCheck('length(@)', 2))

        # Update rules
        self.cmd('storage account blob-inventory-policy rule update -g {} -n {} --policy-id {} --rule-id {} --prefix-match blobA blobB -t "2020-02-20T16:05:00Z"'.format(
            resource_group, destination_account, result['policyId'], result['rules'][1]['ruleId'])) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[0]', 'blobA')) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[1]', 'blobB')) \
            .assert_with_checks(JMESPathCheck('filters.minCreationTime', '2020-02-20T16:05:00Z'))

        self.cmd('storage account blob-inventory-policy rule show -g {} -n {} --policy-id {} --rule-id {}'.format(
            resource_group, destination_account, result['policyId'], result['rules'][1]['ruleId'])) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[0]', 'blobA')) \
            .assert_with_checks(JMESPathCheck('filters.prefixMatch[1]', 'blobB')) \
            .assert_with_checks(JMESPathCheck('filters.minCreationTime', '2020-02-20T16:05:00Z'))

        # Remove rules
        self.cmd('storage account blob-inventory-policy rule remove -g {} -n {} --policy-id {} --rule-id {}'.format(
            resource_group, destination_account, result['policyId'], result['rules'][1]['ruleId']))
        self.cmd('storage account blob-inventory-policy rule list -g {rg} -n {dest_sc} --policy-id {policy_id}') \
            .assert_with_checks(JMESPathCheck('length(@)', 1))

        # Set ORS policy to source account
        with self.assertRaisesRegex(CLIError, 'ValueError: Please specify --policy-id with auto-generated policy id'):
            self.cmd('storage account blob-inventory-policy create -g {rg} -n {src_sc} -d {dest_sc} -s {src_sc} --dcont {dcont} --scont {scont}')

        import json
        temp_dir = self.create_temp_dir()
        policy_file = os.path.join(temp_dir, "policy.json")
        with open(policy_file, "w") as f:
            policy = self.cmd('storage account blob-inventory-policy show -g {rg} -n {dest_sc} --policy-id {policy_id}')\
                .get_output_in_json()
            json.dump(policy, f)
        self.kwargs['policy'] = policy_file
        self.cmd('storage account blob-inventory-policy create -g {rg} -n {src_sc} -p @"{policy}"')\
            .assert_with_checks(JMESPathCheck('type', "Microsoft.Storage/storageAccounts/objectReplicationPolicies")) \
            .assert_with_checks(JMESPathCheck('sourceAccount', source_account)) \
            .assert_with_checks(JMESPathCheck('destinationAccount', destination_account)) \
            .assert_with_checks(JMESPathCheck('rules[0].sourceContainer', src_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].destinationContainer', dest_container)) \
            .assert_with_checks(JMESPathCheck('rules[0].filters.minCreationTime', '2020-02-19T16:05:00Z'))

        # Update ORS policy
        self.cmd('storage account blob-inventory-policy update -g {} -n {} --policy-id {} --source-account {}'.format(
            resource_group, destination_account, self.kwargs["policy_id"], new_account)) \
            .assert_with_checks(JMESPathCheck('sourceAccount', new_account))

        # Delete policy from destination and source account
        self.cmd('storage account blob-inventory-policy delete -g {rg} -n {src_sc} --policy-id {policy_id}')
        self.cmd('storage account blob-inventory-policy list -g {rg} -n {src_sc}') \
            .assert_with_checks(JMESPathCheck('length(@)', 0))

        self.cmd('storage account blob-inventory-policy delete -g {rg} -n {dest_sc} --policy-id {policy_id}')
        self.cmd('storage account blob-inventory-policy list -g {rg} -n {dest_sc}') \
            .assert_with_checks(JMESPathCheck('length(@)', 0))
