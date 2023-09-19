# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=line-too-long
# pylint: disable=unused-import

from azure.cli.testsdk import ScenarioTest, ResourceGroupPreparer
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .preparers import VaultPreparer

class ResourceGuardScenarioTest(ScenarioTest):

    def setUp(test):
        super().setUp()
        test.kwargs.update({
            'location': 'centraluseuap',
            'resourceGuardName':'clitest-resource-guard',
        })

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-resourceguard-', location='centraluseuap')
    def test_dataprotection_resource_guard_create_and_delete(test):
        test.cmd('az dataprotection resource-guard create -g "{rg}" -n "{resourceGuardName}"', checks=[
            test.check('name', "{resourceGuardName}")
        ])
        test.cmd('az dataprotection resource-guard list -g "{rg}"', checks=[
            test.check("length([?name == '{resourceGuardName}'])", 1)
        ])
        test.cmd('az dataprotection resource-guard show -g "{rg}" -n "{resourceGuardName}"', checks=[
            test.check('name', "{resourceGuardName}")
        ])
        test.cmd('az dataprotection resource-guard delete -g "{rg}" -n "{resourceGuardName}" -y')

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-resourceguard-', location='centraluseuap')
    def test_dataprotection_resource_guard_update(test):
        test.kwargs.update({
            'resourceType': 'Microsoft.RecoveryServices/vaults'
        })
        test.cmd('az dataprotection resource-guard create -g "{rg}" -n "{resourceGuardName}"', checks=[
            test.check('name', "{resourceGuardName}")
        ])
        test.cmd('az dataprotection resource-guard update -g "{rg}" -n "{resourceGuardName}" --resource-type "{resourceType}" --critical-operation-exclusion-list deleteProtection getSecurityPIN', checks=[
            test.check('length(properties.vaultCriticalOperationExclusionList)', 2)
        ])
        test.cmd('az dataprotection resource-guard list-protected-operations -g "{rg}" -n "{resourceGuardName}" --resource-type "Microsoft.RecoveryServices/vaults"', checks=[
            test.check('length(@)', 4)
        ])
        test.cmd('az dataprotection resource-guard update -g "{rg}" -n "{resourceGuardName}" --critical-operation-exclusion-list deleteProtection', checks=[
            test.check('length(properties.vaultCriticalOperationExclusionList)', 2)
        ])
        test.cmd('az dataprotection resource-guard update -g "{rg}" -n "{resourceGuardName}" --critical-operation-exclusion-list []', checks=[
            test.check('length(properties.vaultCriticalOperationExclusionList)', 2)
        ])
        test.cmd('az dataprotection resource-guard update -g "{rg}" -n "{resourceGuardName}"  --resource-type "{resourceType}" --tags Purpose="Testing"', checks=[
            test.check('tags.Purpose', "Testing"),
            test.check('length(properties.vaultCriticalOperationExclusionList)', 2)
        ])
        test.cmd('az dataprotection resource-guard update -g "{rg}" -n "{resourceGuardName}" --resource-type "{resourceType}" --critical-operation-exclusion-list []', checks=[
            test.check('length(properties.vaultCriticalOperationExclusionList)', 0)
        ])

    @AllowLargeResponse()
    @ResourceGroupPreparer(name_prefix='clitest-dpp-resourceguard-', location='centraluseuap')
    @VaultPreparer(name_prefix='clitest-dpp-resourceguard-vault-', soft_delete_state="Off")
    @ResourceGuardPreparer(parameter_name='resource_guard_1')
    @ResourceGuardPreparer(parameter_name='resource_guard_2')
    def test_dataprotection_resource_guard_mapping(test, vault_name, resource_guard_1, resource_guard_2):
        test.kwargs.update({
            'vaultName': vault_name,
            'resGuard1': resource_guard_1,
            'resGuard2': resource_guard_2
        })

        test.cmd('az dataprotection backup-vault resource-guard-mapping create -g {rg} -v {vaultName} --resource-guard-resource-id {resource_guard_id}', checks=[
            test.check('name', 'DppResourceGuardProxy')
        ])

        test.cmd('az dataprotection backup-vault resource-guard-mapping show -g {rg} -v {vaultName} -n "DppResourceGuardProxy"')

        print("In the test")
        print("RG: {rg}, Vault Name: {vaultName}, location: {location}")
        # test.cmd('az group list --query "[?location==\'{resource_group_location}\']"')
        test.cmd('az group list --query "[?location==\'{location}\']"')
        test.cmd('az dataprotection backup-vault show -g {rg} --vault-name {vaultName}', checks=[
            test.check('name', "{soft_delete_state}")
        ])

