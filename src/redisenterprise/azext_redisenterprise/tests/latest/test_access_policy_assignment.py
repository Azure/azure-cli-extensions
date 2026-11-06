# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse


class RedisEnterpriseAccessPolicyAssignmentScenarioTest(ScenarioTest):

    @AllowLargeResponse(size_kb=9999)
    @ResourceGroupPreparer(name_prefix='clitest-redisenterprise-policy-', location='eastus2euap')
    def test_redisenterprise_access_policy_assignment(self, resource_group):
        self.kwargs.update({
            'cluster': self.create_random_name(prefix='clitest-policy-', length=23),
            'object_id': str(self.create_guid()),
            'assignment': 'cliTestAssignment',
        })
        self.cmd('redisenterprise create -g {rg} --cluster-name {cluster} --location eastus2euap '
                 '--sku Balanced_B1 --public-network-access Enabled --access-keys-auth Disabled')
        assignment = ('redisenterprise database access-policy-assignment {} -g {{rg}} '
                      '--cluster-name {{cluster}} --database-name default '
                      '--access-policy-assignment-name {{assignment}}')
        self.cmd(assignment.format('create') + ' --access-policy-name default --object-id {object_id}', checks=[
            self.check('name', '{assignment}'),
            self.check('accessPolicyName', 'default'),
            self.check('user.objectId', '{object_id}'),
            self.check('provisioningState', 'Succeeded'),
        ])
        self.cmd(assignment.format('show'), checks=[
            self.check('accessPolicyName', 'default'),
            self.check('user.objectId', '{object_id}'),
        ])
        self.cmd('redisenterprise database access-policy-assignment list -g {rg} '
                 '--cluster-name {cluster} --database-name default', checks=[
                     self.check('length(@)', 1),
                     self.check('[0].name', '{assignment}'),
                     self.check('[0].accessPolicyName', 'default'),
                     self.check('[0].user.objectId', '{object_id}'),
                 ])
        self.cmd(assignment.format('update') + ' --access-policy-name default', checks=[
            self.check('accessPolicyName', 'default'),
            self.check('user.objectId', '{object_id}'),
        ])
        self.cmd(assignment.format('delete') + ' -y')
        self.cmd('redisenterprise database access-policy-assignment list -g {rg} '
                 '--cluster-name {cluster} --database-name default', checks=[
                     self.check('length(@)', 0),
                 ])
