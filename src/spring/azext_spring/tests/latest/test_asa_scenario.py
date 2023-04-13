# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, StorageAccountPreparer, record_only)
from .custom_preparers import (SpringPreparer, SpringResourceGroupPreparer)
from .custom_dev_setting_constant import SpringTestEnvironmentEnum

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


@record_only()
class CustomDomainTests(ScenarioTest):

    def test_bind_cert_to_domain(self):
        self.kwargs.update({
            'cert': 'test-cert',
            'keyVaultUri': 'https://integration-test-prod.vault.azure.net/',
            'KeyVaultCertName': 'cli-unittest',
            'domain': 'clitest.asc-test.net',
            'app': 'test-custom-domain',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
        })
        self.cmd('spring app create -n {app} -s {serviceName} -g {rg}')

        self.cmd('spring certificate add --name {cert} --vault-uri {keyVaultUri} --vault-certificate-name {KeyVaultCertName} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{cert}')
        ])

        self.cmd('spring certificate show --name {cert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{cert}')
        ])

        result = self.cmd('spring certificate list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring app custom-domain bind --domain-name {domain} --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}')
        ])

        self.cmd('spring app custom-domain show --domain-name {domain} --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.appName', '{app}')
        ])

        result = self.cmd('spring app custom-domain list --app {app} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring app custom-domain update --domain-name {domain} --certificate {cert} --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.appName', '{app}'),
            self.check('properties.certName', '{cert}')
        ])

        self.cmd('spring app custom-domain unbind --domain-name {domain} --app {app} -g {rg} -s {serviceName}')
        self.cmd('spring app custom-domain show --domain-name {domain} --app {app} -g {rg} -s {serviceName}', expect_failure=True)

        self.cmd('spring certificate remove --name {cert} -g {rg} -s {serviceName}')
        self.cmd('spring certificate show --name {cert} -g {rg} -s {serviceName}', expect_failure=True)


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

        self.cmd('spring storage add --name {storage} --storage-type {storageType} --account-name {storage_account} --account-key {accountKey} -g {resource_group} -s {serviceName}', checks=[
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


class SslTests(ScenarioTest):

    def test_load_public_cert_to_app(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        baltiCertPath = os.path.join(py_path, 'files/BaltimoreCyberTrustRoot.crt.pem').replace("\\","/")
        digiCertPath = os.path.join(py_path, 'files/DigiCertGlobalRootCA.crt.pem').replace("\\","/")
        loadCertPath = os.path.join(py_path, 'files/load_certificate.json').replace("\\","/")

        self.kwargs.update({
            'cert': 'test-cert',
            'keyVaultUri': 'https://integration-test-prod.vault.azure.net/',
            'KeyVaultCertName': 'cli-unittest',
            'baltiCert': 'balti-cert',
            'digiCert': 'digi-cert',
            'baltiCertPath': baltiCertPath,
            'digiCertPath': digiCertPath,
            'loadCertPath': loadCertPath,
            'app': 'test-app-cert',
            'serviceName': 'cli-unittest',
            'rg': 'cli'
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
        self.assertTrue(len(cert_result) == 2)

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
