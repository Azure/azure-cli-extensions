# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest
)


class StackHciClientTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_', location='eastus')
    def test_stack_hci_cluster_crud(self):
        self.kwargs.update({
            'cluster_name': 'cli-test-cluster',
            'app_name': 'cli-test-app'
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']

        self.cmd(
            'stack-hci cluster create -n {cluster_name} -g {rg} '
            '--aad-client-id {client_id} --aad-tenant-id {tenant_id} --tags key0=value0',
            checks=[
                self.check('name', '{cluster_name}'),
                self.check('tags', {'key0': 'value0'}),
                self.check('type', 'microsoft.azurestackhci/clusters')
            ]
        )
        self.cmd(
            'stack-hci cluster list -g {rg}',
            checks=[
                self.check('length(@)', 1),
                self.check('@[0].name', '{cluster_name}')
            ]
        )
        self.cmd('stack-hci cluster update -n {cluster_name} -g {rg} --tags key0=value1')
        self.cmd(
            'stack-hci cluster show -n {cluster_name} -g {rg}',
            checks=[
                self.check('name', '{cluster_name}'),
                self.check('tags', {'key0': 'value1'}),
                self.check('type', 'microsoft.azurestackhci/clusters')
            ]
        )
        self.cmd('stack-hci cluster delete -n {cluster_name} -g {rg} --yes')
        self.cmd('ad app delete --id {client_id}')

    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_', location='eastus')
    def test_stack_hci_arc_setting_crud(self):
        pass
