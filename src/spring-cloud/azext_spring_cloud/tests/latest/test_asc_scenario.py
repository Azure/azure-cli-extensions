# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from knack.util import CLIError
from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class CertificateTests(ScenarioTest):
    def test_import_certificate(self):
        self.kwargs.update({
            'cert': 'test-cert',
            'keyVaultUri': 'https://integration-test.vault-int.azure-int.net/',
            'KeyVaultCertName': 'cli-ut'
        })

        self.cmd('spring-cloud certificate add --name {cert} --vault-uri {keyVaultUri} --vault-certificate-name {KeyVaultCertName}', checks=[
            self.check('name', '{cert}')
        ])

    def test_show_certificate(self):
        self.kwargs.update({
            'cert': 'test-cert',
        })

        self.cmd('spring-cloud certificate show --name {cert}', checks=[
            self.check('name', '{cert}')
        ])

    def test_list_certificate(self):
        result = self.cmd('spring-cloud certificate list').get_output_in_json()
        self.assertTrue(len(result) > 0)

    def test_bind_custom_domain(self):
        self.kwargs.update({
            'domain': 'cli.asc-test.net',
            'app': 'test-app'
        })

        self.cmd('spring-cloud app custom-domain bind --domain-name {domain} --app {app}', checks=[
            self.check('name', '{domain}')
        ])

    def test_show_custom_domain(self):
        self.kwargs.update({
            'domain': 'cli.asc-test.net',
            'app': 'test-app'
        })

        self.cmd('spring-cloud app custom-domain show --domain-name {domain} --app {app}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.appName', '{app}')
        ])

    def test_list_custom_domain(self):
        self.kwargs.update({
            'app': 'test-app'
        })

        result = self.cmd('spring-cloud app custom-domain list --app {app}').get_output_in_json()
        self.assertTrue(len(result) > 0)

    def test_update_custom_domain(self):
        self.kwargs.update({
            'domain': 'cli.asc-test.net',
            'cert': 'test-cert',
            'app': 'test-app'
        })

        self.cmd('spring-cloud app custom-domain update --domain-name cli.asc-test.net --certificate test-cert --app test-app', checks=[
            self.check('name', '{domain}'),
            self.check('properties.appName', '{app}'),
            self.check('properties.certName', '{cert}')
        ])

    def test_unbind_custom_domain(self):
        self.kwargs.update({
            'domain': 'cli.asc-test.net',
            'cert': 'test-cert',
            'app': 'test-app'
        })

        self.cmd('spring-cloud app custom-domain unbind --domain-name {domain} --app {app}')
        self.cmd('spring-cloud app custom-domain remove --domain-name {domain} --app {app}', expect_failure=True)

    def test_delete_certificate(self):
        self.kwargs.update({
           'cert': 'test-cert',
        })

        self.cmd('spring-cloud certificate remove --name {cert}')
        self.cmd('spring-cloud certificate show --name {cert}', expect_failure=True)