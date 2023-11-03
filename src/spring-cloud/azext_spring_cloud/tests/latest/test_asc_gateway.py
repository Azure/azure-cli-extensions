# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import json
from azure.cli.testsdk import (ScenarioTest, record_only)

# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class GatewayTest(ScenarioTest):

    def test_gateway(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        routes_file = os.path.join(py_path, 'files/gateway_routes.json').replace("\\","/")
        
        self.kwargs.update({
            'serviceName': 'tx-enterprise',
            'rg': 'tx',
            'routeName': 'cli-route',
            'routeFile': routes_file,
            'cert': 'cli-unittest',
            'domain': 'gateway-cli.asc-test.net',
            'thumbprint': 'ef16ce1a35ecd6b7a9d4e546a5b1d480b38f3e5d'
        })

        self.cmd('spring-cloud gateway update -g {rg} -s {serviceName} '
                 '--assign-endpoint true --https-only true --cpu 1 --memory 2Gi --instance-count 3 '
                 '--api-title "Pet clinic" --api-description "Demo for pet clinic" --api-doc-location "doc" --api-version v1 '
                 '--server-url https://tx-enterprise-gateway-fd0c7.svc.asc-test.net '
                 '--allowed-origins "*" --allowed-methods "GET,PUT,DELETE" --allowed-headers "X-TEST,X-STAGING" --max-age 10 --allow-credentials true --exposed-headers "Access-Control-Request-Method,Access-Control-Request-Headers" '
                 '--client-id * --client-secret * --issuer-uri https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0 --scope "openid,profile,email"', checks=[
            self.check('properties.public', True),
            self.check('properties.httpsOnly', True),
            self.check('properties.resourceRequests.cpu', "1"),
            self.check('properties.resourceRequests.memory', "2Gi"),
            self.check('sku.capacity', 3),
            self.check('properties.operatorProperties.resourceRequests.cpu', "1"),
            self.check('properties.operatorProperties.resourceRequests.memory', "2Gi"),
            self.check('properties.operatorProperties.resourceRequests.instanceCount', 2),
            self.check('properties.apiMetadataProperties.title', "Pet clinic"),
            self.check('properties.apiMetadataProperties.description', "Demo for pet clinic"),
            self.check('properties.apiMetadataProperties.documentation', "doc"),
            self.check('properties.apiMetadataProperties.serverUrl', "https://tx-enterprise-gateway-fd0c7.svc.asc-test.net"),
            self.check('properties.apiMetadataProperties.version', "v1"),
            self.check('properties.corsProperties.allowCredentials', True),
            self.check('properties.corsProperties.allowedHeaders', ["X-TEST", "X-STAGING"]),
            self.check('properties.corsProperties.allowedOrigins', ["*"]),
            self.check('properties.corsProperties.allowedMethods', ["GET", "PUT", "DELETE"]),
            self.check('properties.corsProperties.exposedHeaders', ["Access-Control-Request-Method", "Access-Control-Request-Headers"]),
            self.check('properties.ssoProperties.clientId', "*"),
            self.check('properties.ssoProperties.clientSecret', "*"),
            self.check('properties.ssoProperties.issuerUri', "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0"),
            self.check('properties.ssoProperties.scope', ["openid", "profile", "email"]),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud gateway show -g {rg} -s {serviceName}', checks=[
            self.check('properties.public', True),
            self.check('properties.httpsOnly', True),
            self.check('sku.capacity', 3),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud gateway route-config create -g {rg} -s {serviceName} -n {routeName} '
                 '--app-name customers-service --routes-file {routeFile}', checks=[
            self.check('properties.appResourceId', '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/apps/customers-service'),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud gateway route-config update -g {rg} -s {serviceName} -n {routeName} '
                 '--app-name vets-service', checks=[
            self.check('properties.appResourceId', '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/apps/vets-service'),
            self.check('properties.provisioningState', "Succeeded")
        ])

        result = self.cmd('spring-cloud gateway route-config list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring-cloud gateway route-config remove --name {routeName} -g {rg} -s {serviceName}')
        self.cmd('spring-cloud gateway route-config show --name {routeName} -g {rg} -s {serviceName}', expect_failure=True)

        self.cmd('spring-cloud gateway clear -g {rg} -s {serviceName}', checks=[
            self.check('properties.public', False),
            self.check('properties.httpsOnly', False),
            self.check('sku.capacity', 2),
            self.check('properties.ssoProperties', None),
            self.check('properties.provisioningState', "Succeeded")
        ])

        self.cmd('spring-cloud certificate show --name {cert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{cert}')
        ])

        self.cmd('spring-cloud gateway custom-domain bind --domain-name {domain} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}')
        ])

        self.cmd('spring-cloud gateway custom-domain show --domain-name {domain} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}')
        ])

        result = self.cmd('spring-cloud gateway custom-domain list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring-cloud gateway custom-domain update --domain-name {domain} --certificate {cert} -g {rg} -s {serviceName}', checks=[
            self.check('name', '{domain}'),
            self.check('properties.thumbprint', '{thumbprint}')
        ])

        self.cmd('spring-cloud gateway custom-domain unbind --domain-name {domain} -g {rg} -s {serviceName}')
        self.cmd('spring-cloud gateway custom-domain show --domain-name {domain} -g {rg} -s {serviceName}', expect_failure=True)
