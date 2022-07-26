# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

import json

from azure.cli.testsdk import (
    ResourceGroupPreparer,
    ScenarioTest
)


class StackHciClientTest(ScenarioTest):
    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_cluster', location='eastus')
    def test_stack_hci_cluster_crud(self):
        self.kwargs.update({
            'cluster_name': 'cli-test-cluster',
            'app_name': 'cli-test-app'
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']

        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id} --tags key0=value0', checks=[
            self.check('name', '{cluster_name}'),
            self.check('tags', {'key0': 'value0'}),
            self.check('type', 'microsoft.azurestackhci/clusters')
        ])
        self.cmd('stack-hci cluster create-identity --cluster-name {cluster_name} -g {rg}', checks=[
            self.check('status', 'Succeeded'),
        ])
        self.cmd('stack-hci cluster list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', '{cluster_name}')
        ])
        self.cmd('stack-hci cluster update -n {cluster_name} -g {rg} --tags key0=value1')
        self.cmd('stack-hci cluster show -n {cluster_name} -g {rg}', checks=[
            self.check('name', '{cluster_name}'),
            self.check('tags', {'key0': 'value1'}),
            self.check('type', 'microsoft.azurestackhci/clusters')
        ])
        self.cmd('stack-hci cluster delete -n {cluster_name} -g {rg} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_arc_setting', location='eastus')
    def test_stack_hci_arc_setting_crud(self):
        self.kwargs.update({
            'cluster_name': 'cli-test-cluster',
            'app_name': 'cli-test-app'
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']
        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id}')

        self.cmd('stack-hci arc-setting create -n default -g {rg} --cluster-name {cluster_name}', checks=[
            self.check('name', 'default'),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings')
        ])
        self.cmd('stack-hci arc-setting create-identity -n default --cluster-name {cluster_name} -g {rg}')
        self.cmd('stack-hci arc-setting list -g {rg} --cluster-name {cluster_name}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', 'default')
        ])
        self.cmd('stack-hci arc-setting show -n default -g {rg} --cluster-name {cluster_name}', checks=[
            self.check('name', 'default'),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings')
        ])
        self.cmd('stack-hci arc-setting generate-password -n default --cluster-name {cluster_name} -g {rg}', checks=[
            self.exists('secretText')
        ])
        self.cmd('stack-hci arc-setting delete -n default -g {rg} --cluster-name {cluster_name} --no-wait --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_extension', location='eastus')
    def test_stack_hci_extension_crud(self):
        self.kwargs.update({
            'cluster_name': 'cli-test-cluster',
            'app_name': 'cli-test-app',
            'type': 'MicrosoftMonitoringAgent',
            'publisher': 'Microsoft.Compute'
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']
        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id}')
        self.cmd('stack-hci arc-setting create -n default -g {rg} --cluster-name {cluster_name}')

        self.kwargs['settings'] = json.dumps({'workspaceId': 'xx'})
        self.kwargs['protected_settings'] = json.dumps({'workspaceKey': 'xx'})
        self.cmd('stack-hci extension create -n {type} -g {rg} --cluster-name {cluster_name} --arc-setting-name default --settings \'{settings}\' --protected-settings \'{protected_settings}\' --publisher {publisher} --type {type} --type-handler-version 1.10', checks=[
            self.check('name', self.kwargs['type']),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings/extensions')
        ])
        self.cmd('stack-hci extension list -g {rg} --cluster-name {cluster_name} --arc-setting-name default', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', self.kwargs['type'])
        ])
        self.cmd('stack-hci extension show -n {type} -g {rg} --cluster-name {cluster_name} --arc-setting-name default', checks=[
            self.check('name', self.kwargs['type']),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings/extensions')
        ])
        self.cmd('stack-hci extension delete -n {type} -g {rg} --cluster-name {cluster_name} --arc-setting-name default --no-wait --yes')
