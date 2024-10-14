# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from .recording_processors import KeyReplacer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))

class WebpubsubCustomCertificateScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super(WebpubsubCustomCertificateScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_custom_certificate(self, resource_group):
        self.kwargs.update({
            'name': self.create_random_name('webpubsub', 16),
            'sku': 'Premium_P1',
            'location': 'eastus',
            'certificate_name': 'testCertificate',
            'key_vault_base_uri': 'https://myvault.vault.azure.net/',
            'key_vault_secret_name': 'mySecret',
            'key_vault_secret_version': '8d35338681be4cf09b97e899cb7179b8'
        })

        # Create WebPubSub service
        self.cmd('webpubsub create -g {rg} -n {name} --sku {sku} -l {location}', checks=[
            self.check('name', '{name}'),
            self.check('location', '{location}'),
            self.check('sku.name', '{sku}'),
            self.check('provisioningState', 'Succeeded')
        ])

        # Create custom certificate
        self.cmd('webpubsub custom-certificate create -g {rg} -n {name} --certificate-name {certificate_name} '
                 '--key-vault-base-uri {key_vault_base_uri} '
                 '--key-vault-secret-name {key_vault_secret_name} '
                 '--key-vault-secret-version {key_vault_secret_version}', checks=[
            self.check('name', '{certificate_name}'),
            self.check('keyVaultBaseUri', '{key_vault_base_uri}'),
            self.check('keyVaultSecretName', '{key_vault_secret_name}'),
            self.check('keyVaultSecretVersion', '{key_vault_secret_version}')
        ])

        # List custom certificates
        self.cmd('webpubsub custom-certificate list -g {rg} -n {name}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{certificate_name}')
        ])

        # Show custom certificate
        self.cmd('webpubsub custom-certificate show -g {rg} -n {name} --certificate-name {certificate_name}', checks=[
            self.check('name', '{certificate_name}'),
            self.check('keyVaultBaseUri', '{key_vault_base_uri}'),
            self.check('keyVaultSecretName', '{key_vault_secret_name}'),
            self.check('keyVaultSecretVersion', '{key_vault_secret_version}')
        ])

        # Delete custom certificate
        self.cmd('webpubsub custom-certificate delete -g {rg} -n {name} --certificate-name {certificate_name}')

        # Verify deletion
        self.cmd('webpubsub custom-certificate list -g {rg} -n {name}', checks=[
            self.check('length(@)', 0)
        ])
