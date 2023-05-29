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

        cluster = self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id} --tags key0=value0 --type SystemAssigned', checks=[
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

        self.cmd('stack-hci arc-setting create -n default -g {rg} --cluster-name {cluster_name}', checks=[
            self.check('name', 'default'),
            self.check('type', 'microsoft.azurestackhci/clusters/arcsettings')
        ])
        self.cmd('stack-hci arc-setting create-identity -n default --cluster-name {cluster_name} -g {rg}')
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
        self.cmd('stack-hci extension create -n {type} -g {rg} --cluster-name {cluster_name} --arc-setting-name default --settings {{workspaceId:xx}} --protected-settings {{workspaceKey:xx}} --publisher {publisher} --type {type} --type-handler-version 1.10', checks=[
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

    @ResourceGroupPreparer(name_prefix='cli_test_stack_hci_extension', location='eastus')
    def test_stack_hci_cluster_updates_crud(self):
        self.kwargs.update({
            'cluster_name': self.create_random_name('cluster', 15),
            'app_name': self.create_random_name('app', 15),
            'updates_name': self.create_random_name('updates_', 15),
            'updates_run_name': self.create_random_name('updates_', 15)
        })
        self.kwargs['client_id'] = self.cmd('ad app create --display-name {app_name}').get_output_in_json()['appId']
        self.kwargs['tenant_id'] = self.cmd('account show').get_output_in_json()['tenantId']
        self.cmd('stack-hci cluster create -n {cluster_name} -g {rg} --aad-client-id {client_id} --aad-tenant-id {tenant_id}')
        self.cmd('stack-hci cluster-update create -g {rg} --cluster-name {cluster_name} -n {updates_name}', checks=[
            self.check('name', '{updates_name}')
        ])
        self.cmd('stack-hci cluster-update update -g {rg} --cluster-name {cluster_name} -n {updates_name} --description test --package-size-in-mb 10 --additional-properties test --availability-type local --version 1.0.0 --display-name test --publisher clitest', checks=[
            self.check('name', '{updates_name}'),
            self.check('additionalProperties', 'test'),
            self.check('availabilityType', 'Local'),
            self.check('description', 'test'),
            self.check('displayName', 'test'),
            self.check('packageSizeInMb', 10.0),
            self.check('publisher', 'clitest')
        ])
        self.cmd('stack-hci cluster-update show -g {rg} --cluster-name {cluster_name} -n {updates_name}', checks=[
            self.check('name', '{updates_name}'),
            self.check('additionalProperties', 'test'),
            self.check('availabilityType', 'Local'),
            self.check('description', 'test'),
            self.check('displayName', 'test'),
            self.check('packageSizeInMb', 10.0),
            self.check('publisher', 'clitest')
        ])
        self.cmd('stack-hci cluster-update list -g {rg} --cluster-name {cluster_name}', checks=[
            self.check('[0].name', '{updates_name}'),
            self.check('[0].additionalProperties', 'test'),
            self.check('[0].availabilityType', 'Local'),
            self.check('[0].description', 'test'),
            self.check('[0].displayName', 'test'),
            self.check('[0].packageSizeInMb', 10.0),
            self.check('[0].publisher', 'clitest')
        ])

        self.cmd('stack-hci cluster-update summary create --cluster-name {cluster_name} -g {rg}', checks=[
            self.check('name', 'default')
        ])
        self.cmd('stack-hci cluster-update summary update --cluster-name {cluster_name} -g {rg} --current-version 1.0.0  --hardware-model PowerEdge --oem-family DellEMC --package-versions [{{packageType:OEM,version:2.2.2108.6}},{{packageType:Services,version:4.2203.2.32}}]', checks=[
            self.check('name', 'default'),
            self.check('currentVersion', '1.0.0'),
            self.check('hardwareModel', 'PowerEdge'),
            self.check('oemFamily', 'DellEMC'),
            self.check('packageVersions[0].packageType', 'OEM'),
            self.check('packageVersions[0].version', '2.2.2108.6'),
            self.check('packageVersions[1].packageType', 'Services'),
            self.check('packageVersions[1].version', '4.2203.2.32')
        ])
        self.cmd('stack-hci cluster-update summary show --cluster-name {cluster_name} -g {rg}', checks=[
            self.check('name', 'default'),
            self.check('currentVersion', '1.0.0'),
            self.check('hardwareModel', 'PowerEdge'),
            self.check('oemFamily', 'DellEMC'),
            self.check('packageVersions[0].packageType', 'OEM'),
            self.check('packageVersions[0].version', '2.2.2108.6'),
            self.check('packageVersions[1].packageType', 'Services'),
            self.check('packageVersions[1].version', '4.2203.2.32')
        ])
        self.cmd('stack-hci cluster-update summary list --cluster-name {cluster_name} -g {rg}', checks=[
            self.check('[0].name', 'default'),
            self.check('[0].currentVersion', '1.0.0'),
            self.check('[0].hardwareModel', 'PowerEdge'),
            self.check('[0].oemFamily', 'DellEMC'),
            self.check('[0].packageVersions[0].packageType', 'OEM'),
            self.check('[0].packageVersions[0].version', '2.2.2108.6'),
            self.check('[0].packageVersions[1].packageType', 'Services'),
            self.check('[0].packageVersions[1].version', '4.2203.2.32')
        ])
        self.cmd('stack-hci cluster-update update-run create --cluster-name {cluster_name} -g {rg}  -n {updates_run_name} --update-name {updates_name}', checks=[
            self.check('name', '{updates_run_name}')
        ])
        self.cmd('stack-hci cluster-update update-run update --cluster-name {cluster_name} -g {rg}  -n {updates_run_name} --update-name {updates_name} --progress {{name:cli_update_test,description:update_test}}', checks=[
            self.check('name', '{updates_run_name}'),
            self.check('progress.description', 'update_test'),
            self.check('progress.name', 'cli_update_test')
        ])
        self.cmd('stack-hci cluster-update update-run show --cluster-name {cluster_name} -g {rg}  -n {updates_run_name} --update-name {updates_name}', checks=[
            self.check('name', '{updates_run_name}'),
            self.check('progress.description', 'update_test'),
            self.check('progress.name', 'cli_update_test')
        ])
        self.cmd('stack-hci cluster-update update-run list --cluster-name {cluster_name} -g {rg} --update-name {updates_name}', checks=[
            self.check('[0].name', '{updates_run_name}'),
            self.check('[0].progress.description', 'update_test'),
            self.check('[0].progress.name', 'cli_update_test')
        ])
        self.cmd('stack-hci cluster-update update-run delete --cluster-name {cluster_name} -g {rg}  -n {updates_run_name} --update-name {updates_name} -y')
        self.cmd('stack-hci cluster-update summary delete --cluster-name {cluster_name} -g {rg} -y')
        self.cmd('stack-hci cluster-update delete -g {rg} --cluster-name {cluster_name} -n {updates_name} -y')

