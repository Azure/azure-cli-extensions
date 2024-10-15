# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)
from .recording_processors import KeyReplacer

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


class WebpubsubCustomDomainScenarioTest(ScenarioTest):

    def __init__(self, method_name):
        super(WebpubsubCustomDomainScenarioTest, self).__init__(
            method_name, recording_processors=[KeyReplacer()]
        )

    @ResourceGroupPreparer(random_name_length=20)
    def test_webpubsub_custom_domain(self, resource_group):
        webpubsub_name = "webpubsubcliteststatic"
        sku = 'Premium_P1'
        unit_count = 1
        location = 'eastus'

        self.kwargs.update({
            'webpubsub_name': webpubsub_name,
            'sku': sku,
            'location': location,
            'unit_count': unit_count,
            'kv_base_uri': 'https://azureclitestkv.vault.azure.net/',
            'kv_s_name': 'azureclitestkv3',
            'identity': '/subscriptions/9caf2a1e-9c49-49b6-89a2-56bdec7e3f97/resourcegroups/azureclitest/providers/Microsoft.ManagedIdentity/userAssignedIdentities/azureclitestmsi',
            'custom_cert_name': 'test-cert',
            'custom_domain_resource_name': 'test-domain',
            'custom_domain_name': 'wpsclitest.manual-test.dev.signalr.azure.com',
        })

        # Create WebPubSub service
        webpubsub = self.cmd('webpubsub create -g {rg} -n {webpubsub_name} --sku {sku} -l {location}', checks=[
            self.check('name', '{webpubsub_name}'),
            self.check('location', '{location}'),
            self.check('provisioningState', 'Succeeded'),
            self.check('sku.name', '{sku}')
        ]).get_output_in_json()

        # Assign identity
        self.cmd('webpubsub identity assign -g {rg} -n {webpubsub_name} --identity {identity}', checks=[
            self.check('identity.type', 'UserAssigned'),
            self.check('identity.principalId', None),
            self.check('identity.tenantId', None),
        ])

        # Create custom certificate
        self.cmd('webpubsub custom-certificate create -g {rg} --webpubsub-name {webpubsub_name} --certificate-name {custom_cert_name} --key-vault-base-uri {kv_base_uri} --key-vault-secret-name {kv_s_name}', checks=[
            self.check('provisioningState', 'Succeeded')
        ])

        cert = self.cmd(
            'webpubsub custom-certificate show -g {rg} --webpubsub-name {webpubsub_name} --certificate-name {custom_cert_name}', checks=[
                self.check('name', '{custom_cert_name}'),
                self.check('keyVaultBaseUri', '{kv_base_uri}'),
                self.check('keyVaultSecretName', '{kv_s_name}'),
                self.check('provisioningState', 'Succeeded')
            ]).get_output_in_json()

        self.kwargs.update({'cert_resource_id': cert['id']})

        # List custom certificates
        self.cmd('webpubsub custom-certificate list -g {rg} --webpubsub-name {webpubsub_name}', checks=[
            self.check('length(@)', 1),
            self.check('[0].name', '{custom_cert_name}')
        ])

        # Show custom certificate
        self.cmd('webpubsub custom-certificate show -g {rg} --webpubsub-name {webpubsub_name} --certificate-name {custom_cert_name}', checks=[
            self.check('name', '{custom_cert_name}'),
            self.check('keyVaultBaseUri', '{kv_base_uri}'),
            self.check('keyVaultSecretName', '{kv_s_name}'),
        ])

        # TODO: Enable this test when have valid cert and domain_name
        # # Create custom domain
        # self.cmd('webpubsub custom-domain create -g {rg} --webpubsub-name {webpubsub_name} --name {custom_domain_resource_name} --domain-name {custom_domain_name} --certificate-resource-id {cert_resource_id}', checks=[
        #     self.check('provisioningState', 'Succeeded'),
        # ])

        # # List custom domains
        # self.cmd('webpubsub custom-domain list -g {rg} --webpubsub-name {webpubsub_name}', checks=[
        #     self.check('length(@)', 1),
        #     self.check('[0].name', '{custom_domain_resource_name}'),
        #     self.check('[0].domainName', '{custom_domain_name}'),
        #     self.check('[0].provisioningState', 'Succeeded')
        # ])

        # # Show custom domain
        # self.cmd('webpubsub custom-domain show -g {rg} --webpubsub-name {webpubsub_name} --name {custom_domain_resource_name}', checks=[
        #     self.check('name', '{custom_domain_resource_name}'),
        #     self.check('domainName', '{custom_domain_name}'),
        #     self.check('provisioningState', 'Succeeded')
        # ])

        # # Delete custom domain
        # self.cmd('webpubsub custom-domain delete -g {rg} --webpubsub-name {webpubsub_name} --name {custom_domain_resource_name}', checks=[
        #     self.check('provisioningState', 'Succeeded')
        # ])

        # # Verify deletion
        # self.cmd('webpubsub custom-domain list -g {rg} --webpubsub-name {webpubsub_name}', checks=[
        #     self.check('length(@)', 0)
        # ])

        # Delete custom certificate
        self.cmd(
            'webpubsub custom-certificate delete -g {rg} --webpubsub-name {webpubsub_name} --certificate-name {custom_cert_name}')

        # Verify deletion
        self.cmd('webpubsub custom-certificate list -g {rg} --webpubsub-name {webpubsub_name}', checks=[
            self.check('length(@)', 0)
        ])

        self.cmd('webpubsub delete -g {rg} -n {webpubsub_name}')
