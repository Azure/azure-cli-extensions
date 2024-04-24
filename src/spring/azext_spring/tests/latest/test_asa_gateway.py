# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import (ScenarioTest, record_only)


# pylint: disable=line-too-long
# pylint: disable=too-many-lines


@record_only()
class GatewayTest(ScenarioTest):

    def test_gateway(self):
        py_path = os.path.abspath(os.path.dirname(__file__))
        routes_file = os.path.join(py_path, 'files/gateway_routes.json').replace("\\", "/")
        routes_file_v2 = os.path.join(py_path, 'files/gateway_routes_v2.json').replace("\\", "/")
        addon_configs_file = os.path.join(py_path, 'files/gateway_addon_configs.json').replace("\\", "/")

        self.kwargs.update({
            'serviceName': 'tx-enterprise',
            'rg': 'tx',
            'routeName': 'cli-route',
            'routeFile': routes_file,
            'routesFileV2': routes_file_v2,
            'addonConfigsFile': addon_configs_file,
            'cert': 'cli-unittest',
            'domain': 'gateway-cli.azdmss-test.net',
            'thumbprint': '6695512ed53e0c46817348b78411876a9a9c3396'
        })

        self.cmd('spring gateway update -g {rg} -s {serviceName} '
                 '--assign-endpoint true --https-only true --cpu 1 --memory 2Gi --instance-count 3 '
                 '--api-title "Pet clinic" --api-description "Demo for pet clinic" --api-doc-location "doc" --api-version v1 '
                 '--server-url https://tx-enterprise-gateway-fd0c7.svc.asc-test.net '
                 '--certificate-names abc --enable-cert-verify true '
                 '--apm-types NewRelic ElasticAPM --properties a=b c=d --secrets e=f g=h '
                 '--allowed-origins "*" --allowed-origin-patterns "example*" --allowed-methods "GET,PUT,DELETE" --allowed-headers "X-TEST,X-STAGING" --max-age 10 --allow-credentials true --exposed-headers "Access-Control-Request-Method,Access-Control-Request-Headers" '
                 '--client-id * --client-secret * --issuer-uri https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0 --scope "openid,profile,email" '
                 '--addon-configs-file {addonConfigsFile}',
                 checks=[
                     self.check('properties.public', True),
                     self.check('properties.httpsOnly', True),
                     self.check('properties.resourceRequests.cpu', "1"),
                     self.check('properties.resourceRequests.memory', "2Gi"),
                     self.check('sku.capacity', 3),
                     self.check('properties.operatorProperties.resourceRequests.cpu', "1"),
                     self.check('properties.operatorProperties.resourceRequests.memory', "2Gi"),
                     self.check('properties.operatorProperties.resourceRequests.instanceCount', 1),
                     self.check('properties.apiMetadataProperties.title', "Pet clinic"),
                     self.check('properties.apiMetadataProperties.description', "Demo for pet clinic"),
                     self.check('properties.apiMetadataProperties.documentation', "doc"),
                     self.check('properties.apiMetadataProperties.serverUrl',
                                "https://tx-enterprise-gateway-fd0c7.svc.asc-test.net"),
                     self.check('properties.apiMetadataProperties.version', "v1"),
                     self.check('properties.corsProperties.allowCredentials', True),
                     self.check('properties.corsProperties.allowedHeaders', ["X-TEST", "X-STAGING"]),
                     self.check('properties.corsProperties.allowedOrigins', ["*"]),
                     self.check('properties.corsProperties.allowedOriginPatterns', ["example*"]),
                     self.check('properties.corsProperties.allowedMethods', ["GET", "PUT", "DELETE"]),
                     self.check('properties.corsProperties.exposedHeaders',
                                ["Access-Control-Request-Method", "Access-Control-Request-Headers"]),
                     self.check('properties.ssoProperties.clientId', "*"),
                     self.check('properties.ssoProperties.clientSecret', "*"),
                     self.check('properties.ssoProperties.issuerUri',
                                "https://login.microsoftonline.com/72f988bf-86f1-41af-91ab-2d7cd011db47/v2.0"),
                     self.check('properties.ssoProperties.scope', ["openid", "profile", "email"]),
                     self.check('properties.clientAuth.certificates', [
                         "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/certificates/abc"]),
                     self.check('properties.clientAuth.certificateVerification', "Enabled"),
                     self.check('properties.apmTypes', ["NewRelic", "ElasticAPM"]),
                     self.check('properties.environmentVariables.properties', {'a': 'b', 'c': 'd'}),
                     self.check('properties.environmentVariables.secrets', None),
                     self.check('properties.addonConfigs', {'javaOpts': '-Djava.awt.headless=true',
                                                            'sso': {'rolesAttributeName': 'role',
                                                                    'inactiveSessionExpirationInMinutes': 1},
                                                            'envs': [{'name': 'xxx', 'value': 'yyy'},
                                                                     {'name': 'xxx1', 'value': 'yyy'}]}),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring gateway update -g {rg} -s {serviceName} '
                 '--apm-types '' --apms test-ai',
                 checks=[
                     self.check('properties.apms', [{
                         'resourceId': '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/apms/test-ai'}]),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring gateway show -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.public', True),
                     self.check('properties.httpsOnly', True),
                     self.check('sku.capacity', 3),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring gateway route-config create -g {rg} -s {serviceName} -n {routeName} '
                 '--app-name customers-service --routes-file {routeFile}',
                 checks=[
                     self.check('properties.appResourceId',
                                '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/apps/customers-service'),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring gateway route-config update -g {rg} -s {serviceName} -n {routeName} '
                 '--app-name vets-service --routes-file {routesFileV2}',
                 checks=[
                     self.check('properties.appResourceId',
                                '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/apps/vets-service'),
                     self.check('properties.provisioningState', "Succeeded"),
                     self.check('properties.ssoEnabled', True)
                 ])

        self.cmd('spring gateway route-config update -g {rg} -s {serviceName} -n {routeName} '
                 '--app-name vets-service --routes-file {routesFileV2}',
                 checks=[
                     self.check('properties.appResourceId',
                                '/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/tx/providers/Microsoft.AppPlatform/Spring/tx-enterprise/apps/vets-service'),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        result = self.cmd('spring gateway route-config list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd('spring gateway route-config remove --name {routeName} -g {rg} -s {serviceName}')
        self.cmd('spring gateway route-config show --name {routeName} -g {rg} -s {serviceName}', expect_failure=True)

        self.cmd('spring gateway clear -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.public', False),
                     self.check('properties.httpsOnly', False),
                     self.check('sku.capacity', 2),
                     self.check('properties.ssoProperties', None),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring gateway delete -g {rg} -s {serviceName} --yes')

        self.cmd('spring gateway create -g {rg} -s {serviceName}',
                 checks=[
                     self.check('properties.public', False),
                     self.check('properties.provisioningState', "Succeeded")
                 ])

        self.cmd('spring certificate show --name {cert} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('name', '{cert}')
                 ])

        self.cmd('spring gateway custom-domain bind --domain-name {domain} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('name', '{domain}')
                 ])

        self.cmd('spring gateway custom-domain show --domain-name {domain} -g {rg} -s {serviceName}',
                 checks=[
                     self.check('name', '{domain}')
                 ])

        result = self.cmd('spring gateway custom-domain list -g {rg} -s {serviceName}').get_output_in_json()
        self.assertTrue(len(result) > 0)

        self.cmd(
            'spring gateway custom-domain update --domain-name {domain} --certificate {cert} -g {rg} -s {serviceName}',
            checks=[
                self.check('name', '{domain}'),
                self.check('properties.thumbprint', '{thumbprint}')
            ])

        self.cmd('spring gateway custom-domain unbind --domain-name {domain} -g {rg} -s {serviceName}')
        self.cmd('spring gateway custom-domain show --domain-name {domain} -g {rg} -s {serviceName}',
                 expect_failure=True)
