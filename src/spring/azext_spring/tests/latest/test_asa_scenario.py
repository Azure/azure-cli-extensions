# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from knack.util import CLIError
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer, StorageAccountPreparer, record_only)

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
            'domain': 'cli.asc-test.net',
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

    @ResourceGroupPreparer()
    @StorageAccountPreparer()
    def test_persistent_storage(self, resource_group, storage_account):
        template = 'storage account keys list -n {} -g {} --query "[0].value" -otsv'
        accountkey = self.cmd(template.format(storage_account, resource_group)).output

        self.kwargs.update({
            'storageType': 'StorageAccount',
            'storage': 'test-storage-name',
            'app': 'test-app',
            'serviceName': 'cli-unittest',
            'location': 'centralus',
            'accountKey': accountkey,
            'resource_group': resource_group,
            'storage_account': storage_account,
        })

        self.cmd('spring create -n {serviceName} -g {resource_group} -l {location}')

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

        self.cmd('spring delete -n {serviceName} -g {rg}')

class StartStopAscTest(ScenarioTest):

    def test_stop_and_start_service(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest-start-stop',
            'resource_group': 'cli-group',
            'location': 'eastus2euap'
        })

        self.cmd('group create -n {resource_group} -l {location}')
        self.cmd('spring create -n {serviceName} -g {resource_group} -l {location}')
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

        self.cmd('spring delete -n {serviceName} -g {resource_group} --no-wait')

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


class CustomImageTest(ScenarioTest):

    def test_app_deploy_container(self):
        self.kwargs.update({
            'app': 'test-container',
            'serviceName': 'cli-unittest',
            'containerImage': 'springio/gs-spring-boot-docker',
            'resourceGroup': 'cli',
            'location': 'centralindia'
        })

        self.cmd('group create -n {resourceGroup} -l {location}')
        self.cmd('spring create -n {serviceName} -g {resourceGroup}')

        self.cmd('spring app create -s {serviceName} -g {resourceGroup} -n {app}')

        self.cmd('spring app deploy -g {resourceGroup} -s {serviceName} -n {app} --container-image {containerImage}', checks=[
            self.check('name', 'default'),
            self.check('properties.source.type', 'Container'),
            self.check('properties.source.customContainer.containerImage', '{containerImage}'),
            self.check('properties.source.customContainer.languageFramework', None),
        ])

        self.cmd('spring app deploy -g {resourceGroup} -s {serviceName} -n {app} --container-image {containerImage} --container-command "java" --container-args "-cp /app/resources:/app/classes:/app/libs/* hello.Application"', checks=[
            self.check('name', 'default'),
            self.check('properties.source.type', 'Container'),
            self.check('properties.source.customContainer.containerImage', '{containerImage}'),
            self.check('properties.source.customContainer.command', ['java']),
            self.check('properties.source.customContainer.args', ['-cp', '/app/resources:/app/classes:/app/libs/*', 'hello.Application']),
        ])

        self.cmd('spring app deployment create -g {resourceGroup} -s {serviceName} --app {app} -n green --container-image {containerImage} --language-framework springboot', checks=[
            self.check('name', 'green'),
            self.check('properties.source.type', 'Container'),
            self.check('properties.source.customContainer.containerImage', '{containerImage}'),
            self.check('properties.source.customContainer.languageFramework', 'springboot'),
        ])


class RemoteDebuggingTest(ScenarioTest):
    def test_remote_debugging(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test.jar').replace("\\", "/")
        self.kwargs.update({
            'app': 'test-remote-debugging',
            'serviceName': 'cli-unittest',
            'resourceGroup': 'cli',
            'location': 'centralindia',
            'deployment': 'default',
            'file': file_path
        })

        self.cmd('spring app create -s {serviceName} -g {resourceGroup} -n {app}')

        # remote debugging can only be supported for jar, here will throw exception for default banner
        self.cmd(
            'spring app enable-remote-debugging -n {app} -g {resourceGroup} -s {serviceName} -d {deployment}', expect_failure=True)

        self.cmd(
            'spring app disable-remote-debugging -n {app} -g {resourceGroup} -s {serviceName} -d {deployment}')

        self.cmd(
            'spring app get-remote-debugging-config -n {app} -g {resourceGroup} -s {serviceName} -d {deployment}',
            checks=[
                self.check('enabled', False)
            ])


class AppConnectTest(ScenarioTest):

    def test_app_connect(self):
        self.kwargs.update({
            'app': 'test-app',
            'serviceName': 'cli-unittest',
            'resourceGroup': 'cli'
        })

        # Test the failed case only since this is an interactive command
        self.cmd('spring app connect -s {serviceName} -g {resourceGroup} -n {app} --shell-cmd /bin/placeholder', expect_failure=True)
