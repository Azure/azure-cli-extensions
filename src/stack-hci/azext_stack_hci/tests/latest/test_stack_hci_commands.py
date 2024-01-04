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
            'cluster_name': self.create_random_name('cluster', 15),
            'app_name': self.create_random_name('app', 15)
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']

        cluster = self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id} --tags key0=value0 --mi-system-assigned', checks=[
            self.check('name', '{cluster_name}'),
            self.check('tags', {'key0': 'value0'}),
            self.check('type', 'microsoft.azurestackhci/clusters'),
            self.check('identity.type', 'SystemAssigned')
        ]).get_output_in_json()
        self.kwargs.update({
            'cluster_id': cluster['id']
        })
        self.cmd('stack-hci cluster create-identity --cluster-name {cluster_name} -g {rg}')
        self.cmd('stack-hci cluster list -g {rg}', checks=[
            self.check('length(@)', 1),
            self.check('@[0].name', '{cluster_name}'),
            self.check('[0].identity.type', 'SystemAssigned'),
            self.check('[0].type', 'microsoft.azurestackhci/clusters')
        ])
        self.cmd('stack-hci cluster update -n {cluster_name} -g {rg} --tags key0=value1')
        self.cmd('stack-hci cluster show -n {cluster_name} -g {rg}', checks=[
            self.check('name', '{cluster_name}'),
            self.check('tags', {'key0': 'value1'}),
            self.check('type', 'microsoft.azurestackhci/clusters'),
            self.exists('aadApplicationObjectId'),
            self.exists('aadServicePrincipalObjectId')
        ])
        self.cmd('stack-hci cluster show --ids {cluster_id}', checks=[
            self.check('name', '{cluster_name}'),
            self.check('tags', {'key0': 'value1'}),
            self.check('type', 'microsoft.azurestackhci/clusters'),
            self.exists('aadApplicationObjectId'),
            self.exists('aadServicePrincipalObjectId')
        ])
        self.cmd('stack-hci cluster delete -n {cluster_name} -g {rg} --yes')

    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_arc_setting', location='eastus')
    def test_stack_hci_arc_setting_crud(self):
        self.kwargs.update({
            'cluster_name': self.create_random_name('cluster', 15),
            'app_name': self.create_random_name('app', 15)
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']
        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id}')

        self.cmd('stack-hci arc-setting create -n default -g {rg} --cluster-name {cluster_name} --connectivity-properties {{enabled:True,serviceConfigurations:[{{port:7789,serviceName:WAC}}]}}', checks=[
            self.check('name', 'default'),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings'),
            self.check('connectivityProperties.enabled', True),
            self.check('connectivityProperties.serviceConfigurations[0].serviceName', 'WAC'),
            self.check('connectivityProperties.serviceConfigurations[0].port', 7789)
        ])
        self.cmd('stack-hci arc-setting update -n default -g {rg} --cluster-name {cluster_name} --connectivity-properties {{enabled:True,serviceConfigurations:[{{port:7788,serviceName:WAC}}]}}', checks=[
            self.check('name', 'default'),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings'),
            self.check('connectivityProperties.enabled', True),
            self.check('connectivityProperties.serviceConfigurations[0].serviceName', 'WAC'),
            self.check('connectivityProperties.serviceConfigurations[0].port', 7788)
        ])
        self.cmd('stack-hci arc-setting create-identity -n default --cluster-name {cluster_name} -g {rg} ')
        self.cmd('stack-hci arc-setting consent-and-install-default-extension -g {rg} --arc-setting-name default --cluster-name {cluster_name}', checks=[
            self.check('name', 'default'),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings'),
            self.check('defaultExtensions[0].category', 'ProductQualityAndSupport')
        ])
        self.cmd('stack-hci arc-setting initialize-disable-proces -g {rg} --arc-setting-name default --cluster-name {cluster_name}')
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
            'cluster_name': self.create_random_name('cluster', 15),
            'app_name': self.create_random_name('app', 15),
            'type': 'MicrosoftMonitoringAgent',
            'publisher': 'Microsoft.Compute'
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']
        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id}')
        self.cmd('stack-hci arc-setting create -n default -g {rg} --cluster-name {cluster_name}')
        self.cmd('stack-hci extension create -n {type} -g {rg} --cluster-name {cluster_name} --arc-setting-name default --settings "{{\'workspaceId\': \'xx\', \'port\': \'6516\'}}" --protected-settings "{{\'workspaceKey\': \'xx\'}}" --publisher {publisher} --type {type} --type-handler-version 1.10', checks=[
            self.check('name', self.kwargs['type']),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings/extensions'),
            self.check('extensionParameters.settings.workspaceId', 'xx'),
            self.check('extensionParameters.settings.port', '6516')
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

    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_cluster', location='eastus')
    def test_stack_hci_cluster_identity(self):
        self.kwargs.update({
            'cluster_name': self.create_random_name('cluster', 15),
            'cluster_name1': self.create_random_name('cluster', 15),
            'app_name': self.create_random_name('app', 15)
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']

        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id} --tags key0=value0 --mi-system-assigned', checks=[
            self.check('identity.type', 'SystemAssigned')
        ])
        self.cmd('stack-hci cluster create -n {cluster_name1} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id}')
        self.cmd('stack-hci cluster identity assign --cluster-name {cluster_name1} -g {rg} --system-assigned', checks=[
            self.check('type', 'SystemAssigned')
        ])
        self.cmd('stack-hci cluster identity remove --cluster-name {cluster_name1} -g {rg} --system-assigned', checks=[
            self.check('type', 'None')
        ])
