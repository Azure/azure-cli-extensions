# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, StorageAccountPreparer, record_only)
from azure.cli.testsdk.reverse_dependency import (
    get_dummy_cli,
)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer, SpringAppNamePreparer,
                               SpringSubResourceWrapper)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class ByosTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @StorageAccountPreparer()
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    def test_persistent_storage(self, resource_group, storage_account, spring):
        template = 'storage account keys list -n {} -g {} --query "[0].value" -otsv'
        accountkey = self.cmd(template.format(storage_account, resource_group)).output

        self.kwargs.update({
            'storageType': 'StorageAccount',
            'storage': 'test-storage-name',
            'app': 'test-app',
            'serviceName': spring,
            'location': 'centralus',
            'accountKey': accountkey,
            'resource_group': resource_group,
            'storage_account': storage_account,
        })

        self.cmd(
            'spring storage add --name {storage} --storage-type {storageType} --account-name {storage_account} --account-key {accountKey} -g {resource_group} -s {serviceName}',
            checks=[
                self.check('name', '{storage}'),
                self.check('properties.storageType', '{storageType}'),
                self.check('properties.accountName', '{storage_account}'),
            ])

        self.cmd('spring storage show --name {storage} -g {resource_group} -s {serviceName}', checks=[
            self.check('name', '{storage}')
        ])

        result = self.cmd('spring storage list -g {resource_group} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring storage remove --name {storage} -g {resource_group} -s {serviceName}')
        self.cmd('spring storage show --name {storage} -g {resource_group} -s {serviceName}', expect_failure=True)


class StartStopAscTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD_START_STOP['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD_START_STOP['spring'])
    def test_stop_and_start_service(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'resource_group': resource_group,
        })

        self.cmd('spring stop -n {serviceName} -g {resource_group}')
        self.cmd('spring show --name {serviceName} -g {resource_group}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.powerState', 'Stopped')
        ])

        self.cmd('spring start -n {serviceName} -g {resource_group}')
        self.cmd('spring show --name {serviceName} -g {resource_group}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.powerState', 'Running')
        ])


class CertTearDown(SpringSubResourceWrapper):
    def __init__(self,
                 resource_group_parameter_name='resource_group',
                 spring_parameter_name='spring'):
        super(CertTearDown, self).__init__()
        self.cli_ctx = get_dummy_cli()
        self.resource_group_parameter_name = resource_group_parameter_name
        self.spring_parameter_name = spring_parameter_name

    def create_resource(self, *_, **kwargs):
        self.resource_group = self._get_resource_group(**kwargs)
        self.spring = self._get_spring(**kwargs)

    def remove_resource(self, *_, **__):
        self.live_only_execute(self.cli_ctx,
                               'spring certificate remove -g {}  -s {} -n balti-cert'.format(self.resource_group,
                                                                                             self.spring))
        self.live_only_execute(self.cli_ctx,
                               'spring certificate remove -g {}  -s {} -n digi-cert'.format(self.resource_group,
                                                                                            self.spring))


@record_only()
class SslTests(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    @SpringAppNamePreparer(skip_delete=True)
    @CertTearDown()
    def test_load_public_cert_to_app(self, resource_group, spring, app):
        py_path = os.path.abspath(os.path.dirname(__file__))
        baltiCertPath = os.path.join(py_path, 'files/BaltimoreCyberTrustRoot.crt.pem').replace("\\", "/")
        digiCertPath = os.path.join(py_path, 'files/DigiCertGlobalRootCA.crt.pem').replace("\\", "/")
        loadCertPath = os.path.join(py_path, 'files/load_certificate.json').replace("\\", "/")

        self.kwargs.update({
            'baltiCert': 'balti-cert',
            'digiCert': 'digi-cert',
            'baltiCertPath': baltiCertPath,
            'digiCertPath': digiCertPath,
            'loadCertPath': loadCertPath,
            'app': app,
            'serviceName': spring,
            'rg': resource_group
        })

        self.cmd(
            'spring certificate add --name {digiCert} -f {digiCertPath} -g {rg} -s {serviceName}',
            checks=[
                self.check('name', '{digiCert}')
            ])

        self.cmd(
            'spring certificate add --name {baltiCert} -f {baltiCertPath} -g {rg} -s {serviceName}',
            checks=[
                self.check('name', '{baltiCert}')
            ])

        self.cmd(
            'spring certificate show --name {digiCert} -g {rg} -s {serviceName}', checks=[
                self.check('name', '{digiCert}')
            ])

        self.cmd(
            'spring certificate show --name {baltiCert} -g {rg} -s {serviceName}', checks=[
                self.check('name', '{baltiCert}')
            ])

        cert_result = self.cmd(
            'spring certificate list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(cert_result) >= 2)  # in case there are other cert resources

        self.cmd(
            'spring app create --name {app} -f {loadCertPath} -g {rg} -s {serviceName}')

        self.cmd(
            'spring app append-loaded-public-certificate --name {app} --certificate-name {digiCert} --load-trust-store true -g {rg} -s {serviceName}')

        app_result = self.cmd(
            'spring certificate list-reference-app --name {digiCert} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(app_result) > 0)

        app_result = self.cmd(
            'spring certificate list-reference-app --name {digiCert} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(app_result) > 0)

        self.cmd('spring app delete --name {app}  -g {rg} -s {serviceName}')


class FlushVirtualNetworkDnsSettingTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    def test_flush_virtualnetwork_dns_settings_service(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'resource_group': resource_group,
        })

        self.cmd('spring flush-virtualnetwork-dns-settings -n {serviceName} -g {resource_group}')
        self.cmd('spring show --name {serviceName} -g {resource_group}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.powerState', 'Running')
        ])


class PlannedMaintenanceTest(ScenarioTest):

    @SpringResourceGroupPreparer(dev_setting_name=SpringTestEnvironmentEnum.STANDARD['resource_group_name'])
    @SpringPreparer(**SpringTestEnvironmentEnum.STANDARD['spring'])
    def test_enable_planned_maintenance(self, resource_group, spring):
        self.kwargs.update({
            'serviceName': spring,
            'resource_group': resource_group,
        })

        self.cmd(
            'spring update -g {resource_group} -n {serviceName} --enable-planned-maintenance --planned-maintenance-day Friday --planned-maintenance-start-hour 10',
            checks=[
                self.check('properties.maintenanceScheduleConfiguration.day', 'Friday'),
                self.check('properties.maintenanceScheduleConfiguration.hour', 10)
            ])
