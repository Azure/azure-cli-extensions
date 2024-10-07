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
        self.cmd('spring-cloud app create -n {app} -s {serviceName} -g {rg}')

        self.cmd('spring-cloud certificate add --name {cert} --vault-uri {keyVaultUri} --vault-certificate-name {KeyVaultCertName} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{cert}')
        ])

        self.cmd('spring-cloud certificate show --name {cert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{cert}')
        ])

        result = self.cmd('spring-cloud certificate list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring-cloud app custom-domain bind --domain-name {domain} --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}')
        ])

        self.cmd('spring-cloud app custom-domain show --domain-name {domain} --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.appName', '{app}')
        ])

        result = self.cmd('spring-cloud app custom-domain list --app {app} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring-cloud app custom-domain update --domain-name {domain} --certificate {cert} --app {app} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.appName', '{app}'),
            self.check('properties.certName', '{cert}')
        ])

        self.cmd('spring-cloud app custom-domain unbind --domain-name {domain} --app {app} -g {rg} -s {serviceName}')
        self.cmd('spring-cloud app custom-domain show --domain-name {domain} --app {app} -g {rg} -s {serviceName}', expect_failure=True)

        self.cmd('spring-cloud certificate remove --name {cert} -g {rg} -s {serviceName}')
        self.cmd('spring-cloud certificate show --name {cert} -g {rg} -s {serviceName}', expect_failure=True)


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

        self.cmd('spring-cloud create -n {serviceName} -g {resource_group} -l {location}')

        self.cmd('spring-cloud storage add --name {storage} --storage-type {storageType} --account-name {storage_account} --account-key {accountKey} -g {resource_group} -s {serviceName}', checks=[
            self.check('name', '{storage}'),
            self.check('properties.storageType', '{storageType}'),
            self.check('properties.accountName', '{storage_account}'),
        ])

        self.cmd('spring-cloud storage show --name {storage} -g {resource_group} -s {serviceName}', checks=[
            self.check('name', '{storage}')
        ])

        result = self.cmd('spring-cloud storage list -g {resource_group} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring-cloud storage remove --name {storage} -g {resource_group} -s {serviceName}')
        self.cmd('spring-cloud storage show --name {storage} -g {resource_group} -s {serviceName}', expect_failure=True)

        self.cmd('spring-cloud delete -n {serviceName} -g {rg}')

class StartStopAscTest(ScenarioTest):

    def test_stop_and_start_service(self):
        self.kwargs.update({
            'serviceName': 'cli-unittest',
            'resource_group': 'cli',
            'location': 'eastus'
        })

        self.cmd('group create -n {resource_group} -l {location}')
        self.cmd('spring-cloud create -n {serviceName} -g {resource_group} -l {location}')
        self.cmd('spring-cloud stop -n {serviceName} -g {resource_group}')
        self.cmd('spring-cloud show --name {serviceName} -g {resource_group}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.powerState', 'Stopped')
        ])

        self.cmd('spring-cloud start -n {serviceName} -g {resource_group}')
        self.cmd('spring-cloud show --name {serviceName} -g {resource_group}', checks=[
            self.check('properties.provisioningState', 'Succeeded'),
            self.check('properties.powerState', 'Running')
        ])

        self.cmd('spring-cloud delete -n {serviceName} -g {resource_group} --no-wait')

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
            'spring-cloud certificate add --name {digiCert} -f {digiCertPath} -g {rg} -s {serviceName}',
            checks=[
                self.check('name', '{digiCert}')
            ])

        self.cmd(
            'spring-cloud certificate add --name {baltiCert} -f {baltiCertPath} -g {rg} -s {serviceName}',
            checks=[
                self.check('name', '{baltiCert}')
            ])

        self.cmd(
            'spring-cloud certificate show --name {digiCert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{digiCert}')
        ])

        self.cmd(
            'spring-cloud certificate show --name {baltiCert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{baltiCert}')
        ])

        cert_result = self.cmd(
            'spring-cloud certificate list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(cert_result) == 2)

        self.cmd(
            'spring-cloud app create --name {app} -f {loadCertPath} -g {rg} -s {serviceName}')

        self.cmd(
            'spring-cloud app append-loaded-public-certificate --name {app} --certificate-name {digiCert} --load-trust-store true -g {rg} -s {serviceName}')

        app_result = self.cmd(
            'spring-cloud certificate list-reference-app --name {digiCert} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(app_result) > 0)

        app_result = self.cmd(
            'spring-cloud certificate list-reference-app --name {digiCert} -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(app_result) > 0)


class CustomImageTest(ScenarioTest):

    def test_app_deploy_container(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        file_path = os.path.join(py_path, 'files/test.jar').replace("\\","/")
        self.kwargs.update({
            'app': 'test-container',
            'serviceName': 'cli-unittest',
            'containerImage': 'springio/gs-spring-boot-docker',
            'resourceGroup': 'cli',
            'file': file_path
        })

        self.cmd('spring-cloud app create -s {serviceName} -g {resourceGroup} -n {app}')

        self.cmd('spring-cloud app deploy -g {resourceGroup} -s {serviceName} -n {app} --container-image {containerImage}', checks=[
            self.check('name', 'default'),
            self.check('properties.source.type', 'Container'),
            self.check('properties.source.customContainer.containerImage', '{containerImage}'),
        ])

        self.cmd('spring-cloud app deployment create -g {resourceGroup} -s {serviceName} --app {app} -n green'
                 + ' --container-image {containerImage} --registry-username PLACEHOLDER --registry-password PLACEHOLDER', checks=[
            self.check('name', 'green'),
        ])

        with self.assertRaisesRegex(CLIError, "Failed to wait for deployment instances to be ready"):
            self.cmd('spring-cloud app deploy -g {resourceGroup} -s {serviceName} -n {app} --artifact-path {file}')

        self.cmd('spring-cloud app deployment show -g {resourceGroup} -s {serviceName} -n default --app {app} ', checks=[
            self.check('name', 'default'),
            self.check('properties.source.type', 'Jar'),
            self.check('properties.source.runtimeVersion', 'Java_8'),
        ])
