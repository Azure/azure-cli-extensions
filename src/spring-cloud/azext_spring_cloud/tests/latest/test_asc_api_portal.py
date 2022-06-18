# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os

from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class ApiPortalTest(ScenarioTest):

    def test_api_portal(self):
        
        self.kwargs.update({
            'serviceName': 'tx-enterprise',
            'rg': 'tx',
            'cert': 'cli-unittest',
            'domain': 'api-portal-cli.asc-test.net',
            'thumbprint': 'ef16ce1a35ecd6b7a9d4e546a5b1d480b38f3e5d'
        })

        self.cmd('spring-cloud api-portal update -g {rg} -s {serviceName} '
                 '--assign-endpoint true --https-only true --instance-count 1 '
                 '--client-id * --client-secret * --issuer-uri https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0 --scope "openid,profile,email"', checks=[
            self.check('properties.public', True),
            self.check('properties.httpsOnly', True),
            self.check('sku.capacity', 1),
            self.check('properties.ssoProperties.clientId', "*"),
            self.check('properties.ssoProperties.clientSecret', "*"),
            self.check('properties.ssoProperties.issuerUri', "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0"),
            self.check('properties.ssoProperties.scope', ["openid", "profile", "email"]),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud api-portal show -g {rg} -s {serviceName}', checks=[
            self.check('properties.public', True),
            self.check('properties.httpsOnly', True),
            self.check('sku.capacity', 1),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud api-portal clear -g {rg} -s {serviceName}', checks=[
            self.check('properties.public', False),
            self.check('properties.httpsOnly', False),
            self.check('sku.capacity', 1),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud certificate show --name {cert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{cert}')
        ])

        self.cmd('spring-cloud api-portal custom-domain bind --domain-name {domain} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}')
        ])

        self.cmd('spring-cloud api-portal custom-domain show --domain-name {domain} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}')
        ])

        result = self.cmd('spring-cloud api-portal custom-domain list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring-cloud api-portal custom-domain update --domain-name {domain} --certificate {cert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.thumbprint', '{thumbprint}')
        ])

        self.cmd('spring-cloud api-portal custom-domain unbind --domain-name {domain} -g {rg} -s {serviceName}')
        self.cmd('spring-cloud api-portal custom-domain show --domain-name {domain} -g {rg} -s {serviceName}', expect_failure=True)
